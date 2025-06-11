#!/usr/bin/env python3
"""Test Korean Script Generation.

This script tests Korean language script generation to ensure
proper language handling and output.
"""

import sys
import os
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_mock_presentation_analysis():
    """Create mock presentation analysis for testing."""
    class MockSlideAnalysis:
        def __init__(self, slide_number: int, slide_type: str, content: str):
            self.slide_number = slide_number
            self.content_summary = f"{slide_type.title()} Slide {slide_number}"
            self.visual_description = content
            self.key_concepts = ["개념1", "개념2", "개념3"]
            self.aws_services = ["Lambda", "S3"] if "technical" in slide_type else []
    
    class MockPresentationAnalysis:
        def __init__(self):
            self.overall_theme = "AWS 서버리스 아키텍처 모범 사례"
            self.technical_complexity = 4.2
            self.slide_analyses = [
                MockSlideAnalysis(1, "title", "제목 슬라이드 - 발표자 소개"),
                MockSlideAnalysis(2, "agenda", "아젠다 - 다룰 주제들의 개요"),
                MockSlideAnalysis(3, "technical", "AWS Lambda 함수 심화 설명 및 코드 예제"),
                MockSlideAnalysis(4, "technical", "Amazon S3 스토리지 패턴 및 최적화 전략"),
                MockSlideAnalysis(5, "summary", "핵심 내용 요약 및 권장사항")
            ]
    
    return MockPresentationAnalysis()

def test_korean_script_generation():
    """Test Korean script generation."""
    print("🇰🇷 Testing Korean Script Generation...")
    
    try:
        from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
        
        # Initialize generator
        generator = ClaudeScriptGeneratorCached(enable_caching=True)
        print("✅ Script generator initialized")
        
        # Create test data
        presentation_analysis = create_mock_presentation_analysis()
        
        persona_data = {
            'full_name': '김제삼',
            'job_title': '시니어 솔루션스 아키텍트',
            'experience_level': 'Senior',
            'presentation_confidence': 'Expert',
            'interaction_style': 'Conversational'
        }
        
        presentation_params = {
            'duration': 15,
            'target_audience': 'Technical',
            'language': 'Korean',  # 한국어 설정
            'technical_level': 'advanced',
            'presentation_type': 'technical_deep_dive',
            'recommended_script_style': 'conversational',
            'main_topic': 'AWS 서버리스 모범 사례',
            'include_qa': True,
            'qa_duration': 3,
            'technical_depth': 4,
            'include_timing': True,
            'include_transitions': True,
            'include_speaker_notes': True,
            'include_qa_prep': True
        }
        
        print("   Generating Korean script...")
        script = generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=presentation_params
        )
        
        print(f"✅ Script generated successfully")
        print(f"   Script length: {len(script)} characters")
        
        # Check for Korean content
        korean_indicators = ['안녕하세요', '발표', '슬라이드', '시간', '분', '질문', '답변']
        korean_found = sum(1 for indicator in korean_indicators if indicator in script)
        
        if korean_found >= 3:
            print(f"✅ Korean content detected ({korean_found} indicators found)")
        else:
            print(f"⚠️  Limited Korean content detected ({korean_found} indicators found)")
        
        # Check for English content (should be minimal)
        english_indicators = ['Good morning', 'Welcome', 'Today', 'presentation', 'slide']
        english_found = sum(1 for indicator in english_indicators if indicator in script)
        
        if english_found == 0:
            print("✅ No English content found - pure Korean script")
        elif english_found <= 2:
            print(f"⚠️  Some English content found ({english_found} indicators)")
        else:
            print(f"❌ Too much English content found ({english_found} indicators)")
        
        # Save script for review
        with open("test_korean_script_output.md", "w", encoding="utf-8") as f:
            f.write(script)
        print("✅ Korean script saved to test_korean_script_output.md")
        
        # Show first few lines
        print("\n📝 Script Preview (first 500 characters):")
        print("-" * 50)
        print(script[:500] + "...")
        print("-" * 50)
        
        return korean_found >= 3 and english_found <= 2
        
    except Exception as e:
        print(f"❌ Korean script generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Korean script generation test."""
    print("🎯 Korean Script Generation Test")
    print("=" * 40)
    
    success = test_korean_script_generation()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Korean script generation test passed!")
        print("✅ Ready for Korean presentations")
    else:
        print("⚠️  Korean script generation needs improvement")
        print("📝 Check the generated script for language consistency")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
