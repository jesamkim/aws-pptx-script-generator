"""Enhanced AWS Strands Agent Workflow Orchestrator.

This module implements an improved workflow orchestrator with better performance
monitoring, error handling, and optimization capabilities.
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from src.utils.logger import log_execution_time, performance_monitor


class WorkflowStatus(Enum):
    """Enhanced workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    OPTIMIZING = "optimizing"


class TaskStatus(Enum):
    """Enhanced individual task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    OPTIMIZED = "optimized"


@dataclass
class EnhancedWorkflowTask:
    """Enhanced workflow task with optimization features.
    
    Attributes:
        task_id: Unique task identifier
        name: Human-readable task name
        function: Function to execute
        dependencies: List of task IDs this task depends on
        parameters: Task parameters
        timeout: Task timeout in seconds
        retry_count: Number of retry attempts
        priority: Task priority (1-10, higher is more important)
        resource_requirements: Resource requirements
        optimization_hints: Hints for task optimization
        status: Current task status
        result: Task execution result
        error: Error message if task failed
        start_time: Task start timestamp
        end_time: Task completion timestamp
        execution_metrics: Task execution metrics
    """
    task_id: str
    name: str
    function: Callable
    dependencies: List[str]
    parameters: Dict[str, Any]
    timeout: int = 300
    retry_count: int = 3
    priority: int = 5
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    optimization_hints: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    execution_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedWorkflowDefinition:
    """Enhanced workflow definition with optimization features.
    
    Attributes:
        workflow_id: Unique workflow identifier
        name: Human-readable workflow name
        description: Workflow description
        tasks: List of workflow tasks
        max_parallel_tasks: Maximum parallel task execution
        total_timeout: Total workflow timeout
        optimization_strategy: Workflow optimization strategy
        performance_targets: Performance targets
        on_success: Callback for successful completion
        on_failure: Callback for failure
        on_optimization: Callback for optimization events
    """
    workflow_id: str
    name: str
    description: str
    tasks: List[EnhancedWorkflowTask]
    max_parallel_tasks: int = 5
    total_timeout: int = 1800  # 30 minutes
    optimization_strategy: str = "balanced"  # balanced, speed, quality, cost
    performance_targets: Dict[str, Any] = field(default_factory=dict)
    on_success: Optional[Callable] = None
    on_failure: Optional[Callable] = None
    on_optimization: Optional[Callable] = None


@dataclass
class EnhancedWorkflowExecution:
    """Enhanced workflow execution state with metrics.
    
    Attributes:
        workflow_id: Workflow identifier
        execution_id: Unique execution identifier
        status: Current workflow status
        start_time: Execution start time
        end_time: Execution end time
        task_results: Results from individual tasks
        performance_metrics: Execution performance metrics
        optimization_applied: Applied optimizations
        resource_usage: Resource usage statistics
        error_details: Detailed error information
    """
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    start_time: float
    end_time: Optional[float] = None
    task_results: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    optimization_applied: List[str] = field(default_factory=list)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[Dict[str, Any]] = None


class EnhancedWorkflowOrchestrator:
    """Enhanced workflow orchestrator with optimization capabilities."""
    
    def __init__(self, max_workers: int = 8, enable_optimization: bool = True):
        """Initialize enhanced workflow orchestrator.
        
        Args:
            max_workers: Maximum number of worker threads
            enable_optimization: Whether to enable workflow optimization
        """
        self.max_workers = max_workers
        self.enable_optimization = enable_optimization
        
        # Workflow registry
        self.workflows: Dict[str, EnhancedWorkflowDefinition] = {}
        self.executions: Dict[str, EnhancedWorkflowExecution] = {}
        
        # Performance tracking
        self.performance_history = []
        self.optimization_stats = {
            "optimizations_applied": 0,
            "performance_improvements": [],
            "resource_savings": []
        }
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        logger.info(f"Initialized enhanced workflow orchestrator with {max_workers} workers, optimization: {enable_optimization}")
    
    def register_workflow(self, workflow: EnhancedWorkflowDefinition):
        """Register an enhanced workflow definition.
        
        Args:
            workflow: Workflow definition to register
        """
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Registered enhanced workflow: {workflow.workflow_id}")
    
    @log_execution_time
    async def execute_workflow_async(self, 
                                   workflow_id: str, 
                                   context: Dict[str, Any],
                                   execution_id: Optional[str] = None) -> EnhancedWorkflowExecution:
        """Execute workflow asynchronously with optimizations.
        
        Args:
            workflow_id: ID of workflow to execute
            context: Execution context
            execution_id: Optional execution ID
            
        Returns:
            Enhanced workflow execution result
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution_id = execution_id or f"{workflow_id}_{int(time.time())}"
        
        # Create execution state
        execution = EnhancedWorkflowExecution(
            workflow_id=workflow_id,
            execution_id=execution_id,
            status=WorkflowStatus.PENDING,
            start_time=time.time()
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Apply pre-execution optimizations
            if self.enable_optimization:
                await self._optimize_workflow_execution(workflow, execution, context)
            
            execution.status = WorkflowStatus.RUNNING
            logger.info(f"Starting enhanced workflow execution: {execution_id}")
            
            # Execute tasks with dependency resolution
            task_results = await self._execute_tasks_optimized(workflow, execution, context)
            
            # Update execution results
            execution.task_results = task_results
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = time.time()
            
            # Calculate performance metrics
            execution.performance_metrics = self._calculate_performance_metrics(execution)
            
            # Apply post-execution optimizations
            if self.enable_optimization:
                await self._apply_post_execution_optimizations(execution)
            
            # Store performance history
            self.performance_history.append({
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "execution_time": execution.end_time - execution.start_time,
                "success": True,
                "performance_metrics": execution.performance_metrics
            })
            
            logger.info(f"Enhanced workflow execution completed: {execution_id}")
            
            # Call success callback
            if workflow.on_success:
                await self._safe_callback(workflow.on_success, execution)
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = time.time()
            execution.error_details = {
                "error": str(e),
                "type": type(e).__name__,
                "timestamp": time.time()
            }
            
            logger.error(f"Enhanced workflow execution failed: {execution_id}, error: {str(e)}")
            
            # Store failure in history
            self.performance_history.append({
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "execution_time": execution.end_time - execution.start_time,
                "success": False,
                "error": str(e)
            })
            
            # Call failure callback
            if workflow.on_failure:
                await self._safe_callback(workflow.on_failure, execution)
        
        return execution
    
    async def _execute_tasks_optimized(self, 
                                     workflow: EnhancedWorkflowDefinition,
                                     execution: EnhancedWorkflowExecution,
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tasks with optimization strategies."""
        tasks = workflow.tasks.copy()
        completed_tasks = set()
        task_results = {}
        
        # Sort tasks by priority and dependencies
        tasks.sort(key=lambda t: (-t.priority, len(t.dependencies)))
        
        while tasks:
            # Find tasks ready to execute
            ready_tasks = [
                task for task in tasks 
                if all(dep in completed_tasks for dep in task.dependencies)
            ]
            
            if not ready_tasks:
                # Check for circular dependencies
                remaining_deps = set()
                for task in tasks:
                    remaining_deps.update(task.dependencies)
                
                if not remaining_deps.intersection(set(t.task_id for t in tasks)):
                    logger.error("Circular dependency detected in workflow")
                    raise RuntimeError("Circular dependency in workflow")
                
                # Wait for dependencies
                await asyncio.sleep(0.1)
                continue
            
            # Execute ready tasks in parallel (up to max_parallel_tasks)
            batch_size = min(len(ready_tasks), workflow.max_parallel_tasks)
            batch_tasks = ready_tasks[:batch_size]
            
            # Execute batch
            batch_results = await self._execute_task_batch(batch_tasks, context, execution)
            
            # Update results and completed tasks
            for task_id, result in batch_results.items():
                task_results[task_id] = result
                completed_tasks.add(task_id)
            
            # Remove completed tasks
            tasks = [task for task in tasks if task.task_id not in completed_tasks]
        
        return task_results
    
    async def _execute_task_batch(self, 
                                tasks: List[EnhancedWorkflowTask],
                                context: Dict[str, Any],
                                execution: EnhancedWorkflowExecution) -> Dict[str, Any]:
        """Execute a batch of tasks in parallel."""
        batch_results = {}
        
        # Create futures for parallel execution
        loop = asyncio.get_event_loop()
        futures = []
        
        for task in tasks:
            task.status = TaskStatus.RUNNING
            task.start_time = time.time()
            
            # Create task context
            task_context = {**context, "task_results": execution.task_results}
            
            # Submit task for execution
            future = loop.run_in_executor(
                self.executor,
                self._execute_single_task,
                task,
                task_context
            )
            futures.append((task, future))
        
        # Wait for all tasks to complete
        for task, future in futures:
            try:
                result = await future
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.end_time = time.time()
                
                # Calculate task metrics
                task.execution_metrics = {
                    "execution_time": task.end_time - task.start_time,
                    "success": True,
                    "resource_usage": self._estimate_resource_usage(task)
                }
                
                batch_results[task.task_id] = result
                
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                task.end_time = time.time()
                
                task.execution_metrics = {
                    "execution_time": task.end_time - task.start_time,
                    "success": False,
                    "error": str(e)
                }
                
                logger.error(f"Task {task.task_id} failed: {str(e)}")
                
                # Apply retry logic if configured
                if task.retry_count > 0:
                    task.retry_count -= 1
                    task.status = TaskStatus.RETRYING
                    # Re-submit for retry (simplified for this example)
        
        return batch_results
    
    def _execute_single_task(self, task: EnhancedWorkflowTask, context: Dict[str, Any]) -> Any:
        """Execute a single task with error handling."""
        try:
            # Apply task-specific optimizations
            if self.enable_optimization and task.optimization_hints:
                context = self._apply_task_optimizations(task, context)
            
            # Execute task function
            result = task.function(context)
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.task_id}, error: {str(e)}")
            raise
    
    async def _optimize_workflow_execution(self, 
                                         workflow: EnhancedWorkflowDefinition,
                                         execution: EnhancedWorkflowExecution,
                                         context: Dict[str, Any]):
        """Apply pre-execution optimizations."""
        execution.status = WorkflowStatus.OPTIMIZING
        
        optimizations = []
        
        # Analyze historical performance
        similar_executions = [
            h for h in self.performance_history 
            if h["workflow_id"] == workflow.workflow_id and h["success"]
        ]
        
        if similar_executions:
            avg_time = sum(h["execution_time"] for h in similar_executions) / len(similar_executions)
            
            # Adjust timeout based on historical data
            if workflow.total_timeout < avg_time * 1.5:
                workflow.total_timeout = int(avg_time * 1.5)
                optimizations.append("timeout_adjustment")
        
        # Optimize task ordering based on dependencies and resource usage
        if len(workflow.tasks) > 1:
            workflow.tasks = self._optimize_task_order(workflow.tasks)
            optimizations.append("task_reordering")
        
        execution.optimization_applied = optimizations
        self.optimization_stats["optimizations_applied"] += len(optimizations)
        
        if optimizations:
            logger.info(f"Applied optimizations: {optimizations}")
    
    def _optimize_task_order(self, tasks: List[EnhancedWorkflowTask]) -> List[EnhancedWorkflowTask]:
        """Optimize task execution order."""
        # Sort by priority and estimated resource usage
        return sorted(tasks, key=lambda t: (-t.priority, t.resource_requirements.get("cpu", 1)))
    
    def _apply_task_optimizations(self, task: EnhancedWorkflowTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply task-specific optimizations."""
        optimized_context = context.copy()
        
        # Apply caching hints
        if "enable_caching" in task.optimization_hints:
            optimized_context["caching_enabled"] = task.optimization_hints["enable_caching"]
        
        # Apply parallel processing hints
        if "parallel_workers" in task.optimization_hints:
            optimized_context["max_workers"] = task.optimization_hints["parallel_workers"]
        
        return optimized_context
    
    async def _apply_post_execution_optimizations(self, execution: EnhancedWorkflowExecution):
        """Apply post-execution optimizations and learning."""
        # Analyze performance and update optimization strategies
        performance_score = self._calculate_performance_score(execution)
        
        if performance_score > 0.8:  # Good performance
            self.optimization_stats["performance_improvements"].append({
                "execution_id": execution.execution_id,
                "score": performance_score,
                "optimizations": execution.optimization_applied
            })
    
    def _calculate_performance_metrics(self, execution: EnhancedWorkflowExecution) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        total_time = execution.end_time - execution.start_time
        
        # Task-level metrics
        task_times = []
        successful_tasks = 0
        failed_tasks = 0
        
        for task_result in execution.task_results.values():
            if isinstance(task_result, dict) and "execution_time" in task_result:
                task_times.append(task_result["execution_time"])
                if task_result.get("success", True):
                    successful_tasks += 1
                else:
                    failed_tasks += 1
        
        return {
            "total_execution_time": total_time,
            "average_task_time": sum(task_times) / len(task_times) if task_times else 0,
            "task_success_rate": successful_tasks / (successful_tasks + failed_tasks) if (successful_tasks + failed_tasks) > 0 else 1,
            "parallel_efficiency": len(task_times) / total_time if total_time > 0 else 0,
            "optimization_impact": len(execution.optimization_applied)
        }
    
    def _calculate_performance_score(self, execution: EnhancedWorkflowExecution) -> float:
        """Calculate overall performance score (0-1)."""
        metrics = execution.performance_metrics
        
        # Weighted scoring
        time_score = min(1.0, 60.0 / metrics.get("total_execution_time", 60))  # Target: under 1 minute
        success_score = metrics.get("task_success_rate", 0)
        efficiency_score = min(1.0, metrics.get("parallel_efficiency", 0))
        
        return (time_score * 0.4 + success_score * 0.4 + efficiency_score * 0.2)
    
    def _estimate_resource_usage(self, task: EnhancedWorkflowTask) -> Dict[str, Any]:
        """Estimate resource usage for a task."""
        execution_time = task.execution_metrics.get("execution_time", 0)
        
        return {
            "cpu_time": execution_time,
            "memory_estimate": task.resource_requirements.get("memory", 100),  # MB
            "io_operations": task.resource_requirements.get("io", 10)
        }
    
    async def _safe_callback(self, callback: Callable, execution: EnhancedWorkflowExecution):
        """Safely execute callback function."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(execution)
            else:
                callback(execution)
        except Exception as e:
            logger.error(f"Callback execution failed: {str(e)}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.performance_history:
            return {"message": "No execution history available"}
        
        successful_executions = [h for h in self.performance_history if h["success"]]
        failed_executions = [h for h in self.performance_history if not h["success"]]
        
        return {
            "total_executions": len(self.performance_history),
            "success_rate": len(successful_executions) / len(self.performance_history) * 100,
            "average_execution_time": sum(h["execution_time"] for h in successful_executions) / len(successful_executions) if successful_executions else 0,
            "optimization_stats": self.optimization_stats,
            "recent_performance": self.performance_history[-10:] if len(self.performance_history) > 10 else self.performance_history
        }
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
