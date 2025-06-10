"""Claude-based Natural Script Generator.

This module uses Claude 3.7 Sonnet to generate natural, contextual presentation scripts
based on actual slide content rather than templates.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

from config.aws_config import bedrock_client
from src.utils.logger import log_execution_time


@dataclass
class SlideScriptRequest:
    """Request for generating a slide script.
    
    Attributes:
        slide_number: Slide number
        slide_title: Actual slide title
        slide_content: Extracted slide content
        visual_description: Visual elements description
        key_concepts: Key concepts from analysis
        aws_services: AWS services mentioned
        presentation_context: Overall presentation context
        language: Target language (Korean/English)
        duration: Target speaking duration
        audience_level: Target audience level
        presenter_info: Presenter information
    """
    slide_number: int
    slide_title: str
    slide_content: str
    visual_description: str
    key_concepts: List[str]
    aws_services: List[str]
    presentation_context: str
    language: str
    duration: float
    audience_level: str
    presenter_info: Dict[str, str]


class ClaudeScriptGenerator:
    """Natural script generator using Claude 3.7 Sonnet."""
    
    def __init__(self):
        """Initialize Claude script generator."""
        self.model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        self.max_retries = 3
        logger.info("Initialized Claude script generator")
    
    def _create_script_generation_prompt(self, request: SlideScriptRequest) -> str:
        """Create prompt for natural script generation.
        
        Args:
            request: Script generation request
            
        Returns:
            Formatted prompt for Claude
        """
        if request.language == 'Korean':
            prompt = f"""
당신은 전문적인 AWS 솔루션스 아키텍트이며, 실제 프레젠테이션 발표를 위한 자연스러운 스크립트를 작성하는 전문가입니다.

**발표자 정보:**
- 이름: {request.presenter_info.get('full_name', '발표자')}
- 직책: {request.presenter_info.get('job_title', 'Solutions Architect')}

**프레젠테이션 맥락:**
{request.presentation_context}

**현재 슬라이드 정보:**
- 슬라이드 번호: {request.slide_number}
- 실제 슬라이드 제목: {request.slide_title}
- 슬라이드 내용: {request.slide_content}
- 시각적 요소: {request.visual_description}
- 핵심 개념: {', '.join(request.key_concepts)}
- AWS 서비스: {', '.join(request.aws_services)}

**요구사항:**
- 목표 발표 시간: {request.duration:.1f}분
- 대상 청중: {request.audience_level}
- 언어: 한국어 (자연스럽고 전문적인 한국어)

**스크립트 작성 지침:**
1. 실제 발표자가 그대로 말할 수 있는 자연스러운 한국어로 작성
2. 슬라이드의 실제 내용을 바탕으로 구체적이고 의미있는 설명
3. "이 슬라이드에서는..." 같은 메타 언급 금지
4. 청중과의 자연스러운 소통을 위한 발표 톤
5. 기술적 내용을 이해하기 쉽게 설명
6. 실무 적용 가능한 인사이트 포함

**출력 형식:**
다음 JSON 형식으로 응답해주세요:
{{
    "opening": "슬라이드 시작 시 자연스러운 도입 멘트",
    "main_content": "주요 내용 설명 (2-3분 분량의 자연스러운 발표 스크립트)",
    "key_points": ["강조할 핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "transition": "다음 슬라이드로의 자연스러운 전환 멘트",
    "speaker_notes": "발표자를 위한 추가 참고사항"
}}

실제 슬라이드 내용을 바탕으로 의미있고 자연스러운 발표 스크립트를 생성해주세요.
"""
        else:
            prompt = f"""
You are a professional AWS Solutions Architect and expert at creating natural presentation scripts for actual delivery.

**Presenter Information:**
- Name: {request.presenter_info.get('full_name', 'Presenter')}
- Title: {request.presenter_info.get('job_title', 'Solutions Architect')}

**Presentation Context:**
{request.presentation_context}

**Current Slide Information:**
- Slide Number: {request.slide_number}
- Actual Slide Title: {request.slide_title}
- Slide Content: {request.slide_content}
- Visual Elements: {request.visual_description}
- Key Concepts: {', '.join(request.key_concepts)}
- AWS Services: {', '.join(request.aws_services)}

**Requirements:**
- Target Speaking Time: {request.duration:.1f} minutes
- Target Audience: {request.audience_level}
- Language: English (natural and professional)

**Script Writing Guidelines:**
1. Write in natural English that a presenter can speak directly
2. Base content on actual slide information for meaningful explanations
3. Avoid meta-references like "In this slide..."
4. Use natural presentation tone for audience engagement
5. Explain technical content in an accessible way
6. Include practical insights for real-world application

**Output Format:**
Please respond in the following JSON format:
{{
    "opening": "Natural opening statement for the slide",
    "main_content": "Main content explanation (2-3 minutes of natural presentation script)",
    "key_points": ["Key point 1 to emphasize", "Key point 2", "Key point 3"],
    "transition": "Natural transition to next slide",
    "speaker_notes": "Additional notes for the presenter"
}}

Generate a meaningful and natural presentation script based on the actual slide content.
"""
        
        return prompt
    
    @log_execution_time
    def generate_slide_script(self, request: SlideScriptRequest) -> Dict[str, Any]:
        """Generate natural script for a slide using Claude.
        
        Args:
            request: Script generation request
            
        Returns:
            Generated script components
        """
        try:
            prompt = self._create_script_generation_prompt(request)
            
            # Call Claude API
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 3000,
                "temperature": 0.3,  # Slightly creative but consistent
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = bedrock_client.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    script_data = json.loads(json_content)
                    
                    logger.info(f"Generated natural script for slide {request.slide_number}")
                    return script_data
                else:
                    raise Exception("No valid JSON found in Claude response")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude JSON response: {str(e)}")
                # Return fallback structure
                return self._create_fallback_script(request)
                
        except Exception as e:
            logger.error(f"Claude script generation failed: {str(e)}")
            return self._create_fallback_script(request)
    
    def _create_fallback_script(self, request: SlideScriptRequest) -> Dict[str, Any]:
        """Create fallback script when Claude generation fails.
        
        Args:
            request: Script generation request
            
        Returns:
            Fallback script structure
        """
        if request.language == 'Korean':
            return {
                "opening": f"{request.slide_title}에 대해 말씀드리겠습니다.",
                "main_content": f"{request.slide_content}\n\n이 내용의 핵심은 실제 업무에서의 활용 방안입니다.",
                "key_points": request.key_concepts[:3],
                "transition": "다음 내용으로 넘어가겠습니다.",
                "speaker_notes": f"예상 소요 시간: {request.duration:.1f}분"
            }
        else:
            return {
                "opening": f"Let's discuss {request.slide_title}.",
                "main_content": f"{request.slide_content}\n\nThe key here is understanding practical applications.",
                "key_points": request.key_concepts[:3],
                "transition": "Let's move on to the next topic.",
                "speaker_notes": f"Estimated time: {request.duration:.1f} minutes"
            }
    
    def generate_complete_presentation_script(
        self,
        presentation_analysis: Any,
        persona_data: Dict[str, str],
        presentation_params: Dict[str, Any],
        mcp_enhanced_services: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate complete presentation script using Claude.
        
        Args:
            presentation_analysis: Complete presentation analysis
            persona_data: Presenter information
            presentation_params: Presentation parameters
            mcp_enhanced_services: Enhanced AWS service information
            
        Returns:
            Complete natural presentation script
        """
        language = presentation_params.get('language', 'English')
        duration = presentation_params.get('duration', 30)
        audience = presentation_params.get('target_audience', 'Technical')
        
        # Calculate time per slide
        slide_count = len(presentation_analysis.slide_analyses)
        time_per_slide = duration / max(slide_count, 1)
        
        # Create presentation context
        presentation_context = f"""
주제: {presentation_analysis.overall_theme}
전체 슬라이드 수: {slide_count}개
발표 시간: {duration}분
기술 수준: {presentation_analysis.technical_complexity:.1f}/5
대상 청중: {audience}
"""
        
        # Generate script header
        if language == 'Korean':
            script = f"""# {persona_data.get('full_name', '발표자')}님의 {presentation_analysis.overall_theme} 프레젠테이션 스크립트

## 📋 프레젠테이션 개요
- **발표 시간**: {duration}분
- **대상 청중**: {audience}
- **언어**: 한국어
- **주제**: {presentation_analysis.overall_theme}
- **슬라이드 수**: {slide_count}개
- **스크립트 생성**: Claude 3.7 Sonnet 자연어 생성

---

## 🎤 발표 시작 인사

📢 **발표 스크립트**
```
안녕하세요, 여러분. 
저는 {persona_data.get('job_title', 'Solutions Architect')} {persona_data.get('full_name', '발표자')}입니다.

오늘은 {presentation_analysis.overall_theme}에 대해 함께 알아보는 시간을 갖겠습니다.
{duration}분 동안 실무에 바로 적용할 수 있는 내용들을 중심으로 말씀드리겠습니다.

그럼 시작하겠습니다.
```

---

## 📝 슬라이드별 발표 스크립트

"""
        else:
            script = f"""# {persona_data.get('full_name', 'Presenter')}'s {presentation_analysis.overall_theme} Presentation Script

## 📋 Presentation Overview
- **Duration**: {duration} minutes
- **Target Audience**: {audience}
- **Language**: English
- **Topic**: {presentation_analysis.overall_theme}
- **Slide Count**: {slide_count}
- **Script Generation**: Claude 3.7 Sonnet Natural Language Generation

---

## 🎤 Opening Remarks

📢 **Presentation Script**
```
Hello everyone.
I'm {persona_data.get('full_name', 'Presenter')}, {persona_data.get('job_title', 'Solutions Architect')}.

Today we'll explore {presentation_analysis.overall_theme} together.
Over the next {duration} minutes, I'll focus on practical content you can apply immediately.

Let's get started.
```

---

## 📝 Slide-by-Slide Presentation Script

"""
        
        # Generate script for each slide
        for slide_analysis in presentation_analysis.slide_analyses:
            # Create script request
            request = SlideScriptRequest(
                slide_number=slide_analysis.slide_number,
                slide_title=slide_analysis.content_summary[:100] if slide_analysis.content_summary else f"Slide {slide_analysis.slide_number}",
                slide_content=slide_analysis.visual_description,
                visual_description=slide_analysis.visual_description,
                key_concepts=slide_analysis.key_concepts,
                aws_services=slide_analysis.aws_services,
                presentation_context=presentation_context,
                language=language,
                duration=time_per_slide,
                audience_level=audience,
                presenter_info=persona_data
            )
            
            # Generate script for this slide
            slide_script = self.generate_slide_script(request)
            
            # Format slide script
            if language == 'Korean':
                script += f"""### 슬라이드 {slide_analysis.slide_number}: {request.slide_title}

📢 **발표 스크립트** ({time_per_slide:.1f}분)
```
{slide_script['opening']}

{slide_script['main_content']}

{slide_script['transition']}
```

---

📋 **발표자 참고사항**

**핵심 포인트:**"""
                
                for point in slide_script['key_points']:
                    script += f"\n• {point}"
                
                script += f"""

**발표자 노트:**
{slide_script['speaker_notes']}

**AWS 서비스:** {', '.join(slide_analysis.aws_services) if slide_analysis.aws_services else '해당 없음'}

---

"""
            else:
                script += f"""### Slide {slide_analysis.slide_number}: {request.slide_title}

📢 **Presentation Script** ({time_per_slide:.1f} minutes)
```
{slide_script['opening']}

{slide_script['main_content']}

{slide_script['transition']}
```

---

📋 **Speaker Reference**

**Key Points:**"""
                
                for point in slide_script['key_points']:
                    script += f"\n• {point}"
                
                script += f"""

**Speaker Notes:**
{slide_script['speaker_notes']}

**AWS Services:** {', '.join(slide_analysis.aws_services) if slide_analysis.aws_services else 'None'}

---

"""
        
        # Add closing
        if language == 'Korean':
            script += """## 🎤 마무리

📢 **발표 스크립트**
```
오늘 말씀드린 내용들이 여러분의 실무에 도움이 되기를 바랍니다.
궁금한 점이 있으시면 언제든 질문해 주세요.

감사합니다.
```

## ✅ 스크립트 특징
- **생성 방식**: Claude 3.7 Sonnet 자연어 생성
- **품질**: 실제 슬라이드 내용 기반 자연스러운 스크립트
- **언어**: 일관된 한국어 사용
- **실용성**: 바로 사용 가능한 발표용 스크립트
"""
        else:
            script += """## 🎤 Closing

📢 **Presentation Script**
```
I hope today's content will be helpful for your practical work.
Please feel free to ask questions anytime.

Thank you.
```

## ✅ Script Features
- **Generation Method**: Claude 3.7 Sonnet Natural Language Generation
- **Quality**: Natural scripts based on actual slide content
- **Language**: Consistent English usage
- **Practicality**: Ready-to-use presentation scripts
"""
        
        return script
