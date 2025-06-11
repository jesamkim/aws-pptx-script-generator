"""Performance Monitoring Dashboard.

This module implements a real-time performance monitoring dashboard for tracking
application metrics, cache efficiency, and resource usage.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time

from src.utils.logger import log_execution_time


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure.
    
    Attributes:
        timestamp: Metric timestamp
        execution_time: Script generation execution time
        cache_hit_rate: Cache hit rate percentage
        memory_usage: Memory usage in MB
        cpu_usage: CPU usage percentage
        success_rate: Success rate percentage
        parallel_tasks: Number of parallel tasks
        quality_score: Script quality score
    """
    timestamp: datetime
    execution_time: float
    cache_hit_rate: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    parallel_tasks: int
    quality_score: float


class PerformanceDashboard:
    """Real-time performance monitoring dashboard."""
    
    def __init__(self):
        """Initialize performance dashboard."""
        self.metrics_history: List[PerformanceMetrics] = []
        self.update_interval = 5  # seconds
        
    def add_metrics(self, metrics: PerformanceMetrics):
        """Add new metrics to history.
        
        Args:
            metrics: Performance metrics to add
        """
        self.metrics_history.append(metrics)
        # Keep last 24 hours of data
        cutoff = datetime.now() - timedelta(hours=24)
        self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff]
    
    def render_dashboard(self):
        """Render performance monitoring dashboard."""
        st.title("🚀 Performance Monitoring Dashboard")
        
        # Current metrics
        if self.metrics_history:
            current = self.metrics_history[-1]
            self._render_current_metrics(current)
        
        # Historical trends
        if len(self.metrics_history) > 1:
            self._render_historical_trends()
        
        # Cache analysis
        self._render_cache_analysis()
        
        # Resource usage
        self._render_resource_usage()
        
        # Quality metrics
        self._render_quality_metrics()
    
    def _render_current_metrics(self, metrics: PerformanceMetrics):
        """Render current performance metrics."""
        st.subheader("📊 Current Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Execution Time",
                f"{metrics.execution_time:.2f}s",
                delta=self._calculate_delta('execution_time')
            )
        
        with col2:
            st.metric(
                "Cache Hit Rate",
                f"{metrics.cache_hit_rate:.1f}%",
                delta=self._calculate_delta('cache_hit_rate')
            )
        
        with col3:
            st.metric(
                "Success Rate",
                f"{metrics.success_rate:.1f}%",
                delta=self._calculate_delta('success_rate')
            )
        
        with col4:
            st.metric(
                "Quality Score",
                f"{metrics.quality_score:.2f}",
                delta=self._calculate_delta('quality_score')
            )
    
    def _render_historical_trends(self):
        """Render historical performance trends."""
        st.subheader("📈 Performance Trends")
        
        # Convert metrics to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': m.timestamp,
                'execution_time': m.execution_time,
                'cache_hit_rate': m.cache_hit_rate,
                'success_rate': m.success_rate,
                'quality_score': m.quality_score
            }
            for m in self.metrics_history
        ])
        
        # Time series plots
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['execution_time'],
            name='Execution Time',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['cache_hit_rate'],
            name='Cache Hit Rate',
            line=dict(color='green'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Performance Over Time',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Execution Time (s)'),
            yaxis2=dict(title='Cache Hit Rate (%)', overlaying='y', side='right'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_cache_analysis(self):
        """Render cache performance analysis."""
        st.subheader("💾 Cache Analysis")
        
        if not self.metrics_history:
            st.info("No cache data available yet")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cache hit rate distribution
            hit_rates = [m.cache_hit_rate for m in self.metrics_history]
            fig = px.histogram(
                hit_rates,
                title='Cache Hit Rate Distribution',
                labels={'value': 'Hit Rate (%)', 'count': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cache efficiency over time
            df = pd.DataFrame([
                {'timestamp': m.timestamp, 'hit_rate': m.cache_hit_rate}
                for m in self.metrics_history
            ])
            
            fig = px.line(
                df,
                x='timestamp',
                y='hit_rate',
                title='Cache Efficiency Trend'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_resource_usage(self):
        """Render resource usage metrics."""
        st.subheader("💻 Resource Usage")
        
        if not self.metrics_history:
            st.info("No resource usage data available yet")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Memory usage
            df = pd.DataFrame([
                {'timestamp': m.timestamp, 'memory': m.memory_usage}
                for m in self.metrics_history
            ])
            
            fig = px.line(
                df,
                x='timestamp',
                y='memory',
                title='Memory Usage (MB)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # CPU usage
            df = pd.DataFrame([
                {'timestamp': m.timestamp, 'cpu': m.cpu_usage}
                for m in self.metrics_history
            ])
            
            fig = px.line(
                df,
                x='timestamp',
                y='cpu',
                title='CPU Usage (%)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_quality_metrics(self):
        """Render script quality metrics."""
        st.subheader("✨ Quality Metrics")
        
        if not self.metrics_history:
            st.info("No quality metrics available yet")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality score distribution
            scores = [m.quality_score for m in self.metrics_history]
            fig = px.histogram(
                scores,
                title='Quality Score Distribution',
                labels={'value': 'Quality Score', 'count': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Success rate trend
            df = pd.DataFrame([
                {'timestamp': m.timestamp, 'success_rate': m.success_rate}
                for m in self.metrics_history
            ])
            
            fig = px.line(
                df,
                x='timestamp',
                y='success_rate',
                title='Success Rate Trend'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _calculate_delta(self, metric_name: str) -> Optional[float]:
        """Calculate metric delta from previous value.
        
        Args:
            metric_name: Name of metric to calculate delta for
            
        Returns:
            Delta value if available, None otherwise
        """
        if len(self.metrics_history) < 2:
            return None
        
        current = getattr(self.metrics_history[-1], metric_name)
        previous = getattr(self.metrics_history[-2], metric_name)
        
        return current - previous
    
    @log_execution_time
    def update_metrics(self, agent_metrics: Dict[str, Any]):
        """Update dashboard with new agent metrics.
        
        Args:
            agent_metrics: Current agent performance metrics
        """
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            execution_time=agent_metrics.get('execution_time', 0),
            cache_hit_rate=agent_metrics.get('cache_hit_rate', 0),
            memory_usage=agent_metrics.get('memory_usage', 0),
            cpu_usage=agent_metrics.get('cpu_usage', 0),
            success_rate=agent_metrics.get('success_rate', 0),
            parallel_tasks=agent_metrics.get('parallel_tasks', 0),
            quality_score=agent_metrics.get('quality_score', 0)
        )
        
        self.add_metrics(metrics)
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics history in specified format.
        
        Args:
            format: Export format ('json' or 'csv')
            
        Returns:
            Metrics data in specified format
        """
        if format == 'json':
            return json.dumps([vars(m) for m in self.metrics_history])
        elif format == 'csv':
            df = pd.DataFrame([vars(m) for m in self.metrics_history])
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Initialize dashboard
dashboard = PerformanceDashboard()
