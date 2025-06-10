"""AWS PPTX Presentation Script Generator - Main Streamlit Application.

This is the main entry point for the AWS SA Presentation Script Generator,
providing an 8-step wizard interface for generating professional presentation scripts.
"""

import streamlit as st
import os
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
from loguru import logger

# Configure logger
logger.add("logs/app.log", rotation="1 day", retention="7 days", level="INFO")

# Configure page
st.set_page_config(
    page_title="AWS PPTX Presentation Script Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


def analyze_powerpoint_with_claude(uploaded_file):
    """
    Analyze PowerPoint content using Claude 3.7 Sonnet multimodal capabilities
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_path = tmp_file.name
        
        # Initialize progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Load and validate PowerPoint file
        status_text.text("🔍 Loading PowerPoint file...")
        progress_bar.progress(20)
        
        # Import and initialize PowerPoint processor
        from src.processors.pptx_processor import PowerPointProcessor
        from src.analysis.multimodal_analyzer import MultimodalAnalyzer
        from src.processors.slide_image_converter import SlideImageConverter
        
        processor = PowerPointProcessor()
        analyzer = MultimodalAnalyzer()
        converter = SlideImageConverter()
        
        # Load presentation
        processor.load_presentation(temp_path)
        presentation_data = processor.process_presentation()
        
        status_text.text("🖼️ Converting slides to images...")
        progress_bar.progress(40)
        
        # Convert slides to images for multimodal analysis
        slide_images = converter.convert_presentation_to_images(temp_path)
        
        status_text.text("🧠 Analyzing content with Claude 3.7 Sonnet...")
        progress_bar.progress(60)
        
        # Prepare data for multimodal analysis
        slides_data = []
        for i, slide_content in enumerate(presentation_data.slides):
            slide_number = i + 1
            image_data = slide_images.get(slide_number, b'')
            text_content = slide_content.text_content
            slides_data.append((slide_number, image_data, text_content))
        
        # Perform multimodal analysis
        presentation_analysis = analyzer.analyze_complete_presentation(slides_data)
        
        status_text.text("📊 Generating analysis summary...")
        progress_bar.progress(80)
        
        # Generate comprehensive analysis result
        analysis_summary = analyzer.get_analysis_summary(presentation_analysis)
        
        # Extract main topic from slide analyses
        main_topic = presentation_analysis.overall_theme
        if not main_topic or main_topic == "General AWS":
            # Try to extract from first slide title
            if presentation_analysis.slide_analyses:
                first_slide = presentation_analysis.slide_analyses[0]
                main_topic = first_slide.content_summary[:50] + "..." if first_slide.content_summary else "AWS Presentation"
        
        # Create detailed slide summaries
        slide_summaries = []
        for slide_analysis in presentation_analysis.slide_analyses:
            slide_summary = {
                "slide_number": slide_analysis.slide_number,
                "title": slide_analysis.content_summary[:100] if slide_analysis.content_summary else f"Slide {slide_analysis.slide_number}",
                "main_content": slide_analysis.visual_description,
                "key_points": slide_analysis.key_concepts[:5],  # Top 5 concepts
                "aws_services": slide_analysis.aws_services,
                "technical_depth": slide_analysis.technical_depth,
                "speaking_time": slide_analysis.speaking_time_estimate,
                "slide_type": slide_analysis.slide_type
            }
            slide_summaries.append(slide_summary)
        
        # Determine technical level
        avg_depth = presentation_analysis.technical_complexity
        if avg_depth <= 2:
            technical_level = "beginner"
        elif avg_depth <= 3.5:
            technical_level = "intermediate"
        else:
            technical_level = "advanced"
        
        # Create comprehensive analysis result
        analysis_result = {
            "main_topic": main_topic,
            "slide_count": len(presentation_analysis.slide_analyses),
            "key_themes": analysis_summary["key_concepts"][:5],
            "technical_level": technical_level,
            "presentation_type": "technical_overview",
            "target_audience": "technical_teams",
            "slide_summaries": slide_summaries,
            "recommended_script_style": "technical" if avg_depth > 3 else "conversational",
            "analysis_method": "claude_multimodal_analysis",
            "aws_services_mentioned": analysis_summary["aws_services_mentioned"],
            "estimated_duration": presentation_analysis.estimated_duration,
            "flow_quality": presentation_analysis.flow_assessment,
            "recommendations": presentation_analysis.recommendations,
            "file_info": {
                "name": uploaded_file.name,
                "size": len(uploaded_file.getbuffer())
            }
        }
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis completed successfully!")
        
        st.success(f"✅ Content analysis completed with Claude 3.7 Sonnet - {len(slide_summaries)} slides analyzed")
        
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass
            
        return analysis_result
        
    except Exception as e:
        st.error(f"PowerPoint analysis failed: {str(e)}")
        logger.error(f"PowerPoint analysis error: {str(e)}")
        
        # Return fallback analysis
        return {
            "main_topic": "Analysis Failed - Using Fallback",
            "slide_count": 5,
            "key_themes": ["Technology", "Solutions", "Innovation"],
            "technical_level": "intermediate",
            "presentation_type": "technical_overview",
            "target_audience": "technical_teams",
            "slide_summaries": [
                {
                    "slide_number": 1,
                    "title": "Introduction",
                    "main_content": "Presentation introduction and overview",
                    "key_points": ["Welcome", "Agenda", "Objectives"],
                    "aws_services": [],
                    "technical_depth": 2,
                    "speaking_time": 2.0,
                    "slide_type": "title"
                }
            ],
            "recommended_script_style": "conversational",
            "analysis_method": "fallback_analysis",
            "error_message": str(e)
        }


def generate_content_aware_script(analysis_result, persona_data, presentation_params):
    """
    Generate presentation script using Claude 3.7 Sonnet for natural language generation
    """
    if not analysis_result:
        return None
    
    try:
        # Import Claude script generator
        from src.script_generation.claude_script_generator import ClaudeScriptGenerator
        
        # Initialize Claude script generator
        claude_generator = ClaudeScriptGenerator()
        
        # Create mock presentation analysis object for compatibility
        class MockPresentationAnalysis:
            def __init__(self, analysis_result):
                self.overall_theme = analysis_result['main_topic']
                self.technical_complexity = 3.0  # Default
                self.slide_analyses = []
                
                # Convert slide summaries to mock slide analyses
                for slide_summary in analysis_result.get('slide_summaries', []):
                    mock_slide = type('MockSlideAnalysis', (), {
                        'slide_number': slide_summary['slide_number'],
                        'content_summary': slide_summary['title'],
                        'visual_description': slide_summary['main_content'],
                        'key_concepts': slide_summary.get('key_points', []),
                        'aws_services': slide_summary.get('aws_services', [])
                    })()
                    self.slide_analyses.append(mock_slide)
        
        # Create mock presentation analysis
        presentation_analysis = MockPresentationAnalysis(analysis_result)
        
        # Merge analysis result settings with presentation params for comprehensive context
        enhanced_params = {
            **presentation_params,
            'technical_level': analysis_result.get('technical_level', 'intermediate'),
            'presentation_type': analysis_result.get('presentation_type', 'technical_overview'),
            'target_audience_analysis': analysis_result.get('target_audience', 'technical_teams'),
            'recommended_script_style': analysis_result.get('recommended_script_style', 'conversational'),
            'main_topic': analysis_result.get('main_topic', 'AWS Presentation'),
            'key_themes': analysis_result.get('key_themes', []),
            'aws_services_mentioned': analysis_result.get('aws_services_mentioned', [])
        }
        
        # Generate script using Claude with enhanced parameters
        script_content = claude_generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=enhanced_params,
            mcp_enhanced_services=analysis_result.get('mcp_enhanced_services')
        )
        
        logger.info(f"Generated natural script using Claude 3.7 Sonnet: {len(script_content)} characters")
        return script_content
        
    except Exception as e:
        logger.error(f"Claude script generation failed: {str(e)}")
        
        # Fallback to basic script generation
        language = presentation_params.get('language', 'English')
        duration = presentation_params.get('duration', 30)
        full_name = persona_data.get('full_name', 'SA')
        job_title = persona_data.get('job_title', 'Solutions Architect')
        target_audience = presentation_params.get('target_audience', 'Technical')
        
        main_topic = analysis_result['main_topic']
        slide_count = analysis_result['slide_count']
        
        if language == 'Korean':
            script_content = f"""# {full_name}님의 {main_topic} 프레젠테이션 스크립트

## 📋 프레젠테이션 개요
- **발표 시간**: {duration}분
- **대상 청중**: {target_audience}
- **언어**: 한국어
- **주제**: {main_topic}
- **슬라이드 수**: {slide_count}개
- **스크립트 생성**: Claude 3.7 Sonnet (Fallback)

---

## 🎤 발표 시작 인사

📢 **발표 스크립트**
```
안녕하세요, 여러분.
저는 {job_title} {full_name}입니다.

오늘은 {main_topic}에 대해 함께 알아보겠습니다.
실무에 바로 적용할 수 있는 내용들을 중심으로 말씀드리겠습니다.

시작하겠습니다.
```

## 📝 주요 내용
{main_topic}의 핵심 개념과 실제 활용 방안에 대해 다루겠습니다.

## ⚠️ 참고사항
스크립트 생성 중 오류가 발생하여 기본 템플릿을 사용했습니다.
오류: {str(e)}
"""
        else:
            script_content = f"""# {full_name}'s {main_topic} Presentation Script

## 📋 Presentation Overview
- **Duration**: {duration} minutes
- **Target Audience**: {target_audience}
- **Language**: English
- **Topic**: {main_topic}
- **Slide Count**: {slide_count}
- **Script Generation**: Claude 3.7 Sonnet (Fallback)

---

## 🎤 Opening Remarks

📢 **Presentation Script**
```
Hello everyone.
I'm {full_name}, {job_title}.

Today we'll explore {main_topic} together.
I'll focus on practical content you can apply immediately.

Let's get started.
```

## 📝 Main Content
We'll cover the key concepts of {main_topic} and practical applications.

## ⚠️ Note
An error occurred during script generation, using basic template.
Error: {str(e)}
"""
        
        return script_content


# Main Streamlit Application
def main():
    """Main application entry point."""
    
    # Header
    st.title("🎯 AWS PPTX Presentation Script Generator")
    st.markdown("**Professional presentation scripts powered by Claude 3.7 Sonnet multimodal AI**")
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'persona_data' not in st.session_state:
        st.session_state.persona_data = {}
    if 'presentation_params' not in st.session_state:
        st.session_state.presentation_params = {}
    if 'generated_script' not in st.session_state:
        st.session_state.generated_script = None
    
    # Sidebar navigation
    st.sidebar.title("🎯 Script Generator")
    st.sidebar.markdown("---")
    
    # Step navigation
    steps = [
        "📁 Upload PowerPoint",
        "🧠 AI Analysis", 
        "👤 Presenter Info",
        "⚙️ Presentation Settings",
        "📝 Generate Script",
        "📊 Review & Export"
    ]
    
    current_step = st.sidebar.radio("Steps:", steps, index=st.session_state.step-1)
    st.session_state.step = steps.index(current_step) + 1
    
    # Step 1: Upload PowerPoint
    if st.session_state.step == 1:
        st.header("📁 Step 1: Upload PowerPoint File")
        
        uploaded_file = st.file_uploader(
            "Choose a PowerPoint file",
            type=['pptx'],
            help="Upload your PowerPoint presentation for AI analysis"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📊 File size: {len(uploaded_file.getbuffer()):,} bytes")
            
            if st.button("🔍 Analyze with Claude 3.7 Sonnet", type="primary"):
                with st.spinner("Analyzing presentation..."):
                    st.session_state.analysis_result = analyze_powerpoint_with_claude(uploaded_file)
                    if st.session_state.analysis_result:
                        st.session_state.step = 2
                        st.rerun()
    
    # Step 2: AI Analysis Results
    elif st.session_state.step == 2:
        st.header("🧠 Step 2: AI Analysis Results")
        
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Analysis Summary")
                st.write(f"**Topic:** {result['main_topic']}")
                st.write(f"**Slides:** {result['slide_count']}")
                st.write(f"**Technical Level:** {result['technical_level']}")
                st.write(f"**Recommended Style:** {result['recommended_script_style']}")
                
                # Show MCP integration status
                if result.get('mcp_enhanced'):
                    st.success("🔗 AWS Documentation MCP: Active")
                    if result.get('technical_accuracy_score', 0) > 0:
                        st.write(f"**Technical Accuracy:** {result['technical_accuracy_score']:.1%}")
                else:
                    st.info("🔗 AWS Documentation MCP: Offline (using fallback)")
                
            with col2:
                st.subheader("🎯 Key Themes")
                for theme in result.get('key_themes', []):
                    st.write(f"• {theme}")
                    
                if result.get('aws_services_mentioned'):
                    st.subheader("☁️ AWS Services")
                    for service in result['aws_services_mentioned'][:5]:
                        st.write(f"• {service}")
                        
                    # Show MCP enhanced services
                    if result.get('mcp_enhanced_services'):
                        st.subheader("📚 MCP Enhanced Services")
                        for service, info in list(result['mcp_enhanced_services'].items())[:3]:
                            with st.expander(f"📖 {service}"):
                                if info.get('description'):
                                    st.write(f"**Description:** {info['description']}")
                                if info.get('use_cases'):
                                    st.write("**Use Cases:**")
                                    for use_case in info['use_cases']:
                                        st.write(f"• {use_case}")
                                if info.get('documentation_url'):
                                    st.write(f"[📖 Official Documentation]({info['documentation_url']})")
            
            # Show MCP recommendations if available
            if result.get('mcp_recommendations'):
                st.subheader("💡 AWS Best Practices (from MCP)")
                for recommendation in result['mcp_recommendations'][:3]:
                    st.info(f"💡 {recommendation}")
            
            # Allow user to modify AI analysis results
            st.subheader("🔧 Adjust Analysis Results")
            st.markdown("*Review and modify the AI analysis if needed:*")
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Allow user to override technical level
                technical_level = st.selectbox(
                    "Technical Level",
                    ["beginner", "intermediate", "advanced"],
                    index=["beginner", "intermediate", "advanced"].index(result.get('technical_level', 'intermediate')),
                    help="Adjust the technical complexity level for your audience"
                )
                
                # Allow user to override presentation type
                presentation_type = st.selectbox(
                    "Presentation Type",
                    ["technical_overview", "business_case", "deep_dive", "workshop", "demo"],
                    index=0,
                    help="Select the type of presentation"
                )
                
            with col4:
                # Allow user to override target audience
                target_audience_analysis = st.selectbox(
                    "Primary Audience",
                    ["technical_teams", "business_stakeholders", "executives", "mixed_audience"],
                    index=0,
                    help="Who is your primary audience?"
                )
                
                # Allow user to override script style
                script_style = st.selectbox(
                    "Script Style",
                    ["conversational", "technical", "formal", "educational"],
                    index=["conversational", "technical", "formal", "educational"].index(result.get('recommended_script_style', 'conversational')),
                    help="Choose the tone and style for your script"
                )
            
            # Update analysis result with user modifications
            st.session_state.analysis_result.update({
                'technical_level': technical_level,
                'presentation_type': presentation_type,
                'target_audience': target_audience_analysis,
                'recommended_script_style': script_style
            })
            
            if st.button("✅ Continue to Presenter Info", type="primary"):
                st.session_state.step = 3
                st.rerun()
        else:
            st.error("No analysis result available. Please go back to Step 1.")
    
    # Step 3: Presenter Information
    elif st.session_state.step == 3:
        st.header("👤 Step 3: Presenter Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", value=st.session_state.persona_data.get('full_name', ''))
            job_title = st.text_input("Job Title", value=st.session_state.persona_data.get('job_title', 'Solutions Architect'))
            
        with col2:
            company = st.text_input("Company", value=st.session_state.persona_data.get('company', 'AWS'))
            experience_level = st.selectbox(
                "Experience Level",
                ["Junior", "Mid-level", "Senior", "Expert"],
                index=2
            )
        
        st.session_state.persona_data = {
            'full_name': full_name,
            'job_title': job_title,
            'company': company,
            'experience_level': experience_level
        }
        
        if full_name and st.button("✅ Continue to Settings", type="primary"):
            st.session_state.step = 4
            st.rerun()
    
    # Step 4: Presentation Settings
    elif st.session_state.step == 4:
        st.header("⚙️ Step 4: Presentation Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "Presentation Language",
                ["English", "Korean"],
                help="Choose the language for your presentation script"
            )
            
            duration = st.slider(
                "Presentation Duration (minutes)",
                min_value=5,
                max_value=120,
                value=30,
                step=5
            )
            
        with col2:
            target_audience = st.selectbox(
                "Target Audience",
                ["Technical", "Business", "Mixed", "Executive"],
                help="Select your primary audience type"
            )
            
            presentation_style = st.selectbox(
                "Presentation Style",
                ["Professional", "Conversational", "Technical", "Educational"]
            )
        
        st.session_state.presentation_params = {
            'language': language,
            'duration': duration,
            'target_audience': target_audience,
            'presentation_style': presentation_style
        }
        
        if st.button("✅ Continue to Script Generation", type="primary"):
            st.session_state.step = 5
            st.rerun()
    
    # Step 5: Generate Script
    elif st.session_state.step == 5:
        st.header("📝 Step 5: Generate Script")
        
        if st.session_state.analysis_result and st.session_state.persona_data:
            
            st.subheader("🎯 Script Generation Settings")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Language:** {st.session_state.presentation_params.get('language', 'English')}")
                st.write(f"**Duration:** {st.session_state.presentation_params.get('duration', 30)} minutes")
                
            with col2:
                st.write(f"**Presenter:** {st.session_state.persona_data.get('full_name', 'N/A')}")
                st.write(f"**Audience:** {st.session_state.presentation_params.get('target_audience', 'Technical')}")
                
            with col3:
                st.write(f"**Topic:** {st.session_state.analysis_result['main_topic']}")
                st.write(f"**Slides:** {st.session_state.analysis_result['slide_count']}")
            
            if st.button("🚀 Generate Professional Script", type="primary"):
                with st.spinner("Generating your professional presentation script..."):
                    st.session_state.generated_script = generate_content_aware_script(
                        st.session_state.analysis_result,
                        st.session_state.persona_data,
                        st.session_state.presentation_params
                    )
                    if st.session_state.generated_script:
                        st.session_state.step = 6
                        st.rerun()
        else:
            st.error("Missing required data. Please complete previous steps.")
    
    # Step 6: Review & Export
    elif st.session_state.step == 6:
        st.header("📊 Step 6: Review & Export")
        
        if st.session_state.generated_script:
            st.subheader("📝 Generated Script Preview")
            
            # Show script in expandable section
            with st.expander("📖 Full Script Content", expanded=True):
                st.markdown(st.session_state.generated_script)
            
            # Export options
            st.subheader("💾 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download as markdown
                st.download_button(
                    label="📄 Download as Markdown",
                    data=st.session_state.generated_script,
                    file_name=f"presentation_script_{st.session_state.persona_data.get('full_name', 'presenter').replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            
            with col2:
                # Copy to clipboard button
                if st.button("📋 Copy to Clipboard"):
                    st.success("Script copied to clipboard!")
            
            with col3:
                # Start over button
                if st.button("🔄 Start New Script"):
                    # Reset session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            
            # Script statistics with improved time estimation
            st.subheader("📊 Script Statistics")
            
            # Calculate more accurate reading time
            script_text = st.session_state.generated_script
            word_count = len(script_text.split())
            char_count = len(script_text)
            
            # Estimate speaking time (average 150-180 words per minute)
            estimated_speaking_time = word_count / 165  # Using middle value
            target_duration = st.session_state.presentation_params.get('duration', 30)
            
            # Time difference analysis
            time_difference = estimated_speaking_time - target_duration
            time_status = "✅ 적정" if abs(time_difference) <= 2 else ("⚠️ 길음" if time_difference > 0 else "⚠️ 짧음")
            
            script_stats = {
                "Total Characters": f"{char_count:,}",
                "Total Words": f"{word_count:,}",
                "Estimated Speaking Time": f"{estimated_speaking_time:.1f} minutes",
                "Target Duration": f"{target_duration} minutes",
                "Time Status": f"{time_status} ({time_difference:+.1f}분)",
                "Language": st.session_state.presentation_params.get('language', 'English'),
                "Words per Minute": f"{word_count/target_duration:.0f} (target: 150-180)"
            }
            
            for stat, value in script_stats.items():
                st.write(f"**{stat}:** {value}")
        else:
            st.error("No script generated. Please go back to Step 5.")


if __name__ == "__main__":
    main()
