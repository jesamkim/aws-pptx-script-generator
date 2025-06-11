"""Claude-based Natural Script Generator with Prompt Caching.

This module uses Claude 3.7 Sonnet to generate natural, contextual presentation scripts
with optimized prompt caching for improved performance and cost efficiency.
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


class ClaudeScriptGeneratorCached:
    """Natural script generator using Claude 3.7 Sonnet with prompt caching."""
    
    def __init__(self, enable_caching: bool = False):  # 기본값을 False로 변경
        """Initialize Claude script generator with optional caching.
        
        Args:
            enable_caching: Whether to enable prompt caching (default: False for stability)
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
            
        if self.enable_caching and self.cache_manager:
            logger.info(f"Initialized Claude script generator with caching: {enable_caching}")
        else:
            logger.info(f"Initialized Claude script generator without caching for better stability")
    
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
            language_instruction = """CRITICAL LANGUAGE REQUIREMENT: Generate ALL content in Korean language ONLY. 

**MANDATORY Korean Generation Rules:**
- Every single word, sentence, and phrase must be in Korean
- Use natural, professional Korean suitable for business presentations
- Do NOT mix English and Korean - use Korean throughout
- Technical terms should be explained in Korean with English terms in parentheses if necessary
- All timing notes, speaker notes, and instructions must be in Korean
- Headers and formatting text must be in Korean

**Korean Style Guidelines:**
- Use varied transition expressions instead of repeating "이제" (now)
- Alternative transitions: "다음으로", "계속해서", "여기서", "한편", "또한", "그리고", "더불어"
- Avoid starting each slide with greetings - the presentation has already begun
- Use natural Korean business presentation flow
- Vary sentence structures to avoid monotony
- Use appropriate honorifics and professional language

**IMPORTANT: If you generate ANY English content when Korean is requested, this is a FAILURE. All content must be 100% Korean."""
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

**CRITICAL SLIDE FLOW RULES:**
- ONLY the first slide should include greetings and introductions
- Subsequent slides should continue naturally without repeating greetings
- Use smooth transitions between slides (e.g., "Now let's look at...", "Moving on to...", "Next, we'll explore...")
- Maintain presentation continuity throughout all slides
- Avoid redundant introductions or repeated welcomes

**Output Format:**
- Provide complete, ready-to-deliver scripts
- Include timing guidance and speaker notes
- Use natural language that flows well when spoken
- Maintain consistency with presenter's style and experience level
- Ensure each slide builds upon the previous content naturally
"""
        
        return static_content
    
    def _generate_script_header_with_timing(self,
                                           persona_data: Dict[str, str],
                                           presentation_params: Dict[str, Any],
                                           time_plan: Any,
                                           main_topic: str,
                                           language: str) -> str:
        """Generate script header with intelligent timing information.
        
        Args:
            persona_data: Presenter information
            presentation_params: Presentation parameters
            time_plan: PresentationTimePlan object
            main_topic: Main presentation topic
            language: Target language
            
        Returns:
            Formatted script header with timing details
        """
        full_name = persona_data.get('full_name', 'Presenter')
        duration = presentation_params.get('duration', 30)
        target_audience = presentation_params.get('target_audience', 'Technical')
        technical_level = presentation_params.get('technical_level', 'intermediate')
        script_style = presentation_params.get('recommended_script_style', 'conversational')
        
        # Create timing breakdown
        timing_breakdown = []
        for allocation in time_plan.slide_allocations:
            timing_breakdown.append(
                f"  - Slide {allocation.slide_number} ({allocation.slide_type}): {allocation.allocated_minutes:.1f} min"
            )
        
        timing_breakdown_text = "\n".join(timing_breakdown) if timing_breakdown else "  - Equal distribution applied"
        
        # Generate header based on language
        if language == 'Korean':
            header = f"""# {full_name}의 {main_topic} 발표 스크립트

## 📋 발표 개요
- **발표 시간**: {duration}분
- **대상 청중**: {target_audience}
- **언어**: 한국어
- **주제**: {main_topic}
- **슬라이드 수**: {len(time_plan.slide_allocations)}개
- **스크립트 생성**: Claude 3.7 Sonnet 지능형 시간 배분

## ⏰ 동적 타이밍 계획
- **콘텐츠 시간**: {time_plan.content_duration}분
- **버퍼 시간**: {time_plan.buffer_time:.1f}분
- **타이밍 전략**: {time_plan.timing_strategy}

### 슬라이드별 시간 배분:
{timing_breakdown_text}

## 🎯 발표자 가이드
- **발표 자신감**: {persona_data.get('presentation_confidence', 'Comfortable')}
- **상호작용 스타일**: {persona_data.get('interaction_style', 'Conversational')}
- **기술 수준**: {technical_level}
- **스크립트 스타일**: {script_style}

## 📢 **발표 스크립트**

"""
        else:
            header = f"""# {full_name}'s {main_topic} Presentation Script

## 📋 Presentation Overview
- **Presentation Duration**: {duration} minutes
- **Target Audience**: {target_audience}
- **Language**: English
- **Topic**: {main_topic}
- **Number of Slides**: {len(time_plan.slide_allocations)} slides
- **Script Generation**: Claude 3.7 Sonnet with Intelligent Time Allocation

## ⏰ Dynamic Timing Plan
- **Content Duration**: {time_plan.content_duration} minutes
- **Buffer Time**: {time_plan.buffer_time:.1f} minutes
- **Timing Strategy**: {time_plan.timing_strategy}

### Slide Time Allocations:
{timing_breakdown_text}

## 🎯 Presenter Guide
- **Presentation Confidence**: {persona_data.get('presentation_confidence', 'Comfortable')}
- **Interaction Style**: {persona_data.get('interaction_style', 'Conversational')}
- **Technical Level**: {technical_level}
- **Script Style**: {script_style}

## 📢 **Presentation Script**

"""
        
        return header
    
    def _invoke_claude_with_cache(self,
                                static_content: str,
                                dynamic_content: str,
                                slide_number: Optional[int] = None,
                                max_tokens: int = 4000) -> Dict[str, Any]:
        """Invoke Claude with prompt caching support using Converse API.
        
        Args:
            static_content: Static content to cache
            dynamic_content: Dynamic content for this request
            slide_number: Optional slide number for slide-specific caching
            max_tokens: Maximum tokens to generate
            
        Returns:
            Claude response
        """
        try:
            # Check cache first if caching is enabled
            if self.enable_caching and self.cache_manager:
                cached_response = self.cache_manager.get_cached_response(
                    static_content=static_content,
                    dynamic_content=dynamic_content,
                    slide_number=slide_number
                )
                if cached_response:
                    logger.info("Using cached response")
                    return cached_response
            
            # Try Converse API first
            messages = [
                {
                    "role": "user",
                    "content": [{"text": f"{static_content}\n\n{dynamic_content}"}]
                }
            ]
            
            try:
                # Use Converse API
                response = bedrock_client.client.converse(
                    modelId=self.model_id,
                    messages=messages,
                    inferenceConfig={
                        "maxTokens": max_tokens,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                )
                
                # Parse response
                response_body = {
                    "content": response["output"]["message"]["content"][0]["text"],
                    "usage": response.get("usage", {})
                }
                
                # Store in cache if caching is enabled
                if self.enable_caching and self.cache_manager:
                    self.cache_manager.store_response(
                        static_content=static_content,
                        dynamic_content=dynamic_content,
                        response=response_body,
                        slide_number=slide_number
                    )
                
                # Update cache statistics
                if self.enable_caching and self.cache_manager:
                    self.cache_manager.update_cache_stats(response_body)
                
                return response_body
                
            except Exception as converse_error:
                logger.warning(f"Converse API failed: {str(converse_error)}")
                
                # Fallback to InvokeModel API
                logger.info("Falling back to InvokeModel API...")
                
                # Prepare body for InvokeModel
                body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{static_content}\n\n{dynamic_content}"
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "anthropic_version": "bedrock-2023-05-31"
                }
                
                # Invoke Claude using InvokeModel
                response = bedrock_client.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body),
                    contentType="application/json"
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                
                # Store in cache if caching is enabled
                if self.enable_caching and self.cache_manager:
                    self.cache_manager.store_response(
                        static_content=static_content,
                        dynamic_content=dynamic_content,
                        response=response_body,
                        slide_number=slide_number
                    )
                
                # Update cache statistics
                if self.enable_caching and self.cache_manager:
                    self.cache_manager.update_cache_stats(response_body)
                
                return response_body
            
        except Exception as e:
            logger.error(f"All Claude invocation methods failed: {str(e)}")
            raise
    
    @log_execution_time
    def generate_complete_presentation_script(
        self,
        presentation_analysis: Any,
        persona_data: Dict[str, str],
        presentation_params: Dict[str, Any],
        mcp_enhanced_services: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate complete presentation script using Claude with intelligent time allocation.
        
        Args:
            presentation_analysis: Complete presentation analysis
            persona_data: Presenter information
            presentation_params: Presentation parameters
            mcp_enhanced_services: Enhanced AWS service information
            
        Returns:
            Complete natural presentation script with dynamic timing
        """
        try:
            # Extract basic parameters
            language = presentation_params.get('language', 'English')
            duration = presentation_params.get('duration', 30)
            audience = presentation_params.get('target_audience', 'Technical')
            
            # Extract enhanced parameters
            technical_level = presentation_params.get('technical_level', 'intermediate')
            presentation_type = presentation_params.get('presentation_type', 'technical_overview')
            script_style = presentation_params.get('recommended_script_style', 'conversational')
            main_topic = presentation_params.get('main_topic', presentation_analysis.overall_theme)
            key_themes = presentation_params.get('key_themes', [])
            aws_services = presentation_params.get('aws_services_mentioned', [])
            
            # Extract presentation settings
            include_qa = presentation_params.get('include_qa', True)
            qa_duration = presentation_params.get('qa_duration', 10)
            technical_depth = presentation_params.get('technical_depth', 3)
            include_timing = presentation_params.get('include_timing', True)
            include_transitions = presentation_params.get('include_transitions', True)
            include_speaker_notes = presentation_params.get('include_speaker_notes', True)
            include_qa_prep = presentation_params.get('include_qa_prep', True)
            
            # Create intelligent time allocation plan
            from src.analysis.slide_time_planner import SlideTimePlanner
            time_planner = SlideTimePlanner()
            
            time_plan = time_planner.create_time_plan(
                presentation_analysis=presentation_analysis,
                total_duration=duration,
                qa_duration=qa_duration if include_qa else 0,
                buffer_percentage=0.1  # 10% buffer time
            )
            
            logger.info(f"Created dynamic time plan: {time_plan.timing_strategy}")
            
            # Create presentation context with timing strategy
            presentation_context = f"""
Topic: {main_topic}
Total Slides: {len(presentation_analysis.slide_analyses)} slides
Presentation Duration: {duration} minutes (including Q&A {qa_duration if include_qa else 0} minutes)
Content Duration: {time_plan.content_duration} minutes
Technical Level: {technical_level} (Complexity: {technical_depth}/5)
Target Audience: {audience}
Presentation Type: {presentation_type}
Script Style: {script_style}
Key Themes: {', '.join(key_themes[:5]) if key_themes else 'General content'}
AWS Services: {', '.join(aws_services[:10]) if aws_services else 'Not applicable'}

Timing Strategy: {time_plan.timing_strategy}
Buffer Time: {time_plan.buffer_time:.1f} minutes

Presenter Settings:
- Presentation Confidence: {persona_data.get('presentation_confidence', 'Comfortable')}
- Interaction Style: {persona_data.get('interaction_style', 'Conversational')}

Script Requirements:
- Timing Guide: {'Included with dynamic allocation' if include_timing else 'Not included'}
- Slide Transitions: {'Natural transitions included' if include_transitions else 'Basic transitions only'}
- Speaker Notes: {'Detailed notes included' if include_speaker_notes else 'Basic notes only'}
- Q&A Preparation: {'Expected questions included' if include_qa_prep else 'Not included'}
"""
            
            # Get static prompt content for caching
            static_content = self._get_static_prompt_content(
                presentation_context=presentation_context,
                presenter_info=persona_data,
                language=language
            )
            
            # Safety check for None values
            if static_content is None:
                static_content = "You are a professional presentation script generator."
                logger.warning("Static content was None, using fallback")
            
            # Generate script header with timing strategy
            script_header = self._generate_script_header_with_timing(
                persona_data=persona_data,
                presentation_params=presentation_params,
                time_plan=time_plan,
                main_topic=main_topic,
                language=language
            )
            
            # Generate script for each slide with dynamic timing
            slide_scripts = []
            for i, slide_analysis in enumerate(presentation_analysis.slide_analyses):
                # Find corresponding time allocation
                slide_allocation = None
                for allocation in time_plan.slide_allocations:
                    if allocation.slide_number == slide_analysis.slide_number:
                        slide_allocation = allocation
                        break
                
                # Use fallback if allocation not found
                if not slide_allocation:
                    avg_time = time_plan.content_duration / len(presentation_analysis.slide_analyses)
                    slide_time = avg_time
                    slide_type = "content"
                    rationale = "Average allocation (fallback)"
                else:
                    slide_time = slide_allocation.allocated_minutes
                    slide_type = slide_allocation.slide_type
                    rationale = slide_allocation.rationale
                
                # Determine if this is the first slide (opening) or continuation
                is_first_slide = (i == 0)
                slide_context = "opening slide with greeting" if is_first_slide else "continuation slide without greeting"
                
                # Prepare dynamic content for this slide with intelligent timing
                timing_text = f'**⏰ Timing:** {slide_time:.1f} minutes ({rationale})' if include_timing else ''
                speaker_notes_text = f'**📝 Speaker Notes:** [Additional tips and notes for {slide_type} slide]' if include_speaker_notes else ''
                
                # Add language-specific instructions
                language_reminder = ""
                if language == 'Korean':
                    language_reminder = """
CRITICAL: This script must be written ENTIRELY in Korean. Do not use any English words or phrases except for technical terms that require clarification (use format: 한국어 용어 (English term)). All instructions, timing notes, and speaker notes must also be in Korean.
"""
                
                dynamic_content = f"""
Current Slide Information:
- Slide Number: {slide_analysis.slide_number}
- Title: {slide_analysis.content_summary[:100] if slide_analysis.content_summary else f'Slide {slide_analysis.slide_number}'}
- Content: {slide_analysis.visual_description}
- Key Points: {', '.join(slide_analysis.key_concepts[:5])}
- AWS Services: {', '.join(slide_analysis.aws_services)}
- Slide Context: {slide_context}
- Slide Type: {slide_type}
- Allocated Time: {slide_time:.1f} minutes
- Time Rationale: {rationale}
- Target Language: {language}

{language_reminder}

Generate a natural presentation script for this slide that:
1. {"Includes a professional greeting and introduction" if is_first_slide else "Continues naturally from the previous slide without greeting"}
2. Matches the presenter's style and confidence level
3. Fits the allocated time of {slide_time:.1f} minutes (adjust content depth accordingly)
4. Reflects the slide type ({slide_type}) in pacing and detail level
5. Includes timing guidance if requested ({include_timing})
6. Uses appropriate transitions ({include_transitions})
7. Adds speaker notes if requested ({include_speaker_notes})
8. Maintains consistent technical depth ({technical_depth}/5)
9. {"MUST be written entirely in Korean language" if language == 'Korean' else "Must be written in English language"}

{"IMPORTANT: This is the first slide, so include a proper greeting and introduction." if is_first_slide else "IMPORTANT: This is a continuation slide, so do NOT include greetings like '안녕하세요' or introductions. Start directly with the content transition."}

Time Allocation Guidance:
- {slide_time:.1f} minutes means {"brief, focused content" if slide_time < 1.5 else "moderate detail" if slide_time < 3.0 else "comprehensive explanation with examples"}
- Adjust script length and detail level to match the allocated time
- For {slide_type} slides, {"keep it concise and transitional" if slide_type in ["title", "agenda", "transition"] else "provide detailed technical explanation" if slide_type == "technical" else "balance overview with key details"}

Please provide the script in the following format:
### Slide {slide_analysis.slide_number}: [Title]
[Main presentation script - length appropriate for {slide_time:.1f} minutes]
{timing_text}
{speaker_notes_text}
"""
                
                # Generate script for this slide using cached prompt with slide number
                if self.enable_caching:
                    response = self._invoke_claude_with_cache(
                        static_content=static_content,
                        dynamic_content=dynamic_content,
                        slide_number=slide_analysis.slide_number
                    )
                else:
                    # Use direct invocation without caching for better stability
                    full_prompt = (static_content or "") + "\n\n" + (dynamic_content or "")
                    response = self._invoke_claude_direct(full_prompt)
                
                # Extract content from response
                slide_script = response.get('content', response.get('completion', ''))
                slide_scripts.append(slide_script)
            
            # Combine all scripts
            complete_script = script_header + "\n\n".join(slide_scripts)
            
            # Add Q&A section if requested
            if include_qa_prep:
                if language == 'Korean':
                    qa_prompt = f"""
{main_topic}에 대한 발표 내용을 바탕으로 청중이 물어볼 가능성이 높은 질문 5개와 제안 답변을 생성해주세요.
기술 수준 ({technical_level})과 청중 유형 ({audience})을 고려해주세요.
기술적 질문과 비즈니스 중심 질문을 적절히 포함해주세요.

다음 형식으로 출력해주세요:
## 💡 예상 질문 및 답변

**질문 1:** [질문]
**답변 1:** [답변]

[5개 질문까지 계속]

모든 내용을 한국어로 작성해주세요.
"""
                else:
                    qa_prompt = f"""
Based on the presentation content about {main_topic}, generate 5 likely audience questions and suggested answers.
Consider the technical level ({technical_level}) and audience type ({audience}).
Include both technical and business-focused questions as appropriate.

Format the output as:
## 💡 Expected Questions & Answers

**Q1:** [Question]
**A1:** [Answer]

[Continue for 5 questions]
"""
                
                if self.enable_caching:
                    qa_response = self._invoke_claude_with_cache(
                        static_content=static_content,
                        dynamic_content=qa_prompt
                    )
                else:
                    # Use direct invocation for Q&A
                    full_qa_prompt = (static_content or "") + "\n\n" + (qa_prompt or "")
                    qa_response = self._invoke_claude_direct(full_qa_prompt)
                complete_script += "\n\n---\n\n" + qa_response.get('content', qa_response.get('completion', ''))
            
            # Log cache performance
            if self.enable_caching and self.cache_manager:
                cache_stats = self.cache_manager.get_cache_stats()
                logger.info(f"Script generation completed with cache stats: {cache_stats}")
            else:
                logger.info("Script generation completed without caching")
            
            return complete_script
            
        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            raise
    
    def _invoke_claude_direct(self, prompt: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """Invoke Claude directly without caching for better stability.
        
        Args:
            prompt: Complete prompt text
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dictionary with content
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]
            
            # Use Converse API directly
            response = bedrock_client.client.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            )
            
            if response and "output" in response:
                content = response["output"]["message"]["content"][0]["text"]
                return {"content": content}
            
            return {"content": ""}
            
        except Exception as e:
            logger.error(f"Direct Claude invocation failed: {str(e)}")
            return {"content": ""}
    
    def _generate_script_header(self, **kwargs) -> str:
        """Generate script header with presentation overview."""
        persona_data = kwargs['persona_data']
        presentation_params = kwargs['presentation_params']
        main_topic = kwargs['main_topic']
        content_duration = kwargs['content_duration']
        qa_duration = kwargs['qa_duration']
        include_qa = kwargs['include_qa']
        include_timing = kwargs['include_timing']
        time_per_slide = kwargs['time_per_slide']
        language = kwargs['language']
        
        duration = presentation_params.get('duration', 30)
        audience = presentation_params.get('target_audience', 'Technical')
        technical_depth = presentation_params.get('technical_depth', 3)
        technical_level = presentation_params.get('technical_level', 'intermediate')
        script_style = presentation_params.get('recommended_script_style', 'conversational')
        
        if language == 'Korean':
            timing_guide_text = '- **타이밍 가이드**: 각 섹션별 시간 안내 포함' if include_timing else ''
            qa_mention = '마지막에는 질의응답 시간도 준비되어 있으니 궁금한 점이 있으시면 언제든 말씀해 주세요.' if include_qa else ''
            
            return f"""# {persona_data.get('full_name', '발표자')}님의 {main_topic} 프레젠테이션 스크립트

## 📋 프레젠테이션 개요
- **발표 시간**: {duration}분 ({content_duration}분 발표 + {qa_duration if include_qa else 0}분 Q&A)
- **대상 청중**: {audience}
- **언어**: 한국어
- **주제**: {main_topic}
- **기술 수준**: {technical_depth}/5 ({technical_level})
- **발표 스타일**: {script_style}
- **스크립트 생성**: Claude 3.7 Sonnet with Prompt Caching

## 🎯 발표자 가이드
- **발표 자신감 수준**: {persona_data.get('presentation_confidence', 'Comfortable')}
- **상호작용 스타일**: {persona_data.get('interaction_style', 'Conversational')}
- **슬라이드당 목표 시간**: {time_per_slide:.1f}분
{timing_guide_text}

---

## 🎤 발표 시작 인사

📢 **발표 스크립트**
```
안녕하세요, 여러분. 
저는 {persona_data.get('job_title', 'Solutions Architect')} {persona_data.get('full_name', '발표자')}입니다.

오늘은 {main_topic}에 대해 함께 알아보는 시간을 갖겠습니다.
{content_duration}분 동안 실무에 바로 적용할 수 있는 내용들을 중심으로 말씀드리겠습니다.
{qa_mention}

시작하겠습니다.
```

---

## 📝 슬라이드별 발표 스크립트

"""
        else:
            timing_cues_text = '- **Timing Cues**: Section timing guidance included' if include_timing else ''
            qa_mention = "We'll also have time for Q&A at the end, so please feel free to ask questions." if include_qa else ''
            
            return f"""# {persona_data.get('full_name', 'Presenter')}'s {main_topic} Presentation Script

## 📋 Presentation Overview
- **Duration**: {duration} minutes ({content_duration} min presentation + {qa_duration if include_qa else 0} min Q&A)
- **Target Audience**: {audience}
- **Language**: English
- **Topic**: {main_topic}
- **Technical Level**: {technical_depth}/5 ({technical_level})
- **Presentation Style**: {script_style}
- **Script Generation**: Claude 3.7 Sonnet with Prompt Caching

## 🎯 Presenter Guide
- **Presentation Confidence**: {persona_data.get('presentation_confidence', 'Comfortable')}
- **Interaction Style**: {persona_data.get('interaction_style', 'Conversational')}
- **Target Time per Slide**: {time_per_slide:.1f} minutes
{timing_cues_text}

---

## 🎤 Opening Remarks

📢 **Presentation Script**
```
Hello everyone.
I'm {persona_data.get('full_name', 'Presenter')}, {persona_data.get('job_title', 'Solutions Architect')}.

Today we'll explore {main_topic} together.
I'll focus on practical content you can apply immediately over the next {content_duration} minutes.
{qa_mention}

Let's get started.
```

---

## 📝 Slide-by-Slide Script

"""
    
    def get_cache_performance(self) -> Dict[str, Any]:
        """Get cache performance statistics.
        
        Returns:
            Dictionary containing cache performance metrics
        """
        if self.cache_manager:
            return self.cache_manager.get_cache_stats()
        return {"caching_disabled": True}
