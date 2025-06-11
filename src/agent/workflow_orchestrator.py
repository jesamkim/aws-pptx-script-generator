"""AWS Strands Agent Workflow Orchestrator.

This module implements intelligent workflow orchestration using AWS Strands Agent SDK
for coordinating complex presentation processing workflows.
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from src.utils.logger import log_execution_time, performance_monitor


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Individual task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowTask:
    """Individual workflow task definition.
    
    Attributes:
        task_id: Unique task identifier
        name: Human-readable task name
        function: Function to execute
        dependencies: List of task IDs this task depends on
        parameters: Task parameters
        timeout: Task timeout in seconds
        retry_count: Number of retry attempts
        status: Current task status
        result: Task execution result
        error: Error message if task failed
        start_time: Task start timestamp
        end_time: Task completion timestamp
    """
    task_id: str
    name: str
    function: Callable
    dependencies: List[str]
    parameters: Dict[str, Any]
    timeout: int = 300
    retry_count: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class WorkflowDefinition:
    """Complete workflow definition.
    
    Attributes:
        workflow_id: Unique workflow identifier
        name: Human-readable workflow name
        description: Workflow description
        tasks: List of workflow tasks
        max_parallel_tasks: Maximum parallel task execution
        total_timeout: Total workflow timeout
        on_success: Callback for successful completion
        on_failure: Callback for failure
    """
    workflow_id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    max_parallel_tasks: int = 5
    total_timeout: int = 1800  # 30 minutes
    on_success: Optional[Callable] = None
    on_failure: Optional[Callable] = None


@dataclass
class WorkflowExecution:
    """Workflow execution state.
    
    Attributes:
        workflow_id: Workflow identifier
        status: Current workflow status
        start_time: Execution start time
        end_time: Execution end time
        completed_tasks: Number of completed tasks
        total_tasks: Total number of tasks
        current_tasks: Currently executing tasks
        results: Task results dictionary
        task_results: Detailed task results
        errors: Error messages
        error: Error message if failed
        progress_callback: Progress update callback
    """
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    completed_tasks: int = 0
    total_tasks: int = 0
    current_tasks: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    task_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    error: Optional[str] = None
    progress_callback: Optional[Callable] = None
    
    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = []
        if self.results is None:
            self.results = {}
        if self.errors is None:
            self.errors = []


class WorkflowOrchestrator:
    """Intelligent workflow orchestrator using agent-based coordination.
    
    This class provides sophisticated workflow management with parallel execution,
    dependency resolution, error handling, and progress tracking.
    """
    
    def __init__(self, max_workers: int = 5):
        """Initialize workflow orchestrator.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        
        logger.info(f"Initialized workflow orchestrator with {max_workers} workers")
    
    def register_workflow(self, workflow_def: WorkflowDefinition):
        """Register a workflow definition.
        
        Args:
            workflow_def: Workflow definition to register
        """
        try:
            # Validate workflow definition
            self._validate_workflow_definition(workflow_def)
            
            # Store workflow definition
            self.workflow_definitions[workflow_def.workflow_id] = workflow_def
            
            logger.info(f"Registered workflow: {workflow_def.name} ({workflow_def.workflow_id})")
            
        except Exception as e:
            logger.error(f"Failed to register workflow {workflow_def.workflow_id}: {str(e)}")
            raise
    
    def _validate_workflow_definition(self, workflow_def: WorkflowDefinition):
        """Validate workflow definition for consistency.
        
        Args:
            workflow_def: Workflow definition to validate
            
        Raises:
            ValueError: If workflow definition is invalid
        """
        # Check for duplicate task IDs
        task_ids = [task.task_id for task in workflow_def.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Duplicate task IDs found in workflow")
        
        # Check dependency references
        for task in workflow_def.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise ValueError(f"Task {task.task_id} depends on non-existent task {dep_id}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(workflow_def.tasks):
            raise ValueError("Circular dependencies detected in workflow")
        
        logger.debug(f"Validated workflow definition: {workflow_def.workflow_id}")
    
    def _has_circular_dependencies(self, tasks: List[WorkflowTask]) -> bool:
        """Check for circular dependencies in task list.
        
        Args:
            tasks: List of workflow tasks
            
        Returns:
            True if circular dependencies exist
        """
        # Build dependency graph
        graph = {task.task_id: task.dependencies for task in tasks}
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True
        
        return False
    
    @log_execution_time
    async def execute_workflow_async(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> WorkflowExecution:
        """Execute workflow asynchronously and return result.
        
        Args:
            workflow_id: ID of workflow to execute
            context: Execution context
            
        Returns:
            Workflow execution result
            
        Raises:
            ValueError: If workflow not found
        """
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow_def = self.workflow_definitions[workflow_id]
        execution_id = f"{workflow_id}_{int(time.time())}"
        
        # Create workflow execution
        execution = WorkflowExecution(
            workflow_id=execution_id,
            status=WorkflowStatus.RUNNING,
            total_tasks=len(workflow_def.tasks),
            start_time=time.time()
        )
        
        try:
            # Execute tasks with dependency resolution
            task_results = {}
            remaining_tasks = workflow_def.tasks.copy()
            
            while remaining_tasks:
                # Find tasks with satisfied dependencies
                ready_tasks = [
                    task for task in remaining_tasks
                    if all(dep in task_results for dep in task.dependencies)
                ]
                
                if not ready_tasks:
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute ready tasks in parallel
                futures = []
                for task in ready_tasks[:workflow_def.max_parallel_tasks]:
                    task.start_time = time.time()
                    task.status = TaskStatus.RUNNING
                    
                    # Create task context
                    task_context = {
                        **context,
                        "task_results": task_results,
                        "execution_id": execution_id
                    }
                    
                    # Submit task for execution
                    future = self.executor.submit(
                        self._execute_single_task,
                        task,
                        task_context
                    )
                    futures.append((task, future))
                
                # Wait for task completion
                for task, future in futures:
                    try:
                        result = future.result(timeout=task.timeout)
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                        task.end_time = time.time()
                        task_results[task.task_id] = result
                        
                    except Exception as e:
                        task.error = str(e)
                        task.status = TaskStatus.FAILED
                        task.end_time = time.time()
                        logger.error(f"Task {task.task_id} failed: {str(e)}")
                        
                        if task.retry_count > 0:
                            task.retry_count -= 1
                            task.status = TaskStatus.RETRYING
                            remaining_tasks.append(task)
                        else:
                            raise
                    
                    remaining_tasks.remove(task)
            
            # Update execution status
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = time.time()
            execution.task_results = task_results
            execution.results = task_results
            
            logger.info(f"Workflow completed successfully: {execution_id}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = time.time()
            execution.error = str(e)
            logger.error(f"Workflow execution failed: {execution_id}, error: {str(e)}")
            raise
        
        return execution
    
    @log_execution_time
    async def execute_workflow_async(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> WorkflowExecution:
        """Execute workflow asynchronously and return result.
        
        Args:
            workflow_id: ID of workflow to execute
            context: Execution context
            
        Returns:
            Workflow execution result
            
        Raises:
            ValueError: If workflow not found
        """
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow_def = self.workflow_definitions[workflow_id]
        execution_id = f"{workflow_id}_{int(time.time())}"
        
        # Create workflow execution
        execution = WorkflowExecution(
            workflow_id=execution_id,
            status=WorkflowStatus.RUNNING,
            total_tasks=len(workflow_def.tasks),
            start_time=time.time()
        )
        
        self.active_workflows[execution_id] = execution
        
        try:
            # Execute tasks with dependency resolution
            task_results = {}
            remaining_tasks = workflow_def.tasks.copy()
            
            while remaining_tasks:
                # Find tasks with satisfied dependencies
                ready_tasks = [
                    task for task in remaining_tasks
                    if all(dep in task_results for dep in task.dependencies)
                ]
                
                if not ready_tasks:
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute ready tasks in parallel
                futures = []
                for task in ready_tasks[:workflow_def.max_parallel_tasks]:
                    task.start_time = time.time()
                    task.status = TaskStatus.RUNNING
                    execution.current_tasks.append(task.task_id)
                    
                    # Create task context
                    task_context = {
                        **context,
                        "task_results": task_results,
                        "execution_id": execution_id
                    }
                    
                    # Submit task for execution
                    future = self.executor.submit(
                        self._execute_single_task,
                        task,
                        task_context
                    )
                    futures.append((task, future))
                
                # Wait for task completion
                for task, future in futures:
                    try:
                        result = future.result(timeout=task.timeout)
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                        task.end_time = time.time()
                        task_results[task.task_id] = result
                        execution.completed_tasks += 1
                        execution.current_tasks.remove(task.task_id)
                        
                        # Update progress
                        if execution.progress_callback:
                            execution.progress_callback(execution)
                        
                    except Exception as e:
                        task.error = str(e)
                        task.status = TaskStatus.FAILED
                        task.end_time = time.time()
                        execution.errors.append(str(e))
                        execution.current_tasks.remove(task.task_id)
                        logger.error(f"Task {task.task_id} failed: {str(e)}")
                        
                        if task.retry_count > 0:
                            task.retry_count -= 1
                            task.status = TaskStatus.RETRYING
                            remaining_tasks.append(task)
                        else:
                            raise
                    
                    remaining_tasks.remove(task)
            
            # Update execution status
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = time.time()
            execution.task_results = task_results
            execution.results = task_results
            
            logger.info(f"Workflow completed successfully: {execution_id}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = time.time()
            execution.error = str(e)
            logger.error(f"Workflow execution failed: {execution_id}, error: {str(e)}")
            raise
        finally:
            if execution_id in self.active_workflows:
                del self.active_workflows[execution_id]
        
        return execution
    
    def _execute_single_task(self, task: WorkflowTask, context: Dict[str, Any]) -> Any:
        """Execute a single task with error handling."""
        try:
            # Execute task function
            result = task.function(context)
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.task_id}, error: {str(e)}")
            raise
    
    @log_execution_time
    def execute_workflow(
        self,
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Execute a registered workflow.
        
        Args:
            workflow_id: ID of workflow to execute
            parameters: Global workflow parameters
            progress_callback: Progress update callback
            
        Returns:
            Execution ID for tracking
            
        Raises:
            ValueError: If workflow not found or invalid
        """
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_def = self.workflow_definitions[workflow_id]
        execution_id = f"{workflow_id}_{int(time.time())}"
        
        # Create workflow execution
        execution = WorkflowExecution(
            workflow_id=execution_id,
            status=WorkflowStatus.PENDING,
            total_tasks=len(workflow_def.tasks),
            progress_callback=progress_callback
        )
        
        self.active_workflows[execution_id] = execution
        
        # Start workflow execution in background
        self.executor.submit(self._execute_workflow_async, workflow_def, execution, parameters or {})
        
        logger.info(f"Started workflow execution: {execution_id}")
        return execution_id
    
    def _execute_workflow_async(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        global_params: Dict[str, Any]
    ):
        """Execute workflow asynchronously.
        
        Args:
            workflow_def: Workflow definition
            execution: Workflow execution state
            global_params: Global parameters
        """
        performance_monitor.start_operation(f"workflow_{execution.workflow_id}")
        
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = time.time()
            
            # Create task execution plan
            execution_plan = self._create_execution_plan(workflow_def.tasks)
            
            # Execute tasks in planned order
            for task_batch in execution_plan:
                if execution.status != WorkflowStatus.RUNNING:
                    break  # Workflow was cancelled
                
                # Execute batch of tasks in parallel
                self._execute_task_batch(task_batch, execution, global_params)
                
                # Update progress
                if execution.progress_callback:
                    progress = execution.completed_tasks / execution.total_tasks
                    execution.progress_callback(progress, execution.current_tasks)
            
            # Check final status
            if execution.status == WorkflowStatus.RUNNING:
                if execution.completed_tasks == execution.total_tasks:
                    execution.status = WorkflowStatus.COMPLETED
                    if workflow_def.on_success:
                        workflow_def.on_success(execution.results)
                else:
                    execution.status = WorkflowStatus.FAILED
                    if workflow_def.on_failure:
                        workflow_def.on_failure(execution.errors)
            
            execution.end_time = time.time()
            performance_monitor.end_operation(f"workflow_{execution.workflow_id}", 
                                            execution.status == WorkflowStatus.COMPLETED)
            
            logger.info(f"Workflow {execution.workflow_id} completed with status: {execution.status}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = time.time()
            execution.errors.append(f"Workflow execution failed: {str(e)}")
            
            performance_monitor.end_operation(f"workflow_{execution.workflow_id}", False)
            logger.error(f"Workflow {execution.workflow_id} failed: {str(e)}")
            
            if workflow_def.on_failure:
                workflow_def.on_failure(execution.errors)
    
    def _create_execution_plan(self, tasks: List[WorkflowTask]) -> List[List[WorkflowTask]]:
        """Create task execution plan respecting dependencies.
        
        Args:
            tasks: List of workflow tasks
            
        Returns:
            List of task batches for parallel execution
        """
        # Topological sort to determine execution order
        task_map = {task.task_id: task for task in tasks}
        in_degree = {task.task_id: len(task.dependencies) for task in tasks}
        execution_plan = []
        
        while task_map:
            # Find tasks with no dependencies
            ready_tasks = [task for task_id, task in task_map.items() 
                          if in_degree[task_id] == 0]
            
            if not ready_tasks:
                # This shouldn't happen if validation passed
                raise ValueError("Circular dependency detected during execution planning")
            
            execution_plan.append(ready_tasks)
            
            # Remove ready tasks and update dependencies
            for task in ready_tasks:
                del task_map[task.task_id]
                del in_degree[task.task_id]
                
                # Update dependent tasks
                for remaining_task in task_map.values():
                    if task.task_id in remaining_task.dependencies:
                        in_degree[remaining_task.task_id] -= 1
        
        logger.debug(f"Created execution plan with {len(execution_plan)} batches")
        return execution_plan
    
    def _execute_task_batch(
        self,
        task_batch: List[WorkflowTask],
        execution: WorkflowExecution,
        global_params: Dict[str, Any]
    ):
        """Execute a batch of tasks in parallel.
        
        Args:
            task_batch: List of tasks to execute
            execution: Workflow execution state
            global_params: Global parameters
        """
        # Submit tasks to executor
        future_to_task = {}
        
        for task in task_batch:
            if execution.status != WorkflowStatus.RUNNING:
                break
            
            task.status = TaskStatus.RUNNING
            task.start_time = time.time()
            execution.current_tasks.append(task.task_id)
            
            # Prepare task parameters
            task_params = {**global_params, **task.parameters}
            
            # Add results from completed dependencies
            for dep_id in task.dependencies:
                if dep_id in execution.results:
                    task_params[f"{dep_id}_result"] = execution.results[dep_id]
            
            # Submit task
            future = self.executor.submit(self._execute_single_task, task, task_params)
            future_to_task[future] = task
        
        # Wait for tasks to complete
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            
            try:
                result = future.result(timeout=task.timeout)
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.end_time = time.time()
                
                execution.results[task.task_id] = result
                execution.completed_tasks += 1
                
                logger.info(f"Task {task.task_id} completed successfully")
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.end_time = time.time()
                
                execution.errors.append(f"Task {task.task_id} failed: {str(e)}")
                logger.error(f"Task {task.task_id} failed: {str(e)}")
                
                # Check if this is a critical failure
                if task.retry_count <= 0:
                    execution.status = WorkflowStatus.FAILED
                    break
            
            finally:
                if task.task_id in execution.current_tasks:
                    execution.current_tasks.remove(task.task_id)
    
    def _execute_single_task(self, task: WorkflowTask, parameters: Dict[str, Any]) -> Any:
        """Execute a single task with retry logic.
        
        Args:
            task: Task to execute
            parameters: Task parameters
            
        Returns:
            Task execution result
            
        Raises:
            Exception: If task fails after all retries
        """
        last_error = None
        
        for attempt in range(task.retry_count + 1):
            try:
                logger.debug(f"Executing task {task.task_id}, attempt {attempt + 1}")
                result = task.function(parameters)
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Task {task.task_id} attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < task.retry_count:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        raise last_error
    
    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow execution status.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Status dictionary or None if not found
        """
        if execution_id not in self.active_workflows:
            return None
        
        execution = self.active_workflows[execution_id]
        
        status = {
            'workflow_id': execution.workflow_id,
            'status': execution.status.value,
            'progress': execution.completed_tasks / max(1, execution.total_tasks),
            'completed_tasks': execution.completed_tasks,
            'total_tasks': execution.total_tasks,
            'current_tasks': execution.current_tasks.copy(),
            'errors': execution.errors.copy(),
            'start_time': execution.start_time,
            'end_time': execution.end_time
        }
        
        if execution.start_time and execution.end_time:
            status['duration'] = execution.end_time - execution.start_time
        elif execution.start_time:
            status['duration'] = time.time() - execution.start_time
        
        return status
    
    def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            True if cancelled successfully
        """
        if execution_id not in self.active_workflows:
            return False
        
        execution = self.active_workflows[execution_id]
        
        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = time.time()
            logger.info(f"Cancelled workflow: {execution_id}")
            return True
        
        return False
    
    def cleanup_completed_workflows(self, max_age_hours: int = 24):
        """Clean up old completed workflow executions.
        
        Args:
            max_age_hours: Maximum age in hours for keeping completed workflows
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        
        for execution_id, execution in self.active_workflows.items():
            if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                if execution.end_time and (current_time - execution.end_time) > max_age_seconds:
                    to_remove.append(execution_id)
        
        for execution_id in to_remove:
            del self.active_workflows[execution_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old workflow executions")
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics.
        
        Returns:
            Dictionary with orchestrator statistics
        """
        stats = {
            'active_workflows': len(self.active_workflows),
            'registered_workflows': len(self.workflow_definitions),
            'max_workers': self.max_workers,
            'status_distribution': {}
        }
        
        # Count workflows by status
        for execution in self.active_workflows.values():
            status = execution.status.value
            stats['status_distribution'][status] = stats['status_distribution'].get(status, 0) + 1
        
        return stats
    
    def shutdown(self):
        """Shutdown the orchestrator and cleanup resources."""
        try:
            # Cancel all running workflows
            for execution_id, execution in self.active_workflows.items():
                if execution.status == WorkflowStatus.RUNNING:
                    self.cancel_workflow(execution_id)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("Workflow orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during orchestrator shutdown: {str(e)}")


# Global orchestrator instance
workflow_orchestrator = WorkflowOrchestrator()
