#!/usr/bin/env python3
"""
Test script to verify the improved script generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.script_generation.claude_script_generator import ClaudeScriptGenerator, SlideScriptRequest

def test_korean_script_generation():
    """Test Korean script generation with improved prompts"""
    
    generator = ClaudeScriptGenerator()
    
    # Create a test request
    request = SlideScriptRequest(
        slide_number=2,
        slide_title="AWS Strands Agents 소개",
        slide_content="Strands Agents는 에이전트 개발을 간소화하기 위해 설계된 오픈 소스 Python SDK입니다.",
        visual_description="제품 로고와 주요 특징들이 표시된 슬라이드",
        key_concepts=["오픈소스", "Python SDK", "에이전트 개발"],
        aws_services=["Bedrock", "Lambda"],
        presentation_context="기술 수준: intermediate\n발표 유형: technical_overview\n스크립트 스타일: conversational",
        language="Korean",
        duration=1.0,
        audience_level="Mixed",
        presenter_info={"full_name": "김제삼", "job_title": "SA"}
    )
    
    # Generate script
    result = generator.generate_slide_script(request)
    
    print("=== Generated Script ===")
    print(f"Opening: {result.get('opening', 'N/A')}")
    print(f"Main Content: {result.get('main_content', 'N/A')}")
    print(f"Transition: {result.get('transition', 'N/A')}")
    
    # Check for issues
    issues = []
    if "안녕하세요" in result.get('opening', '') or "안녕하세요" in result.get('main_content', ''):
        issues.append("Contains greeting '안녕하세요'")
    
    content = result.get('main_content', '')
    if content.count("이제") > 1:
        issues.append(f"Overuses '이제' ({content.count('이제')} times)")
    
    if issues:
        print(f"\n⚠️  Issues found: {', '.join(issues)}")
    else:
        print("\n✅ No issues found!")

if __name__ == "__main__":
    test_korean_script_generation()
