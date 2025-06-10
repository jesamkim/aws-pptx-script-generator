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
        """Create unified English prompt for natural script generation.
        
        Args:
            request: Script generation request
            
        Returns:
            Formatted prompt for Claude
        """
        # Extract enhanced parameters from request context
        context_lines = request.presentation_context.split('\n')
        technical_level = 'intermediate'
        presentation_type = 'technical_overview'
        script_style = 'conversational'
        
        for line in context_lines:
            if '기술 수준:' in line or 'Technical Level:' in line:
                if 'beginner' in line:
                    technical_level = 'beginner'
                elif 'advanced' in line:
                    technical_level = 'advanced'
            elif '발표 유형:' in line or 'Presentation Type:' in line:
                if 'business_case' in line:
                    presentation_type = 'business_case'
                elif 'deep_dive' in line:
                    presentation_type = 'deep_dive'
                elif 'workshop' in line:
                    presentation_type = 'workshop'
                elif 'demo' in line:
                    presentation_type = 'demo'
            elif '스크립트 스타일:' in line or 'Script Style:' in line:
                if 'technical' in line:
                    script_style = 'technical'
                elif 'formal' in line:
                    script_style = 'formal'
                elif 'educational' in line:
                    script_style = 'educational'
        
        # Create style-specific guidelines
        style_guidelines = {
            'conversational': "friendly and conversational tone, emphasizing audience engagement",
            'technical': "precise technical terminology, focusing on detailed technical explanations",
            'formal': "formal and professional tone, suitable for business environments",
            'educational': "educational and explanatory tone, maximizing learning effectiveness"
        }
        
        level_guidelines = {
            'beginner': "explain basic concepts clearly for audiences with limited technical background",
            'intermediate': "practical explanations for audiences with some technical understanding",
            'advanced': "in-depth content and advanced concepts for highly technical audiences"
        }
        
        type_guidelines = {
            'technical_overview': "focus on technical overview and architecture explanations",
            'business_case': "emphasize business value and ROI-focused explanations",
            'deep_dive': "concentrate on technical details and implementation methods",
            'workshop': "focus on hands-on practice and practical experience",
            'demo': "center on live demonstrations and real-time examples"
        }
        
        # Determine language instruction
        language_instruction = ""
        if request.language == 'Korean':
            language_instruction = "IMPORTANT: Generate all content in Korean language. Use natural, professional Korean suitable for business presentations."
        else:
            language_instruction = "Generate all content in English language. Use natural, professional English suitable for business presentations."
        
        prompt = f"""
You are a professional AWS Solutions Architect and expert at creating natural presentation scripts for actual delivery.

{language_instruction}

**Presenter Information:**
- Name: {request.presenter_info.get('full_name', 'Presenter')}
- Title: {request.presenter_info.get('job_title', 'Solutions Architect')}

**Presentation Context:**
{request.presentation_context}

**Script Style Guidelines:**
- **Technical Level**: {technical_level} - {level_guidelines.get(technical_level, '')}
- **Presentation Type**: {presentation_type} - {type_guidelines.get(presentation_type, '')}
- **Script Style**: {script_style} - {style_guidelines.get(script_style, '')}

**Current Slide Information:**
- Slide Number: {request.slide_number}
- Actual Slide Title: {request.slide_title}
- Slide Content: {request.slide_content}
- Visual Elements: {request.visual_description}
- Key Concepts: {', '.join(request.key_concepts)}
- AWS Services: {', '.join(request.aws_services)}

**Requirements:**
- Target Speaking Time: {request.duration:.1f} minutes (strict time constraint)
- Target Audience: {request.audience_level}
- Language: {request.language}

**Time Management Guidelines:**
- Generate appropriate script length for {request.duration:.1f} minutes
- Aim for approximately 150-200 words per minute
- Focus on core content to prevent time overrun
- Include additional explanations in speaker_notes if needed

**Script Writing Guidelines:**
1. MUST reflect the specified technical level, presentation type, and script style above
2. Write in natural language that a presenter can speak directly
3. Base content on actual slide information for meaningful explanations
4. Avoid meta-references like "In this slide..."
5. Apply audience communication style matching the selected style
6. Adjust explanation depth according to the technical level
7. Structure content and emphasis points according to presentation type

**Output Format:**
Please respond in the following JSON format:
{{
    "opening": "Natural opening statement for the slide (matching style and level)",
    "main_content": "Main content explanation (2-3 minutes of natural presentation script, reflecting selected style)",
    "key_points": ["Key point 1 to emphasize", "Key point 2", "Key point 3"],
    "transition": "Natural transition to next slide",
    "speaker_notes": "Additional notes for the presenter (including style and level considerations)"
}}

Generate a meaningful and natural presentation script based on the actual slide content, ensuring you reflect the selected technical level ({technical_level}), presentation type ({presentation_type}), and script style ({script_style}).
"""
        
        return prompt
        """Create prompt for natural script generation.
        
        Args:
            request: Script generation request
            
        Returns:
            Formatted prompt for Claude
        """
        if request.language == 'Korean':
            # Extract enhanced parameters from request context
            context_lines = request.presentation_context.split('\n')
            technical_level = 'intermediate'
            presentation_type = 'technical_overview'
            script_style = 'conversational'
            
            for line in context_lines:
                if '기술 수준:' in line:
                    if 'beginner' in line:
                        technical_level = 'beginner'
                    elif 'advanced' in line:
                        technical_level = 'advanced'
                elif '발표 유형:' in line:
                    if 'business_case' in line:
                        presentation_type = 'business_case'
                    elif 'deep_dive' in line:
                        presentation_type = 'deep_dive'
                    elif 'workshop' in line:
                        presentation_type = 'workshop'
                    elif 'demo' in line:
                        presentation_type = 'demo'
                elif '스크립트 스타일:' in line:
                    if 'technical' in line:
                        script_style = 'technical'
                    elif 'formal' in line:
                        script_style = 'formal'
                    elif 'educational' in line:
                        script_style = 'educational'
            
            # Create style-specific guidelines
            style_guidelines = {
                'conversational': "친근하고 대화하듯이, 청중과의 소통을 중시하는 톤",
                'technical': "정확하고 전문적인 기술 용어 사용, 구체적인 기술 설명 중심",
                'formal': "격식있고 공식적인 톤, 비즈니스 환경에 적합한 표현",
                'educational': "교육적이고 설명적인 톤, 학습 효과를 높이는 구성"
            }
            
            level_guidelines = {
                'beginner': "기술적 배경이 적은 청중을 위해 기본 개념부터 쉽게 설명",
                'intermediate': "어느 정도 기술적 이해가 있는 청중을 위한 실무 중심 설명",
                'advanced': "높은 기술적 이해도를 가진 청중을 위한 심화 내용과 고급 개념"
            }
            
            type_guidelines = {
                'technical_overview': "기술적 개요와 아키텍처 중심의 설명",
                'business_case': "비즈니스 가치와 ROI 중심의 설명",
                'deep_dive': "기술적 세부사항과 구현 방법 중심",
                'workshop': "실습과 hands-on 경험 중심",
                'demo': "실제 시연과 라이브 데모 중심"
            }
            
            prompt = f"""
당신은 전문적인 AWS 솔루션스 아키텍트이며, 실제 프레젠테이션 발표를 위한 자연스러운 스크립트를 작성하는 전문가입니다.

**발표자 정보:**
- 이름: {request.presenter_info.get('full_name', '발표자')}
- 직책: {request.presenter_info.get('job_title', 'Solutions Architect')}

**프레젠테이션 맥락:**
{request.presentation_context}

**스크립트 스타일 지침:**
- **기술 수준**: {technical_level} - {level_guidelines.get(technical_level, '')}
- **발표 유형**: {presentation_type} - {type_guidelines.get(presentation_type, '')}
- **스크립트 스타일**: {script_style} - {style_guidelines.get(script_style, '')}

**현재 슬라이드 정보:**
- 슬라이드 번호: {request.slide_number}
- 실제 슬라이드 제목: {request.slide_title}
- 슬라이드 내용: {request.slide_content}
- 시각적 요소: {request.visual_description}
- 핵심 개념: {', '.join(request.key_concepts)}
- AWS 서비스: {', '.join(request.aws_services)}

**요구사항:**
- 목표 발표 시간: {request.duration:.1f}분 (엄격한 시간 제한)
- 대상 청중: {request.audience_level}
- 언어: 한국어 (자연스럽고 전문적인 한국어)

**시간 관리 지침:**
- {request.duration:.1f}분에 맞는 적절한 스크립트 분량 생성
- 1분당 약 150-200단어 기준으로 내용 조절
- 시간 초과 방지를 위해 핵심 내용에 집중
- 필요시 부가 설명은 speaker_notes에 포함

**스크립트 작성 지침:**
1. 위에 명시된 기술 수준, 발표 유형, 스크립트 스타일을 반드시 반영
2. 실제 발표자가 그대로 말할 수 있는 자연스러운 한국어로 작성
3. 슬라이드의 실제 내용을 바탕으로 구체적이고 의미있는 설명
4. "이 슬라이드에서는..." 같은 메타 언급 금지
5. 선택된 스타일에 맞는 청중과의 소통 방식 적용
6. 기술 수준에 맞는 적절한 설명 깊이 조절
7. 발표 유형에 맞는 내용 구성과 강조점

**출력 형식:**
다음 JSON 형식으로 응답해주세요:
{{
    "opening": "슬라이드 시작 시 자연스러운 도입 멘트 (스타일과 수준에 맞게)",
    "main_content": "주요 내용 설명 (2-3분 분량의 자연스러운 발표 스크립트, 선택된 스타일 반영)",
    "key_points": ["강조할 핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "transition": "다음 슬라이드로의 자연스러운 전환 멘트",
    "speaker_notes": "발표자를 위한 추가 참고사항 (스타일과 수준 고려사항 포함)"
}}

선택된 기술 수준({technical_level}), 발표 유형({presentation_type}), 스크립트 스타일({script_style})을 반드시 반영하여 실제 슬라이드 내용을 바탕으로 의미있고 자연스러운 발표 스크립트를 생성해주세요.
"""
        else:
            # Extract enhanced parameters from request context (English version)
            context_lines = request.presentation_context.split('\n')
            technical_level = 'intermediate'
            presentation_type = 'technical_overview'
            script_style = 'conversational'
            
            for line in context_lines:
                if 'Technical Level:' in line or '기술 수준:' in line:
                    if 'beginner' in line:
                        technical_level = 'beginner'
                    elif 'advanced' in line:
                        technical_level = 'advanced'
                elif 'Presentation Type:' in line or '발표 유형:' in line:
                    if 'business_case' in line:
                        presentation_type = 'business_case'
                    elif 'deep_dive' in line:
                        presentation_type = 'deep_dive'
                    elif 'workshop' in line:
                        presentation_type = 'workshop'
                    elif 'demo' in line:
                        presentation_type = 'demo'
                elif 'Script Style:' in line or '스크립트 스타일:' in line:
                    if 'technical' in line:
                        script_style = 'technical'
                    elif 'formal' in line:
                        script_style = 'formal'
                    elif 'educational' in line:
                        script_style = 'educational'
            
            # Create style-specific guidelines (English)
            style_guidelines = {
                'conversational': "friendly and conversational tone, emphasizing audience engagement",
                'technical': "precise technical terminology, focusing on detailed technical explanations",
                'formal': "formal and professional tone, suitable for business environments",
                'educational': "educational and explanatory tone, maximizing learning effectiveness"
            }
            
            level_guidelines = {
                'beginner': "explain basic concepts clearly for audiences with limited technical background",
                'intermediate': "practical explanations for audiences with some technical understanding",
                'advanced': "in-depth content and advanced concepts for highly technical audiences"
            }
            
            type_guidelines = {
                'technical_overview': "focus on technical overview and architecture explanations",
                'business_case': "emphasize business value and ROI-focused explanations",
                'deep_dive': "concentrate on technical details and implementation methods",
                'workshop': "focus on hands-on practice and practical experience",
                'demo': "center on live demonstrations and real-time examples"
            }
            
            prompt = f"""
You are a professional AWS Solutions Architect and expert at creating natural presentation scripts for actual delivery.

**Presenter Information:**
- Name: {request.presenter_info.get('full_name', 'Presenter')}
- Title: {request.presenter_info.get('job_title', 'Solutions Architect')}

**Presentation Context:**
{request.presentation_context}

**Script Style Guidelines:**
- **Technical Level**: {technical_level} - {level_guidelines.get(technical_level, '')}
- **Presentation Type**: {presentation_type} - {type_guidelines.get(presentation_type, '')}
- **Script Style**: {script_style} - {style_guidelines.get(script_style, '')}

**Current Slide Information:**
- Slide Number: {request.slide_number}
- Actual Slide Title: {request.slide_title}
- Slide Content: {request.slide_content}
- Visual Elements: {request.visual_description}
- Key Concepts: {', '.join(request.key_concepts)}
- AWS Services: {', '.join(request.aws_services)}

**Requirements:**
- Target Speaking Time: {request.duration:.1f} minutes (strict time constraint)
- Target Audience: {request.audience_level}
- Language: English (natural and professional)

**Time Management Guidelines:**
- Generate appropriate script length for {request.duration:.1f} minutes
- Aim for approximately 150-200 words per minute
- Focus on core content to prevent time overrun
- Include additional explanations in speaker_notes if needed

**Script Writing Guidelines:**
1. MUST reflect the specified technical level, presentation type, and script style above
2. Write in natural English that a presenter can speak directly
3. Base content on actual slide information for meaningful explanations
4. Avoid meta-references like "In this slide..."
5. Apply audience communication style matching the selected style
6. Adjust explanation depth according to the technical level
7. Structure content and emphasis points according to presentation type

**Output Format:**
Please respond in the following JSON format:
{{
    "opening": "Natural opening statement for the slide (matching style and level)",
    "main_content": "Main content explanation (2-3 minutes of natural presentation script, reflecting selected style)",
    "key_points": ["Key point 1 to emphasize", "Key point 2", "Key point 3"],
    "transition": "Natural transition to next slide",
    "speaker_notes": "Additional notes for the presenter (including style and level considerations)"
}}

Generate a meaningful and natural presentation script based on the actual slide content, ensuring you reflect the selected technical level ({technical_level}), presentation type ({presentation_type}), and script style ({script_style}).
"""
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
        
        # Extract enhanced parameters from analysis
        technical_level = presentation_params.get('technical_level', 'intermediate')
        presentation_type = presentation_params.get('presentation_type', 'technical_overview')
        script_style = presentation_params.get('recommended_script_style', 'conversational')
        main_topic = presentation_params.get('main_topic', presentation_analysis.overall_theme)
        key_themes = presentation_params.get('key_themes', [])
        aws_services = presentation_params.get('aws_services_mentioned', [])
        
        # Calculate time per slide with content-aware distribution
        slide_count = len(presentation_analysis.slide_analyses)
        
        # Calculate base time per slide
        base_time_per_slide = duration / max(slide_count, 1)
        
        # Adjust time allocation based on slide complexity and importance
        slide_time_allocations = []
        total_complexity_score = 0
        
        # Calculate complexity scores for each slide
        for slide_analysis in presentation_analysis.slide_analyses:
            # Factors that affect speaking time:
            # 1. Number of key concepts
            # 2. Number of AWS services mentioned
            # 3. Technical depth
            # 4. Content length
            
            concept_factor = min(len(slide_analysis.key_concepts), 5) * 0.2  # Max 1.0
            service_factor = min(len(slide_analysis.aws_services), 3) * 0.3   # Max 0.9
            content_factor = min(len(slide_analysis.visual_description), 500) / 500 * 0.5  # Max 0.5
            
            # Special slide types get different time allocations
            slide_type_factor = 1.0
            if hasattr(slide_analysis, 'slide_type'):
                if slide_analysis.slide_type in ['title', 'agenda']:
                    slide_type_factor = 0.5  # Less time for intro slides
                elif slide_analysis.slide_type in ['demo', 'architecture']:
                    slide_type_factor = 1.5  # More time for complex slides
            
            complexity_score = (1.0 + concept_factor + service_factor + content_factor) * slide_type_factor
            slide_time_allocations.append(complexity_score)
            total_complexity_score += complexity_score
        
        # Normalize time allocations to match total duration
        if total_complexity_score > 0:
            # Reserve 10% of time for opening/closing remarks
            available_time = duration * 0.9
            normalized_times = [(score / total_complexity_score) * available_time 
                              for score in slide_time_allocations]
        else:
            # Fallback to equal distribution
            normalized_times = [base_time_per_slide] * slide_count
        
        # Create enhanced presentation context with all user settings
        presentation_context = f"""
주제: {main_topic}
전체 슬라이드 수: {slide_count}개
발표 시간: {duration}분
기술 수준: {technical_level} (복잡도: {presentation_analysis.technical_complexity:.1f}/5)
대상 청중: {audience}
발표 유형: {presentation_type}
스크립트 스타일: {script_style}
핵심 주제: {', '.join(key_themes[:5]) if key_themes else '일반적인 내용'}
AWS 서비스: {', '.join(aws_services[:10]) if aws_services else '해당 없음'}
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
        
        # Generate script for each slide with allocated time
        for i, slide_analysis in enumerate(presentation_analysis.slide_analyses):
            # Get allocated time for this slide
            allocated_time = normalized_times[i] if i < len(normalized_times) else base_time_per_slide
            
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
                duration=allocated_time,
                audience_level=audience,
                presenter_info=persona_data
            )
            
            # Generate script for this slide
            slide_script = self.generate_slide_script(request)
            
            # Format slide script with allocated time
            if language == 'Korean':
                script += f"""### 슬라이드 {slide_analysis.slide_number}: {request.slide_title}

📢 **발표 스크립트** ({allocated_time:.1f}분 할당)
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
**할당 시간:** {allocated_time:.1f}분 (전체 {duration}분 중)

---

"""
            else:
                script += f"""### Slide {slide_analysis.slide_number}: {request.slide_title}

📢 **Presentation Script** ({allocated_time:.1f} minutes allocated)
```
{slide_script['opening']}

{slide_script['main_content']}

{slide_script['transition']}
```

---

📋 **Speaker Notes**

**Key Points:**"""
                
                for point in slide_script['key_points']:
                    script += f"\n• {point}"
                
                script += f"""

**Speaker Notes:**
{slide_script['speaker_notes']}

**AWS Services:** {', '.join(slide_analysis.aws_services) if slide_analysis.aws_services else 'None'}
**Allocated Time:** {allocated_time:.1f} minutes (out of {duration} total)

---

"""

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
