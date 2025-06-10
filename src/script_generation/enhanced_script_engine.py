"""Enhanced Script Generation Engine.

This module provides advanced script generation with detailed content,
natural transitions, and professional presentation flow.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
from loguru import logger


@dataclass
class DetailedScriptSection:
    """Detailed script section for professional presentations.
    
    Attributes:
        slide_number: Slide number
        title: Section title
        opening: Opening statement for the slide
        main_content: Detailed main content (2-3 minutes worth)
        key_points: Key points with explanations
        examples: Real-world examples or use cases
        transitions: Natural transition to next slide
        speaker_notes: Detailed speaker notes
        time_allocation: Allocated time in minutes
        interaction_prompts: Audience interaction opportunities
        technical_details: Technical depth content
    """
    slide_number: int
    title: str
    opening: str
    main_content: str
    key_points: List[Dict[str, str]]
    examples: List[str]
    transitions: str
    speaker_notes: str
    time_allocation: float
    interaction_prompts: List[str]
    technical_details: List[str]


class EnhancedScriptEngine:
    """Enhanced script generation engine for professional presentations."""
    
    def __init__(self):
        """Initialize enhanced script engine."""
        self.transition_templates = {
            'Korean': [
                "이제 다음 내용으로 넘어가보겠습니다.",
                "그럼 이어서 살펴보겠습니다.",
                "다음으로는 이런 부분을 다뤄보겠습니다.",
                "이번에는 좀 더 구체적으로 알아보겠습니다.",
                "그럼 실제 사례를 통해 확인해보겠습니다."
            ],
            'English': [
                "Now let's move on to our next topic.",
                "This brings us to an important point.",
                "Let's dive deeper into this concept.",
                "Moving forward, we'll explore how this works in practice.",
                "Now, let me show you a real-world example."
            ]
        }
        
        self.opening_templates = {
            'Korean': [
                "{topic}에 대해 말씀드리겠습니다.",
                "{topic}를 살펴보겠습니다.",
                "다음으로 {topic}에 대해 알아보겠습니다.",
                "{topic}의 주요 내용을 설명드리겠습니다.",
                "이번에는 {topic}를 다뤄보겠습니다."
            ],
            'English': [
                "Let's talk about {topic}.",
                "Now I'll cover {topic}.",
                "Let's explore {topic}.",
                "I'll walk you through {topic}.",
                "Let's dive into {topic}."
            ]
        }
        
        logger.info("Initialized enhanced script engine")
    
    def generate_detailed_opening(self, language: str, slide_data: Dict[str, Any]) -> str:
        """Generate detailed opening for a slide.
        
        Args:
            language: Target language
            slide_data: Slide content data
            
        Returns:
            Natural opening statement for presentation
        """
        title = slide_data.get('title', f"Slide {slide_data['slide_number']}")
        slide_type = slide_data.get('slide_type', 'content')
        slide_number = slide_data.get('slide_number', 1)
        
        # Create natural openings based on slide type and position
        if language == 'Korean':
            if slide_number == 1 or slide_type == 'title':
                return f"안녕하세요. 오늘은 {title}에 대해 말씀드리겠습니다."
            elif slide_type == 'agenda':
                return "오늘 다룰 주요 내용들을 살펴보겠습니다."
            elif slide_type == 'architecture':
                return f"{title} 아키텍처를 살펴보겠습니다."
            elif slide_type == 'demo':
                return f"실제 {title} 데모를 보여드리겠습니다."
            elif slide_type == 'comparison':
                return f"{title} 비교 분석을 해보겠습니다."
            elif slide_type == 'summary':
                return "지금까지의 내용을 정리해보겠습니다."
            else:
                # For content slides, use natural transitions
                natural_openings = [
                    f"{title}에 대해 말씀드리겠습니다.",
                    f"다음으로 {title}를 살펴보겠습니다.",
                    f"{title}의 주요 특징들을 알아보겠습니다.",
                    f"{title}에 대해 자세히 설명드리겠습니다."
                ]
                # Use slide number to select consistent opening
                return natural_openings[slide_number % len(natural_openings)]
        else:
            if slide_number == 1 or slide_type == 'title':
                return f"Hello everyone. Today I'll be talking about {title}."
            elif slide_type == 'agenda':
                return "Let's look at what we'll be covering today."
            elif slide_type == 'architecture':
                return f"Let's examine the {title} architecture."
            elif slide_type == 'demo':
                return f"Now I'll show you a {title} demonstration."
            elif slide_type == 'comparison':
                return f"Let's compare {title}."
            elif slide_type == 'summary':
                return "Let me summarize what we've covered."
            else:
                # For content slides, use natural transitions
                natural_openings = [
                    f"Let's talk about {title}.",
                    f"Now I'll cover {title}.",
                    f"Let's explore {title}.",
                    f"I'll walk you through {title}."
                ]
                # Use slide number to select consistent opening
                return natural_openings[slide_number % len(natural_openings)]
    
    def generate_main_content(
        self,
        language: str,
        slide_data: Dict[str, Any],
        duration: float
    ) -> str:
        """Generate detailed main content for a slide.
        
        Args:
            language: Target language
            slide_data: Slide content data
            duration: Target duration in minutes
            
        Returns:
            Detailed main content (2-3 minutes worth) in consistent language
        """
        main_content = slide_data.get('main_content', '')
        key_points = slide_data.get('key_points', [])
        aws_services = slide_data.get('aws_services', [])
        technical_depth = slide_data.get('technical_depth', 3)
        
        # Clean main_content to remove English mixed with Korean
        if language == 'Korean':
            # Filter out English content and create Korean-only content
            content = f"""
{slide_data.get('title', '주요 내용')}에 대해 구체적으로 설명드리겠습니다.

먼저 기본적인 개념부터 시작해서, 실제 활용 방법까지 
단계별로 알아보겠습니다.

특히 중요한 점은 이 기술이 어떻게 여러분의 업무 환경에서 
실질적인 도움이 될 수 있는지입니다.

실제 사례를 통해 살펴보면, 많은 기업들이 이런 접근 방식을 통해 
상당한 성과를 거두고 있습니다.
"""
            
            if aws_services:
                korean_services = []
                for service in aws_services[:3]:
                    if 'Amazon' in service:
                        korean_services.append(service.replace('Amazon ', '아마존 '))
                    elif 'AWS' in service:
                        korean_services.append(service.replace('AWS ', 'AWS '))
                    else:
                        korean_services.append(service)
                
                content += f"\n특히 이번 내용과 관련된 주요 서비스로는 {', '.join(korean_services)} 등이 있습니다."
                
        else:
            content = f"""
Let me walk you through {slide_data.get('title', 'this topic')} in detail.

I'll start with the fundamental concepts and then move on to 
practical implementation approaches.

The key thing to understand is how this technology can provide 
real value in your specific work environment.

Looking at real-world implementations, many organizations have achieved 
significant results using this approach.
"""
            
            if aws_services:
                content += f"\nThe key AWS services relevant to this topic include {', '.join(aws_services[:3])} and others."
        
        # Adjust content length based on duration
        if duration > 3:
            # Add more detailed explanations for longer durations
            if language == 'Korean':
                content += """

구체적인 구현 방법을 살펴보면, 몇 가지 핵심적인 단계가 있습니다.

첫째, 현재 상황을 정확히 파악하는 것이 중요합니다.
둘째, 목표를 명확히 설정해야 합니다.
셋째, 단계별 실행 계획을 수립합니다.

이런 체계적인 접근을 통해 성공적인 결과를 얻을 수 있습니다."""
            else:
                content += """

Looking at the implementation approach, there are several key steps:

First, it's important to assess your current situation accurately.
Second, you need to set clear objectives.
Third, develop a phased implementation plan.

This systematic approach will help you achieve successful outcomes."""
        
        return content.strip()
    
    def generate_key_points_with_explanations(
        self,
        language: str,
        key_points: List[str],
        slide_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate key points with detailed explanations.
        
        Args:
            language: Target language
            key_points: List of key points
            slide_data: Slide content data
            
        Returns:
            List of key points with explanations
        """
        detailed_points = []
        
        for i, point in enumerate(key_points[:5]):  # Limit to 5 key points
            if language == 'Korean':
                explanation = f"""
이 포인트는 전체 솔루션에서 핵심적인 역할을 합니다.
구체적으로는 {point.lower()}를 통해 실질적인 가치를 창출할 수 있으며,
이는 비즈니스 목표 달성에 직접적으로 기여합니다.
"""
            else:
                explanation = f"""
This point plays a crucial role in the overall solution.
Specifically, {point.lower()} enables tangible value creation
and directly contributes to achieving business objectives.
"""
            
            detailed_points.append({
                'point': point,
                'explanation': explanation.strip()
            })
        
        return detailed_points
    
    def generate_examples(
        self,
        language: str,
        slide_data: Dict[str, Any]
    ) -> List[str]:
        """Generate relevant examples for the slide content.
        
        Args:
            language: Target language
            slide_data: Slide content data
            
        Returns:
            List of relevant examples
        """
        aws_services = slide_data.get('aws_services', [])
        technical_depth = slide_data.get('technical_depth', 3)
        slide_type = slide_data.get('slide_type', 'content')
        
        examples = []
        
        if language == 'Korean':
            if aws_services:
                examples.append(f"""
실제 사례로, 한 글로벌 기업에서는 {aws_services[0] if aws_services else 'AWS 서비스'}를 
활용하여 기존 시스템을 현대화했습니다. 
그 결과 처리 속도가 3배 향상되고 운영 비용은 40% 절감되었습니다.
""")
            
            if technical_depth >= 4:
                examples.append("""
기술적인 관점에서 보면, 이 아키텍처는 마이크로서비스 패턴을 적용하여
각 컴포넌트의 독립성을 보장하면서도 전체적인 일관성을 유지합니다.
""")
        else:
            if aws_services:
                examples.append(f"""
For example, a global enterprise leveraged {aws_services[0] if aws_services else 'AWS services'} 
to modernize their legacy systems.
The result was a 3x improvement in processing speed and 40% reduction in operational costs.
""")
            
            if technical_depth >= 4:
                examples.append("""
From a technical perspective, this architecture applies microservices patterns
to ensure component independence while maintaining overall system consistency.
""")
        
        return [ex.strip() for ex in examples if ex.strip()]
    
    def generate_natural_transition(
        self,
        language: str,
        current_slide: Dict[str, Any],
        next_slide: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate natural transition to next slide.
        
        Args:
            language: Target language
            current_slide: Current slide data
            next_slide: Next slide data (optional)
            
        Returns:
            Natural transition text
        """
        templates = self.transition_templates.get(language, self.transition_templates['English'])
        
        if next_slide:
            next_title = next_slide.get('title', 'next topic')
            if language == 'Korean':
                return f"이제 {next_title}에 대해 알아보겠습니다."
            else:
                return f"Now let's explore {next_title}."
        
        # Default transition
        return templates[0]
    
    def generate_speaker_notes(
        self,
        language: str,
        slide_data: Dict[str, Any],
        duration: float
    ) -> str:
        """Generate detailed speaker notes.
        
        Args:
            language: Target language
            slide_data: Slide content data
            duration: Target duration
            
        Returns:
            Detailed speaker notes
        """
        if language == 'Korean':
            notes = f"""
**발표자 노트:**

• 예상 소요 시간: {round(duration, 1)}분
• 핵심 메시지: {slide_data.get('title', '주요 내용')} 전달
• 청중 참여: 질문이나 의견 유도
• 시각 자료: 슬라이드의 차트/다이어그램 적극 활용
• 속도 조절: 복잡한 내용은 천천히, 간단한 내용은 빠르게
• 체크 포인트: 중간중간 청중의 이해도 확인

**주의사항:**
- 전문 용어 사용 시 간단한 설명 추가
- 실제 경험이나 사례 언급으로 신뢰성 확보
- 다음 슬라이드로의 자연스러운 연결 준비
"""
        else:
            notes = f"""
**Speaker Notes:**

• Estimated time: {round(duration, 1)} minutes
• Key message: Deliver {slide_data.get('title', 'main content')}
• Audience engagement: Encourage questions and feedback
• Visual aids: Actively reference charts/diagrams on slide
• Pacing: Slow down for complex topics, speed up for simple ones
• Check points: Verify audience understanding throughout

**Important reminders:**
- Provide brief explanations for technical terms
- Share real experiences or examples for credibility
- Prepare smooth transition to next slide
"""
        
        return notes.strip()
    
    def generate_detailed_script_section(
        self,
        language: str,
        slide_data: Dict[str, Any],
        duration: float,
        next_slide: Optional[Dict[str, Any]] = None
    ) -> DetailedScriptSection:
        """Generate detailed script section for a slide.
        
        Args:
            language: Target language
            slide_data: Slide content data
            duration: Target duration
            next_slide: Next slide data for transitions
            
        Returns:
            DetailedScriptSection object
        """
        opening = self.generate_detailed_opening(language, slide_data)
        main_content = self.generate_main_content(language, slide_data, duration)
        key_points = self.generate_key_points_with_explanations(
            language, slide_data.get('key_points', []), slide_data
        )
        examples = self.generate_examples(language, slide_data)
        transitions = self.generate_natural_transition(language, slide_data, next_slide)
        speaker_notes = self.generate_speaker_notes(language, slide_data, duration)
        
        # Generate interaction prompts
        if language == 'Korean':
            interaction_prompts = [
                "이 부분에 대해 질문이 있으시면 언제든 말씀해 주세요.",
                "실제 경험해 보신 분이 계시다면 공유해 주시면 좋겠습니다.",
                "이해가 안 되는 부분이 있으시면 바로 말씀해 주세요."
            ]
        else:
            interaction_prompts = [
                "Please feel free to ask questions about this topic.",
                "If anyone has hands-on experience with this, please share.",
                "Let me know if anything needs clarification."
            ]
        
        # Generate technical details based on depth
        technical_details = []
        tech_depth = slide_data.get('technical_depth', 3)
        if tech_depth >= 4:
            if language == 'Korean':
                technical_details = [
                    "기술적 구현 세부사항",
                    "성능 최적화 고려사항",
                    "보안 및 컴플라이언스 요구사항"
                ]
            else:
                technical_details = [
                    "Technical implementation details",
                    "Performance optimization considerations",
                    "Security and compliance requirements"
                ]
        
        return DetailedScriptSection(
            slide_number=slide_data['slide_number'],
            title=slide_data.get('title', f"Slide {slide_data['slide_number']}"),
            opening=opening,
            main_content=main_content,
            key_points=key_points,
            examples=examples,
            transitions=transitions,
            speaker_notes=speaker_notes,
            time_allocation=duration,
            interaction_prompts=interaction_prompts,
            technical_details=technical_details
        )
    
    def format_detailed_script_section(
        self,
        language: str,
        section: DetailedScriptSection
    ) -> str:
        """Format detailed script section as markdown.
        
        Args:
            language: Target language
            section: DetailedScriptSection object
            
        Returns:
            Formatted markdown script
        """
        if language == 'Korean':
            script = f"""### 슬라이드 {section.slide_number}: {section.title}

📢 **발표 스크립트** ({section.time_allocation:.1f}분)
```
{section.opening}

{section.main_content}

{section.transitions}
```

---

📋 **발표자 참고사항**

**핵심 포인트:**"""
            
            for point_data in section.key_points:
                script += f"""
• {point_data['point']}
  - {point_data['explanation']}"""
            
            if section.examples:
                script += "\n\n**실제 사례:**"
                for example in section.examples:
                    script += f"\n• {example}"
            
            script += "\n\n**발표자 노트:**"
            for line in section.speaker_notes.split('\n'):
                if line.strip():
                    script += f"\n• {line.strip()}"
            
            if section.technical_details:
                script += "\n\n**기술 세부사항:**"
                for detail in section.technical_details:
                    script += f"\n• {detail}"
            
            if section.interaction_prompts:
                script += "\n\n**청중 상호작용:**"
                for prompt in section.interaction_prompts:
                    script += f"\n• {prompt}"
            
        else:
            script = f"""### Slide {section.slide_number}: {section.title}

📢 **Presentation Script** ({section.time_allocation:.1f} minutes)
```
{section.opening}

{section.main_content}

{section.transitions}
```

---

📋 **Speaker Reference**

**Key Points:**"""
            
            for point_data in section.key_points:
                script += f"""
• {point_data['point']}
  - {point_data['explanation']}"""
            
            if section.examples:
                script += "\n\n**Examples:**"
                for example in section.examples:
                    script += f"\n• {example}"
            
            script += "\n\n**Speaker Notes:**"
            for line in section.speaker_notes.split('\n'):
                if line.strip():
                    script += f"\n• {line.strip()}"
            
            if section.technical_details:
                script += "\n\n**Technical Details:**"
                for detail in section.technical_details:
                    script += f"\n• {detail}"
            
            if section.interaction_prompts:
                script += "\n\n**Audience Interaction:**"
                for prompt in section.interaction_prompts:
                    script += f"\n• {prompt}"
        
        return script
