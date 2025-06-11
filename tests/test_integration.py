"""Integration Tests for AWS PPTX Script Generator."""

import sys
import os
import asyncio
import time
import unittest
from unittest.mock import MagicMock, patch
import pytest
import psutil
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.optimized_script_agent import OptimizedScriptAgent, OptimizedPersonaProfile
from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
from src.analysis.multimodal_analyzer import MultimodalAnalyzer
from src.mcp_integration.knowledge_enhancer import KnowledgeEnhancer


class TestIntegration(unittest.TestCase):
    """Integration test suite for AWS PPTX Script Generator."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Initialize components
        cls.agent = OptimizedScriptAgent(enable_caching=True, max_workers=4)
        cls.generator = ClaudeScriptGeneratorCached(enable_caching=True)
        cls.analyzer = MultimodalAnalyzer()
        cls.enhancer = KnowledgeEnhancer()

        # Test data
        cls.test_persona = OptimizedPersonaProfile(
            full_name="Test Presenter",
            job_title="Senior Solutions Architect",
            experience_level="Senior",
            presentation_style="Technical",
            specializations=["AWS", "Cloud Architecture"],
            language="English",
            cultural_context={},
            optimization_preferences={
                "confidence": "Expert",
                "enable_caching": True,
                "parallel_processing": True
            }
        )

        cls.test_params = {
            'language': 'English',
            'duration': 30,
            'target_audience': 'Technical',
            'technical_level': 'advanced',
            'presentation_type': 'technical_overview',
            'recommended_script_style': 'technical',
            'time_per_slide': 3.0,
            'include_qa': True,
            'qa_duration': 10,
            'technical_depth': 4,
            'include_timing': True,
            'include_transitions': True,
            'include_speaker_notes': True,
            'include_qa_prep': True
        }

    def setUp(self):
        """Set up individual test cases."""
        self.start_time = time.time()
        logger.info(f"Starting test: {self._testMethodName}")

    def tearDown(self):
        """Clean up after each test."""
        execution_time = time.time() - self.start_time
        logger.info(f"Test completed in {execution_time:.2f}s: {self._testMethodName}")

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Mock presentation data
        presentation_analysis = self._create_mock_presentation()

        # Execute workflow
        result = await self.agent.generate_script_optimized(
            presentation_analysis=presentation_analysis,
            persona_profile=self.test_persona,
            presentation_params=self.test_params
        )

        # Verify results
        self.assertTrue(result.success)
        self.assertIsNotNone(result.script_content)
        self.assertGreater(result.quality_score, 0.7)
        self.assertGreater(len(result.script_content), 1000)

        # Verify performance metrics
        self.assertIn('execution_time', result.performance_metrics)
        self.assertIn('parallel_tasks', result.performance_metrics)
        self.assertIn('cache_enabled', result.performance_metrics)

    def test_cache_performance(self):
        """Test caching performance."""
        # Generate script multiple times with same content
        presentation = self._create_mock_presentation()
        execution_times = []

        for i in range(3):
            start_time = time.time()
            script = self.generator.generate_complete_presentation_script(
                presentation_analysis=presentation,
                persona_data=self.test_persona.__dict__,
                presentation_params=self.test_params
            )
            execution_times.append(time.time() - start_time)

        # Verify cache effectiveness
        self.assertGreater(execution_times[0], execution_times[1])
        cache_stats = self.generator.get_cache_performance()
        self.assertGreater(cache_stats.get('hits', 0), 0)

    def test_error_handling(self):
        """Test error handling and recovery."""
        with patch.object(self.generator, '_invoke_claude_with_cache') as mock_invoke:
            # Simulate API error
            mock_invoke.side_effect = Exception("API Error")

            with self.assertRaises(Exception):
                self.generator.generate_complete_presentation_script(
                    presentation_analysis=self._create_mock_presentation(),
                    persona_data=self.test_persona.__dict__,
                    presentation_params=self.test_params
                )

    def test_parallel_processing(self):
        """Test parallel processing capabilities."""
        presentation = self._create_mock_presentation(slide_count=10)
        start_time = time.time()

        # Generate script with parallel processing
        script = self.generator.generate_complete_presentation_script(
            presentation_analysis=presentation,
            persona_data=self.test_persona.__dict__,
            presentation_params=self.test_params
        )

        parallel_time = time.time() - start_time

        # Disable parallel processing
        self.agent.max_workers = 1
        start_time = time.time()

        script_sequential = self.generator.generate_complete_presentation_script(
            presentation_analysis=presentation,
            persona_data=self.test_persona.__dict__,
            presentation_params=self.test_params
        )

        sequential_time = time.time() - start_time

        # Verify parallel processing is faster
        self.assertLess(parallel_time, sequential_time)

    def test_memory_usage(self):
        """Test memory usage under load."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Generate multiple scripts
        for _ in range(5):
            script = self.generator.generate_complete_presentation_script(
                presentation_analysis=self._create_mock_presentation(),
                persona_data=self.test_persona.__dict__,
                presentation_params=self.test_params
            )

        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB

        # Verify memory usage is reasonable
        self.assertLess(memory_increase, 500)  # Less than 500MB increase

    def _create_mock_presentation(self, slide_count=5):
        """Create mock presentation for testing."""
        class MockSlideAnalysis:
            def __init__(self, num):
                self.slide_number = num
                self.content_summary = f"Test Slide {num}"
                self.visual_description = f"Description for slide {num}"
                self.key_concepts = ["concept1", "concept2"]
                self.aws_services = ["EC2", "S3"]

        class MockPresentation:
            def __init__(self, slides):
                self.overall_theme = "AWS Architecture"
                self.technical_complexity = 3.5
                self.slide_analyses = [MockSlideAnalysis(i) for i in range(slides)]

        return MockPresentation(slide_count)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
