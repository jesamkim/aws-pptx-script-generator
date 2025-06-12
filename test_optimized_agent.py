#!/usr/bin/env python3
"""Test script for Optimized Script Agent functionality."""

import sys
import os
import asyncio
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.optimized_script_agent import OptimizedScriptAgent, OptimizedPersonaProfile


def test_optimized_agent():
    """Test optimized agent functionality."""
    print("🧪 Testing Optimized Script Agent...")
    
    # Initialize optimized agent
    agent = OptimizedScriptAgent(enable_caching=True, max_workers=4)
    
    # Mock presentation data
    class MockSlideAnalysis:
        def __init__(self, slide_num):
            self.slide_number = slide_num
            self.content_summary = f"AWS Service Overview - Slide {slide_num}"
            self.visual_description = f"This slide covers AWS service {slide_num} architecture and best practices"
            self.key_concepts = [f"scalability", f"security", f"cost-optimization"]
            self.aws_services = ["EC2", "S3"] if slide_num % 2 == 0 else ["Lambda", "DynamoDB"]
    
    class MockPresentationAnalysis:
        def __init__(self):
            self.overall_theme = "AWS Architecture Best Practices"
            self.technical_complexity = 3.5
            self.slide_analyses = [MockSlideAnalysis(i) for i in range(1, 6)]  # 5 slides
    
    # Create optimized persona profile
    persona_profile = OptimizedPersonaProfile(
        full_name="Test Presenter",
        job_title="Senior Solutions Architect",
        experience_level="Senior",
        presentation_style="Technical",
        specializations=["AWS", "Cloud Architecture", "DevOps"],
        language="English",
        cultural_context={"region": "global"},
        optimization_preferences={
            "confidence": "Expert",
            "enable_caching": True,
            "parallel_processing": True,
            "quality_focus": "high"
        }
    )
    
    # Test presentation parameters
    presentation_params = {
        'language': 'English',
        'duration': 25,
        'target_audience': 'Technical',
        'technical_level': 'advanced',
        'presentation_type': 'technical_overview',
        'recommended_script_style': 'technical',
        'main_topic': 'AWS Architecture Best Practices',
        'key_themes': ['Scalability', 'Security', 'Cost Optimization', 'Performance'],
        'aws_services_mentioned': ['EC2', 'S3', 'Lambda', 'DynamoDB', 'CloudFormation'],
        'time_per_slide': 3.0,
        'include_qa': True,
        'qa_duration': 10,
        'technical_depth': 4,
        'include_timing': True,
        'include_transitions': True,
        'include_speaker_notes': True,
        'include_qa_prep': True
    }
    
    async def run_test():
        """Run the async test."""
        print("📝 Generating script with optimized agent...")
        start_time = time.time()
        
        try:
            # Create presentation analysis
            presentation_analysis = MockPresentationAnalysis()
            
            # Generate script using optimized agent
            result = await agent.generate_script_optimized(
                presentation_analysis=presentation_analysis,
                persona_profile=persona_profile,
                presentation_params=presentation_params
            )
            
            generation_time = time.time() - start_time
            
            if result.success:
                print(f"✅ Script generation successful!")
                print(f"⏱️  Generation time: {generation_time:.2f} seconds")
                print(f"📊 Script length: {len(result.script_content)} characters")
                print(f"🎯 Quality score: {result.quality_score:.2f}")
                
                # Display performance metrics
                print("\n📈 Performance Metrics:")
                for key, value in result.performance_metrics.items():
                    print(f"  • {key}: {value}")
                
                # Display cache performance
                print("\n🚀 Cache Performance:")
                for key, value in result.cache_performance.items():
                    print(f"  • {key}: {value}")
                
                # Display optimization suggestions
                if result.optimization_suggestions:
                    print("\n💡 Optimization Suggestions:")
                    for suggestion in result.optimization_suggestions:
                        print(f"  • {suggestion}")
                
                # Display agent performance summary
                print("\n🎯 Agent Performance Summary:")
                performance_summary = agent.get_performance_summary()
                for key, value in performance_summary.items():
                    print(f"  • {key}: {value}")
                
                print("\n✨ Optimized agent test completed successfully!")
                
                # Test multiple executions for performance comparison
                print("\n🔄 Testing multiple executions for performance analysis...")
                
                execution_times = []
                for i in range(3):
                    print(f"  Execution {i+1}/3...")
                    exec_start = time.time()
                    
                    exec_result = await agent.generate_script_optimized(
                        presentation_analysis=presentation_analysis,
                        persona_profile=persona_profile,
                        presentation_params=presentation_params
                    )
                    
                    exec_time = time.time() - exec_start
                    execution_times.append(exec_time)
                    
                    if exec_result.success:
                        print(f"    ✅ Completed in {exec_time:.2f}s")
                    else:
                        print(f"    ❌ Failed in {exec_time:.2f}s")
                
                # Performance analysis
                avg_time = sum(execution_times) / len(execution_times)
                print(f"\n📊 Performance Analysis:")
                print(f"  • Average execution time: {avg_time:.2f}s")
                print(f"  • First execution: {execution_times[0]:.2f}s")
                print(f"  • Subsequent executions: {execution_times[1:]}")
                
                if len(execution_times) > 1:
                    improvement = ((execution_times[0] - avg_time) / execution_times[0]) * 100
                    print(f"  • Performance improvement: {improvement:.1f}%")
                
                # Final agent summary
                final_summary = agent.get_performance_summary()
                print(f"\n🏆 Final Agent Summary:")
                print(f"  • Total executions: {final_summary['total_executions']}")
                print(f"  • Success rate: {final_summary['success_rate']:.1f}%")
                print(f"  • Average execution time: {final_summary['average_execution_time']:.2f}s")
                print(f"  • Cache hit rate: {final_summary['cache_hit_rate']:.1f}%")
                
            else:
                print(f"❌ Script generation failed!")
                print(f"Error: {result.metadata.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run the async test
    asyncio.run(run_test())


if __name__ == "__main__":
    test_optimized_agent()
