"""Claude-based Natural Script Generator with Prompt Caching.

This module uses Claude 3.7 Sonnet to generate natural, contextual presentation scripts
based on actual slide content with optimized prompt caching for performance.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

from config.aws_config import bedrock_client
from src.utils.logger import log_execution_time
from .prompt_cache_manager import PromptCacheManager, CacheConfig


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
    """Natural script generator using Claude 3.7 Sonnet with prompt caching."""
    
    def __init__(self, enable_caching: bool = True):
        """Initialize Claude script generator with caching support.
        
        Args:
            enable_caching: Whether to enable prompt caching
        """
        self.model_id = bedrock_client.config.bedrock_model_id
        self.max_retries = 3
        self.enable_caching = enable_caching
        
        # Initialize cache manager if caching is enabled
        if self.enable_caching:
            cache_config = CacheConfig(
                type="ephemeral",
                namespace="aws-pptx-script-generator",
                version="1.0.0",
                ttl=300  # 5 minutes
            )
            self.cache_manager = PromptCacheManager(cache_config)
        else:
            self.cache_manager = None
            
        logger.info(f"Initialized Claude script generator with caching: {enable_caching}")
    
    def _get_static_prompt_content(self, 
                                 presentation_context: str,
                                 presenter_info: Dict[str, str],
                                 language: str) -> str:
        """Get static content that can be cached.
        
        Args:
            presentation_context: Overall presentation context
            presenter_info: Presenter information
            language: Target language
            
        Returns:
            Static prompt content for caching
        """
        # Determine language instruction
        language_instruction = ""
        if language == 'Korean':
            language_instruction = """IMPORTANT: Generate all content in Korean language. Use natural, professional Korean suitable for business presentations.

**Korean Style Guidelines:**
- Use varied transition expressions instead of repeating "이제" (now)
- Alternative transitions: "다음으로", "계속해서", "여기서", "한편", "또한", "그리고", "더불어"
- Avoid starting each slide with greetings - the presentation has already begun
- Use natural Korean business presentation flow
- Vary sentence structures to avoid monotony
- Use appropriate honorifics and professional language"""
        else:
            language_instruction = "Generate all content in English language. Use natural, professional English suitable for business presentations."
        
        static_content = f"""
You are a professional AWS Solutions Architect and expert at creating natural presentation scripts for actual delivery.

{language_instruction}

**Presenter Information:**
- Name: {presenter_info.get('full_name', 'Presenter')}
- Title: {presenter_info.get('job_title', 'Solutions Architect')}
- Experience: {presenter_info.get('experience_level', 'Senior')}
- Confidence: {presenter_info.get('presentation_confidence', 'Comfortable')}
- Style: {presenter_info.get('interaction_style', 'Conversational')}

**Presentation Context:**
{presentation_context}

**Script Generation Guidelines:**
1. Create natural, conversational scripts that sound authentic when spoken
2. Include appropriate timing cues and transitions
3. Adapt technical depth to the specified audience level
4. Incorporate presenter's personal style and confidence level
5. Ensure smooth flow between slides with natural transitions
6. Add speaker notes and tips when requested
7. Include Q&A preparation if specified

**Output Format:**
- Provide complete, ready-to-deliver scripts
- Include timing guidance and speaker notes
- Use natural language that flows well when spoken
- Maintain consistency with presenter's style and experience level
"""
        return static_content
    
    def _invoke_claude_with_cache(self,
                                static_content: str,
                                dynamic_content: str,
                                max_tokens: int = 4000) -> Dict[str, Any]:
        """Invoke Claude with prompt caching support.
        
        Args:
            static_content: Static content to cache
            dynamic_content: Dynamic content for this request
            max_tokens: Maximum tokens to generate
            
        Returns:
            Claude response
        """
        try:
            if self.enable_caching and self.cache_manager:
                # Prepare cached prompt
                prompt_config = self.cache_manager.prepare_cached_prompt(
                    static_content=static_content,
                    dynamic_content=dynamic_content,
                    breakpoints=[1024, 2048]  # Cache breakpoints at 1K and 2K tokens
                )
                
                # Prepare request body with cache control
                body = {
                    "prompt": prompt_config["prompt"],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "cache_control": prompt_config["cache_control"]
                }
            else:
                # Standard request without caching
                body = {
                    "prompt": f"{static_content}\n\n{dynamic_content}",
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            
            # Invoke Claude
            response = bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Update cache statistics if caching is enabled
            if self.enable_caching and self.cache_manager:
                self.cache_manager.update_cache_stats(response_body)
            
            return response_body
            
        except Exception as e:
            logger.error(f"Claude invocation failed: {str(e)}")
            raise
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
            language_instruction = """IMPORTANT: Generate all content in Korean language. Use natural, professional Korean suitable for business presentations.

**Korean Style Guidelines:**
- Use varied transition expressions instead of repeating "이제" (now)
- Alternative transitions: "다음으로", "계속해서", "여기서", "한편", "또한", "그리고", "더불어"
- Avoid starting each slide with greetings - the presentation has already begun
- Use natural Korean business presentation flow
- Vary sentence structures to avoid monotony
- Use appropriate honorifics and professional language"""
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
8. **IMPORTANT**: Do NOT start with greetings like "안녕하세요" or "Hello" - assume the presentation has already begun
9. **IMPORTANT**: Avoid overusing transition words like "이제" (now), "그럼" (then), "자" (well) - use varied transitions
10. Create smooth, natural flow without repetitive opening phrases

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
                "opening": f"슬라이드 {request.slide_number}번을 보시겠습니다.",
                "main_content": f"{request.slide_title}에 대해 말씀드리겠습니다. {request.slide_content}",
                "key_points": request.key_concepts[:3],
                "transition": "다음 내용으로 넘어가겠습니다.",
                "speaker_notes": f"예상 소요 시간: {request.duration:.1f}분"
            }
        else:
            return {
                "opening": f"Let's look at slide {request.slide_number}.",
                "main_content": f"I'll discuss {request.slide_title}. {request.slide_content}",
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
        
        # Extract new presentation settings
        time_per_slide = presentation_params.get('time_per_slide', 2.0)
        include_qa = presentation_params.get('include_qa', True)
        qa_duration = presentation_params.get('qa_duration', 10)
        technical_depth = presentation_params.get('technical_depth', 3)
        include_timing = presentation_params.get('include_timing', True)
        include_transitions = presentation_params.get('include_transitions', True)
        include_speaker_notes = presentation_params.get('include_speaker_notes', True)
        include_qa_prep = presentation_params.get('include_qa_prep', True)
        
        # Extract presenter preferences
        presentation_confidence = persona_data.get('presentation_confidence', 'Comfortable')
        interaction_style = persona_data.get('interaction_style', 'Conversational')
        
        # Calculate effective content duration
        content_duration = duration - (qa_duration if include_qa else 0)
        
        # Calculate time per slide with content-aware distribution
        slide_count = len(presentation_analysis.slide_analyses)
        
        # Use user-specified time per slide or calculate based on content duration
        if time_per_slide * slide_count <= content_duration:
            base_time_per_slide = time_per_slide
        else:
            base_time_per_slide = content_duration / max(slide_count, 1)
            logger.warning(f"Adjusted time per slide from {time_per_slide} to {base_time_per_slide:.1f} minutes to fit duration")
        
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
발표 시간: {duration}분 (Q&A {qa_duration if include_qa else 0}분 포함)
기술 수준: {technical_level} (복잡도: {technical_depth}/5)
대상 청중: {audience}
발표 유형: {presentation_type}
스크립트 스타일: {script_style}
핵심 주제: {', '.join(key_themes[:5]) if key_themes else '일반적인 내용'}
AWS 서비스: {', '.join(aws_services[:10]) if aws_services else '해당 없음'}

발표자 설정:
- 발표 자신감: {presentation_confidence}
- 상호작용 스타일: {interaction_style}
- 슬라이드당 목표 시간: {time_per_slide:.1f}분

스크립트 요구사항:
- 타이밍 가이드: {'포함' if include_timing else '미포함'}
- 슬라이드 전환: {'자연스러운 전환 포함' if include_transitions else '기본 전환만'}
- 발표자 노트: {'상세 노트 포함' if include_speaker_notes else '기본 노트만'}
- Q&A 준비: {'예상 질문 포함' if include_qa_prep else '미포함'}
"""
        
        # Generate script header with language-specific content
        if language == 'Korean':
            script = f"""# {persona_data.get('full_name', '발표자')}님의 {main_topic} 프레젠테이션 스크립트

## 📋 프레젠테이션 개요
- **발표 시간**: {duration}분 ({content_duration}분 발표 + {qa_duration if include_qa else 0}분 Q&A)
- **대상 청중**: {audience}
- **언어**: 한국어
- **주제**: {main_topic}
- **슬라이드 수**: {slide_count}개
- **기술 수준**: {technical_depth}/5 ({technical_level})
- **발표 스타일**: {script_style}
- **스크립트 생성**: Claude 3.7 Sonnet 자연어 생성

## 🎯 발표자 가이드
- **발표 자신감 수준**: {presentation_confidence}
- **상호작용 스타일**: {interaction_style}
- **슬라이드당 목표 시간**: {time_per_slide:.1f}분
{'- **타이밍 가이드**: 각 섹션별 시간 안내 포함' if include_timing else ''}
{'- **전환 가이드**: 자연스러운 슬라이드 전환 문구 포함' if include_transitions else ''}
{'- **발표자 노트**: 상세한 발표 팁과 주의사항 포함' if include_speaker_notes else ''}

---

## 🎤 발표 시작 인사

📢 **발표 스크립트**
```
안녕하세요, 여러분. 
저는 {persona_data.get('job_title', 'Solutions Architect')} {persona_data.get('full_name', '발표자')}입니다.

오늘은 {main_topic}에 대해 함께 알아보는 시간을 갖겠습니다.
{content_duration}분 동안 실무에 바로 적용할 수 있는 내용들을 중심으로 말씀드리겠습니다.
{'마지막에는 질의응답 시간도 준비되어 있으니 궁금한 점이 있으시면 언제든 말씀해 주세요.' if include_qa else ''}

시작하겠습니다.
```

{'## ⏰ 타이밍 가이드' if include_timing else ''}
{'- 전체 발표: ' + str(content_duration) + '분' if include_timing else ''}
{'- 슬라이드당 평균: ' + f'{time_per_slide:.1f}분' if include_timing else ''}
{'- Q&A 시간: ' + str(qa_duration) + '분' if include_timing and include_qa else ''}

---

## 📝 슬라이드별 발표 스크립트

"""
        else:
            script = f"""# {persona_data.get('full_name', 'Presenter')}'s {main_topic} Presentation Script

## 📋 Presentation Overview
- **Duration**: {duration} minutes ({content_duration} min presentation + {qa_duration if include_qa else 0} min Q&A)
- **Target Audience**: {audience}
- **Language**: English
- **Topic**: {main_topic}
- **Slide Count**: {slide_count}
- **Technical Level**: {technical_depth}/5 ({technical_level})
- **Presentation Style**: {script_style}
- **Script Generation**: Claude 3.7 Sonnet Natural Language Generation

## 🎯 Presenter Guide
- **Presentation Confidence**: {presentation_confidence}
- **Interaction Style**: {interaction_style}
- **Target Time per Slide**: {time_per_slide:.1f} minutes
{'- **Timing Cues**: Section timing guidance included' if include_timing else ''}
{'- **Transition Guide**: Natural slide transition phrases included' if include_transitions else ''}
{'- **Speaker Notes**: Detailed presentation tips and notes included' if include_speaker_notes else ''}

---

## 🎤 Opening Remarks

📢 **Presentation Script**
```
Hello everyone.
I'm {persona_data.get('full_name', 'Presenter')}, {persona_data.get('job_title', 'Solutions Architect')}.

Today we'll explore {main_topic} together.
I'll focus on practical content you can apply immediately over the next {content_duration} minutes.
{'We'll also have time for Q&A at the end, so please feel free to ask questions.' if include_qa else ''}

Let's get started.
```

{'## ⏰ Timing Guide' if include_timing else ''}
{'- Total Presentation: ' + str(content_duration) + ' minutes' if include_timing else ''}
{'- Average per Slide: ' + f'{time_per_slide:.1f} minutes' if include_timing else ''}
{'- Q&A Time: ' + str(qa_duration) + ' minutes' if include_timing and include_qa else ''}

---

## 📝 Slide-by-Slide Script

"""

## 📋 Presentation Overview
- **Duration**: {duration} minutes
- **Target Audience**: {audience}
- **Language**: English
- **Topic**: {main_topic}
- **Slide Count**: {slide_count}
- **Script Generation**: Claude 3.7 Sonnet Natural Language Generation

---

## 🎤 Opening Remarks

📢 **Presentation Script**
```
Hello everyone.
I'm {persona_data.get('full_name', 'Presenter')}, {persona_data.get('job_title', 'Solutions Architect')}.

Today we'll explore {main_topic} together.
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
        
        # Add closing remarks
        if language == 'Korean':
            script += f"""
## 🎯 발표 마무리

📢 **마무리 스크립트**
```
이상으로 {main_topic}에 대한 발표를 마치겠습니다.

오늘 말씀드린 내용이 여러분의 업무에 도움이 되기를 바랍니다.
질문이 있으시면 언제든지 말씀해 주세요.

감사합니다.
```

---

## 📊 발표 통계
- **전체 발표 시간**: {duration}분
- **슬라이드 수**: {slide_count}개
- **평균 슬라이드당 시간**: {duration/slide_count:.1f}분
- **기술 수준**: {technical_level}
- **발표 스타일**: {script_style}
"""
        else:
            script += f"""
## 🎯 Closing Remarks

📢 **Closing Script**
```
That concludes our presentation on {main_topic}.

I hope the content we've covered today will be valuable for your work.
Please feel free to ask any questions you may have.

Thank you.
```

---

## 📊 Presentation Statistics
- **Total Duration**: {duration} minutes
- **Number of Slides**: {slide_count}
- **Average Time per Slide**: {duration/slide_count:.1f} minutes
- **Technical Level**: {technical_level}
- **Presentation Style**: {script_style}
"""
        
        logger.info(f"Generated complete presentation script: {len(script)} characters")
        return script
