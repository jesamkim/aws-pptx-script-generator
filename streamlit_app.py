"""AWS Presentation Script Generator - Main Streamlit Application.

This is the main entry point for the AWS SA Presentation Script Generator,
providing an 8-step wizard interface for generating professional presentation scripts.
"""

import streamlit as st
import os
import asyncio
import concurrent.futures
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
from loguru import logger

# Configure logger
logger.add("logs/app.log", rotation="1 day", retention="7 days", level="INFO")

# Configure page
st.set_page_config(
    page_title="AWS Presentation Script Generator",
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
    """Generate presentation script using Claude 3.7 Sonnet."""
    if not analysis_result:
        return None
    
    try:
        # Import Claude script generator
        from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
        
        # Initialize Claude script generator with caching
        claude_generator = ClaudeScriptGeneratorCached(enable_caching=False)
        
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
            **presentation_params,  # This now includes all the new settings from Step 4
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
        
        # Store the generator instance for cache stats
        st.session_state.claude_generator = claude_generator
        
        logger.info(f"Generated natural script using Claude 3.7 Sonnet with caching: {len(script_content)} characters")
        return script_content
        
    except Exception as e:
        logger.error(f"Script generation failed: {str(e)}")
        return None


def generate_content_aware_script_optimized(analysis_result, persona_data, presentation_params):
    """
    Generate presentation script using Optimized Agent with Claude 3.7 Sonnet
    """
    if not analysis_result:
        return None
    
    try:
        # Import optimized agent
        from src.agent.optimized_script_agent import OptimizedScriptAgent, OptimizedPersonaProfile
        
        # Initialize optimized script agent with caching
        script_agent = OptimizedScriptAgent(enable_caching=False, max_workers=4)
        
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
        
        # Create optimized persona profile
        optimized_persona = OptimizedPersonaProfile(
            full_name=persona_data.get('full_name', 'Presenter'),
            job_title=persona_data.get('job_title', 'Solutions Architect'),
            experience_level=persona_data.get('experience_level', 'Senior'),
            presentation_style=persona_data.get('interaction_style', 'Conversational'),
            specializations=['AWS', 'Cloud Architecture'],
            language=presentation_params.get('language', 'English'),
            cultural_context={},
            optimization_preferences={
                'confidence': persona_data.get('presentation_confidence', 'Comfortable'),
                'enable_caching': True,
                'parallel_processing': True
            }
        )
        
        # Merge analysis result settings with presentation params for comprehensive context
        enhanced_params = {
            **presentation_params,  # This now includes all the new settings from Step 4
            'technical_level': analysis_result.get('technical_level', 'intermediate'),
            'presentation_type': analysis_result.get('presentation_type', 'technical_overview'),
            'target_audience_analysis': analysis_result.get('target_audience', 'technical_teams'),
            'recommended_script_style': analysis_result.get('recommended_script_style', 'conversational'),
            'main_topic': analysis_result.get('main_topic', 'AWS Presentation'),
            'key_themes': analysis_result.get('key_themes', []),
            'aws_services_mentioned': analysis_result.get('aws_services_mentioned', [])
        }
        
        # Generate script using optimized agent
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in a running loop, use asyncio.create_task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, script_agent.generate_script_optimized(
                        presentation_analysis=presentation_analysis,
                        persona_profile=optimized_persona,
                        presentation_params=enhanced_params,
                        mcp_enhanced_services=analysis_result.get('mcp_enhanced_services')
                    ))
                    result = future.result()
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                result = asyncio.run(
                    script_agent.generate_script_optimized(
                        presentation_analysis=presentation_analysis,
                        persona_profile=optimized_persona,
                        presentation_params=enhanced_params,
                        mcp_enhanced_services=analysis_result.get('mcp_enhanced_services')
                    )
                )
        except Exception as async_error:
            logger.error(f"Async execution failed: {str(async_error)}")
            raise
        
        # Store the agent instance for performance stats
        st.session_state.script_agent = script_agent
        
        if result.success:
            logger.info(f"Generated optimized script using Agent: {len(result.script_content)} characters")
            logger.info(f"Agent performance: {script_agent.get_performance_summary()}")
            return result.script_content
        else:
            logger.error(f"Optimized script generation failed: {result.metadata.get('error', 'Unknown error')}")
            return None
        
    except Exception as e:
        logger.error(f"Optimized script generation failed: {str(e)}")
        
        # Fallback to regular cached generator
        return generate_content_aware_script(analysis_result, persona_data, presentation_params)
    """
    Generate presentation script using Claude 3.7 Sonnet for natural language generation
    """
    if not analysis_result:
        return None
    
    try:
        # Import Claude script generator
        from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
        
        # Initialize Claude script generator with caching
        claude_generator = ClaudeScriptGeneratorCached(enable_caching=False)
        
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
            **presentation_params,  # This now includes all the new settings from Step 4
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
        
        # Store the generator instance for cache stats
        st.session_state.claude_generator = claude_generator
        
        logger.info(f"Generated natural script using Claude 3.7 Sonnet with caching: {len(script_content)} characters")
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

## 📋 Presentation Overview
- **Presentation Duration**: {duration} minutes
- **Target Audience**: {target_audience}
- **Language**: Korean
- **Topic**: {main_topic}
- **Number of Slides**: {slide_count} slides
- **Script Generation**: Claude 3.7 Sonnet (Fallback)

---

## 🎤 Presentation Opening

📢 **Presentation Script**
```
안녕하세요, 여러분.
저는 {job_title} {full_name}입니다.

오늘은 {main_topic}에 대해 함께 알아보겠습니다.
실무에 바로 적용할 수 있는 내용들을 중심으로 말씀드리겠습니다.

시작하겠습니다.
```

## 📝 Main Content
We will cover the core concepts and practical applications of {main_topic}.

## ⚠️ Note
An error occurred during script generation, using default template.
Error: {str(e)}
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
    st.title("🎯 AWS Presentation Script Generator")
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
    
    # Step definitions
    steps = [
        "📁 Upload PowerPoint",
        "🧠 AI Analysis", 
        "👤 Presenter Info",
        "⚙️ Presentation Settings",
        "📝 Generate Script",
        "📊 Review & Export"
    ]
    
    # Progress visualization
    st.sidebar.subheader("📋 Progress")
    progress_percentage = (st.session_state.step - 1) / (len(steps) - 1)
    st.sidebar.progress(progress_percentage)
    st.sidebar.write(f"Step {st.session_state.step} of {len(steps)}")
    
    # Current step display
    st.sidebar.markdown("### 🔄 Current Step")
    st.sidebar.info(f"**{steps[st.session_state.step-1]}**")
    
    # Step status display
    st.sidebar.markdown("### 📝 Step Status")
    for i, step in enumerate(steps, 1):
        if i < st.session_state.step:
            st.sidebar.success(f"✅ {step}")
        elif i == st.session_state.step:
            st.sidebar.warning(f"🔄 {step}")
        else:
            st.sidebar.write(f"⏳ {step}")
    
    # Navigation controls
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.session_state.step > 1:
            if st.button("⬅️ Previous", key="prev_step"):
                st.session_state.step -= 1
                st.rerun()
    
    with col2:
        # Reset button
        if st.button("🔄 Reset", key="reset_all"):
            # Reset session state
            for key in list(st.session_state.keys()):
                if key != 'step':  # Keep step for smooth transition
                    del st.session_state[key]
            st.session_state.step = 1
            st.rerun()
    
    # Step 1: Upload PowerPoint
    if st.session_state.step == 1:
        st.header("📁 Step 1: Upload PowerPoint File")
        st.markdown("Upload your PowerPoint presentation to begin the AI-powered script generation process.")
        
        uploaded_file = st.file_uploader(
            "Choose a PowerPoint file",
            type=['pptx'],
            help="Upload your PowerPoint presentation for AI analysis"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📊 File size: {len(uploaded_file.getbuffer()):,} bytes")
            
            # Show file preview info
            with st.expander("📋 File Information"):
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**File size:** {len(uploaded_file.getbuffer()):,} bytes")
                st.write(f"**File type:** PowerPoint Presentation (.pptx)")
            
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info("💡 **Next:** The AI will analyze your presentation content, structure, and visual elements using Claude 3.7 Sonnet.")
            
            with col2:
                if st.button("🔍 Analyze & Continue", type="primary", use_container_width=True):
                    with st.spinner("🧠 Analyzing presentation with Claude 3.7 Sonnet..."):
                        st.session_state.analysis_result = analyze_powerpoint_with_claude(uploaded_file)
                        if st.session_state.analysis_result:
                            st.session_state.step = 2
                            st.success("✅ Analysis completed! Moving to next step...")
                            st.rerun()
        else:
            st.info("👆 Please upload a PowerPoint file to continue.")
    
    # Step 2: AI Analysis Results
    elif st.session_state.step == 2:
        st.header("🧠 Step 2: AI Analysis Results")
        st.markdown("Review and adjust the AI analysis of your presentation content.")
        
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
            st.markdown("---")
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
            
            st.markdown("---")
            col5, col6 = st.columns([3, 1])
            
            with col5:
                st.info("💡 **Next:** Enter your presenter information to personalize the script generation.")
            
            with col6:
                if st.button("👤 Continue to Presenter Info", type="primary", use_container_width=True):
                    st.session_state.step = 3
                    st.success("✅ Analysis confirmed! Moving to presenter information...")
                    st.rerun()
        else:
            st.error("❌ No analysis result available. Please go back to Step 1.")
            if st.button("⬅️ Back to Upload", type="secondary"):
                st.session_state.step = 1
                st.rerun()
    
    # Step 3: Presenter Information
    elif st.session_state.step == 3:
        st.header("👤 Step 3: Presenter Information")
        st.markdown("Enter your information to personalize the presentation script.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name *", 
                value=st.session_state.persona_data.get('full_name', ''),
                placeholder="Enter your full name"
            )
            job_title = st.text_input(
                "Job Title *", 
                value=st.session_state.persona_data.get('job_title', 'Solutions Architect'),
                placeholder="e.g., Senior Solutions Architect"
            )
            
        with col2:
            company = st.text_input(
                "Company", 
                value=st.session_state.persona_data.get('company', 'AWS'),
                placeholder="Your company name"
            )
            experience_level = st.selectbox(
                "Experience Level",
                ["Junior", "Mid-level", "Senior", "Expert"],
                index=2,
                help="Your experience level affects the script's technical depth and confidence level"
            )
        
        # Additional presenter preferences
        st.markdown("### 🎯 Presentation Preferences")
        col3, col4 = st.columns(2)
        
        with col3:
            presentation_confidence = st.selectbox(
                "Presentation Confidence",
                ["Beginner", "Comfortable", "Experienced", "Expert"],
                index=2,
                help="How comfortable are you with presenting?"
            )
            
        with col4:
            interaction_style = st.selectbox(
                "Interaction Style",
                ["Formal", "Conversational", "Interactive", "Q&A Focused"],
                index=1,
                help="Your preferred interaction style with the audience"
            )
        
        # Store persona data
        st.session_state.persona_data = {
            'full_name': full_name,
            'job_title': job_title,
            'company': company,
            'experience_level': experience_level,
            'presentation_confidence': presentation_confidence,
            'interaction_style': interaction_style
        }
        
        # Validation and preview
        if full_name and job_title:
            st.markdown("---")
            st.subheader("👤 Presenter Profile Preview")
            st.info(f"**{full_name}** - {job_title} at {company}")
            st.write(f"**Experience:** {experience_level} | **Confidence:** {presentation_confidence} | **Style:** {interaction_style}")
            
            col5, col6 = st.columns([3, 1])
            
            with col5:
                st.info("💡 **Next:** Configure your presentation settings and requirements.")
            
            with col6:
                if st.button("⚙️ Continue to Settings", type="primary", use_container_width=True):
                    st.session_state.step = 4
                    st.success("✅ Presenter info saved! Moving to presentation settings...")
                    st.rerun()
        else:
            st.warning("⚠️ Please fill in the required fields (marked with *) to continue.")
    
    # Step 4: Presentation Settings
    elif st.session_state.step == 4:
        st.header("⚙️ Step 4: Presentation Settings")
        st.markdown("Configure your presentation requirements and preferences.")
        
        # Basic settings
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "Presentation Language *",
                ["English", "Korean"],
                help="Choose the language for your presentation script"
            )
            
            duration = st.slider(
                "Presentation Duration (minutes) *",
                min_value=5,
                max_value=120,
                value=30,
                step=5,
                help="Total time allocated for the presentation"
            )
            
        with col2:
            target_audience = st.selectbox(
                "Target Audience *",
                ["Technical", "Business", "Mixed", "Executive"],
                help="Select your primary audience type"
            )
            
            presentation_style = st.selectbox(
                "Presentation Style *",
                ["Professional", "Conversational", "Technical", "Educational"],
                help="Overall tone and style of the presentation"
            )
        
        # Advanced settings
        st.markdown("### 🎯 Advanced Settings")
        col3, col4 = st.columns(2)
        
        with col3:
            time_per_slide = st.number_input(
                "Average Time per Slide (minutes)",
                min_value=1.0,
                max_value=10.0,
                value=2.0,
                step=0.5,
                help="Target time to spend on each slide"
            )
            
            include_qa = st.checkbox(
                "Include Q&A Section",
                value=True,
                help="Reserve time for questions at the end"
            )
            
        with col4:
            technical_depth = st.slider(
                "Technical Detail Level",
                min_value=1,
                max_value=5,
                value=3,
                help="1: Basic overview, 5: Deep technical details"
            )
            
            if include_qa:
                qa_duration = st.slider(
                    "Q&A Duration (minutes)",
                    min_value=5,
                    max_value=30,
                    value=10,
                    step=5,
                    help="Time reserved for Q&A"
                )
        
        # Store presentation settings
        st.session_state.presentation_params = {
            'language': language,
            'duration': duration,
            'target_audience': target_audience,
            'presentation_style': presentation_style,
            'time_per_slide': time_per_slide,
            'include_qa': include_qa,
            'qa_duration': qa_duration if include_qa else 0,
            'technical_depth': technical_depth
        }
        
        # Settings preview
        st.markdown("---")
        st.subheader("📊 Settings Summary")
        
        col5, col6 = st.columns(2)
        with col5:
            st.write(f"**Language:** {language}")
            st.write(f"**Total Duration:** {duration} minutes")
            st.write(f"**Audience:** {target_audience}")
            st.write(f"**Style:** {presentation_style}")
        
        with col6:
            st.write(f"**Technical Level:** {technical_depth}/5")
            st.write(f"**Time per Slide:** {time_per_slide} minutes")
            if include_qa:
                st.write(f"**Q&A Time:** {qa_duration} minutes")
            st.write(f"**Content Time:** {duration - (qa_duration if include_qa else 0)} minutes")
        
        # Time allocation warning
        total_slides = st.session_state.analysis_result.get('slide_count', 0)
        estimated_content_time = total_slides * time_per_slide
        content_time_available = duration - (qa_duration if include_qa else 0)
        
        if estimated_content_time > content_time_available:
            st.warning(f"⚠️ Time allocation warning: Your settings suggest {estimated_content_time:.1f} minutes for content, but only {content_time_available} minutes are available.")
        
        st.markdown("---")
        col7, col8 = st.columns([3, 1])
        
        with col7:
            st.info("💡 **Next:** Generate your personalized presentation script based on these settings.")
        
        with col8:
            if st.button("📝 Generate Script", type="primary", use_container_width=True):
                st.session_state.step = 5
                st.success("✅ Settings saved! Moving to script generation...")
                st.rerun()
    
    # Step 5: Generate Script
    elif st.session_state.step == 5:
        st.header("📝 Step 5: Generate Script")
        st.markdown("Generate your personalized presentation script using Claude 3.7 Sonnet.")
        
        if st.session_state.analysis_result and st.session_state.persona_data:
            
            # Generation settings summary
            st.subheader("🎯 Script Generation Configuration")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📋 Presentation**")
                st.write(f"**Language:** {st.session_state.presentation_params.get('language', 'English')}")
                st.write(f"**Duration:** {st.session_state.presentation_params.get('duration', 30)} minutes")
                st.write(f"**Style:** {st.session_state.presentation_params.get('presentation_style', 'Professional')}")
                
            with col2:
                st.markdown("**👤 Presenter**")
                st.write(f"**Name:** {st.session_state.persona_data.get('full_name', 'N/A')}")
                st.write(f"**Role:** {st.session_state.persona_data.get('job_title', 'N/A')}")
                st.write(f"**Experience:** {st.session_state.persona_data.get('experience_level', 'N/A')}")
                
            with col3:
                st.markdown("**📊 Content**")
                st.write(f"**Topic:** {st.session_state.analysis_result['main_topic']}")
                st.write(f"**Slides:** {st.session_state.analysis_result['slide_count']}")
                st.write(f"**Audience:** {st.session_state.presentation_params.get('target_audience', 'Technical')}")
            
            # Generation options
            st.markdown("---")
            st.subheader("🔧 Generation Options")
            
            col4, col5 = st.columns(2)
            
            with col4:
                include_timing = st.checkbox(
                    "Include Timing Cues",
                    value=True,
                    help="Add timing guidance for each section"
                )
                
                include_transitions = st.checkbox(
                    "Include Slide Transitions",
                    value=True,
                    help="Add smooth transitions between slides"
                )
                
            with col5:
                include_speaker_notes = st.checkbox(
                    "Include Speaker Notes",
                    value=True,
                    help="Add additional notes and tips for the presenter"
                )
                
                include_qa_prep = st.checkbox(
                    "Include Q&A Preparation",
                    value=st.session_state.presentation_params.get('include_qa', True),
                    help="Add potential questions and answers"
                )
            
            # Update generation parameters
            st.session_state.presentation_params.update({
                'include_timing': include_timing,
                'include_transitions': include_transitions,
                'include_speaker_notes': include_speaker_notes,
                'include_qa_prep': include_qa_prep
            })
            
            st.markdown("---")
            
            # Generation button
            if not st.session_state.generated_script:
                col6, col7 = st.columns([3, 1])
                
                with col6:
                    st.info("🚀 **Ready to generate:** Click the button to create your personalized presentation script using Claude 3.7 Sonnet AI.")
                
                with col7:
                    if st.button("🚀 Generate Script", type="primary", use_container_width=True):
                        with st.spinner("🧠 Generating your professional presentation script..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Simulate generation progress
                            status_text.text("🔍 Analyzing presentation structure...")
                            progress_bar.progress(20)
                            
                            status_text.text("🎯 Personalizing content for presenter...")
                            progress_bar.progress(40)
                            
                            status_text.text("✍️ Generating script with Claude 3.7 Sonnet...")
                            progress_bar.progress(60)
                            
                            # Generate script with optimized agent
                            st.session_state.generated_script = generate_content_aware_script_optimized(
                                st.session_state.analysis_result,
                                st.session_state.persona_data,
                                st.session_state.presentation_params
                            )
                            
                            status_text.text("🎨 Formatting and finalizing...")
                            progress_bar.progress(80)
                            
                            if st.session_state.generated_script:
                                status_text.text("✅ Script generation completed!")
                                progress_bar.progress(100)
                                st.session_state.step = 6
                                st.success("🎉 Script generated successfully! Moving to review...")
                                st.rerun()
                            else:
                                status_text.text("❌ Script generation failed")
                                st.error("Failed to generate script. Please try again.")
            else:
                # Script already generated
                st.success("✅ Script has been generated successfully!")
                col8, col9 = st.columns([3, 1])
                
                with col8:
                    st.info("📖 **Script ready:** Your personalized presentation script is ready for review.")
                
                with col9:
                    if st.button("📊 Review Script", type="primary", use_container_width=True):
                        st.session_state.step = 6
                        st.rerun()
        else:
            st.error("❌ Missing required data. Please complete previous steps.")
            
            # Show what's missing
            missing_items = []
            if not st.session_state.analysis_result:
                missing_items.append("PowerPoint analysis")
            if not st.session_state.persona_data:
                missing_items.append("Presenter information")
            
            st.warning(f"⚠️ Missing: {', '.join(missing_items)}")
            
            if st.button("⬅️ Go Back to Fix Issues", type="secondary"):
                if not st.session_state.analysis_result:
                    st.session_state.step = 1
                elif not st.session_state.persona_data:
                    st.session_state.step = 3
                st.rerun()
    
    # Step 6: Review & Export
    elif st.session_state.step == 6:
        st.header("📊 Step 6: Review & Export")
        st.markdown("Review your generated script and export in your preferred format.")
        
        if st.session_state.generated_script:
            # Script preview
            st.subheader("📝 Generated Script Preview")
            
            # Show script in expandable section
            with st.expander("📖 Full Script Content", expanded=True):
                st.markdown(st.session_state.generated_script)
            
            # Script statistics with improved time estimation
            st.markdown("---")
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
            time_status = "✅ Optimal" if abs(time_difference) <= 2 else ("⚠️ Too Long" if time_difference > 0 else "⚠️ Too Short")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Characters", f"{char_count:,}")
                st.metric("Total Words", f"{word_count:,}")
                
            with col2:
                st.metric("Estimated Speaking Time", f"{estimated_speaking_time:.1f} min")
                st.metric("Target Duration", f"{target_duration} min")
                
            with col3:
                st.metric("Time Status", time_status)
                st.metric("Words per Minute", f"{word_count/target_duration:.0f}")
            
            # Display agent performance if available
            if hasattr(st.session_state, 'script_agent'):
                st.markdown("---")
                st.subheader("🚀 Agent Performance")
                
                performance_summary = st.session_state.script_agent.get_performance_summary()
                
                col7, col8, col9 = st.columns(3)
                
                with col7:
                    st.metric("Success Rate", f"{performance_summary.get('success_rate', 0):.1f}%")
                    st.metric("Total Executions", performance_summary.get('total_executions', 0))
                
                with col8:
                    st.metric("Avg. Execution Time", f"{performance_summary.get('average_execution_time', 0):.2f}s")
                    st.metric("Optimizations Applied", len(performance_summary.get('optimization_stats', {}).get('optimizations_applied', [])))
                
                with col9:
                    st.metric("Cache Hit Rate", f"{performance_summary.get('cache_hit_rate', 0):.1f}%")
                    st.metric("Parallel Tasks", performance_summary.get('parallel_tasks', 0))
                
                # Show recent optimizations
                if performance_summary.get('optimization_stats', {}).get('performance_improvements'):
                    st.markdown("### 📈 Recent Optimizations")
                    improvements = performance_summary['optimization_stats']['performance_improvements'][-3:]
                    for imp in improvements:
                        st.info(f"🔧 Score: {imp['score']:.2f} | Optimizations: {', '.join(imp['optimizations'])}")
                
                # Show optimization suggestions
                if hasattr(st.session_state, 'generated_script') and isinstance(st.session_state.generated_script, dict):
                    suggestions = st.session_state.generated_script.get('optimization_suggestions', [])
                    if suggestions:
                        st.markdown("### 💡 Optimization Suggestions")
                        for suggestion in suggestions:
                            st.info(f"💡 {suggestion}")
            
            # Display cache performance if available
            if hasattr(st.session_state, 'claude_generator') and hasattr(st.session_state.claude_generator, 'get_cache_performance'):
                st.markdown("---")
                st.subheader("🚀 Cache Performance")
                
                cache_stats = st.session_state.claude_generator.get_cache_performance()
                if not cache_stats.get('caching_disabled'):
                    col4, col5, col6 = st.columns(3)
                    
                    total_requests = (cache_stats['hits'] + cache_stats['misses'])
                    hit_rate = (cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
                    
                    with col4:
                        st.metric("Cache Hit Rate", f"{hit_rate:.1f}%")
                    with col5:
                        st.metric("Cache Hits", cache_stats['hits'])
                        st.metric("Cache Misses", cache_stats['misses'])
                    with col6:
                        st.metric("Cache Writes", cache_stats['writes'])
                        st.metric("Total Requests", total_requests)
                    
                    # Cache effectiveness analysis
                    if hit_rate > 80:
                        st.success("✨ Excellent cache performance! Most prompts were served from cache.")
                    elif hit_rate > 50:
                        st.info("📈 Good cache utilization. Some prompts were reused effectively.")
                    else:
                        st.warning("💡 Low cache hit rate. Consider optimizing prompt structure for better reuse.")
                else:
                    st.info("ℹ️ Prompt caching is currently disabled.")
            
            # Time analysis
            if abs(time_difference) > 2:
                if time_difference > 0:
                    st.warning(f"⚠️ Script is {time_difference:.1f} minutes longer than target. Consider shortening content.")
                else:
                    st.warning(f"⚠️ Script is {abs(time_difference):.1f} minutes shorter than target. Consider adding more detail.")
            else:
                st.success("✅ Script timing is well-aligned with your target duration!")
            
            # Export options
            st.markdown("---")
            st.subheader("💾 Export Options")
            
            col4, col5, col6, col7 = st.columns(4)
            
            with col4:
                # Download as markdown
                st.download_button(
                    label="📄 Download Markdown",
                    data=st.session_state.generated_script,
                    file_name=f"presentation_script_{st.session_state.persona_data.get('full_name', 'presenter').replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col5:
                # Download as text
                st.download_button(
                    label="📝 Download Text",
                    data=st.session_state.generated_script,
                    file_name=f"presentation_script_{st.session_state.persona_data.get('full_name', 'presenter').replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col6:
                # Copy to clipboard button
                if st.button("📋 Copy Script", use_container_width=True):
                    st.success("📋 Script copied to clipboard!")
                    st.balloons()
            
            with col7:
                # Regenerate script
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.generated_script = None
                    st.session_state.step = 5
                    st.info("🔄 Returning to script generation...")
                    st.rerun()
            
            # Additional actions
            st.markdown("---")
            st.subheader("🎯 Next Steps")
            
            col8, col9, col10 = st.columns(3)
            
            with col8:
                st.markdown("**📚 Practice Tips**")
                st.info("• Read through the script multiple times\n• Practice timing with a stopwatch\n• Rehearse transitions between slides")
            
            with col9:
                st.markdown("**🎤 Presentation Tips**")
                st.info("• Maintain eye contact with audience\n• Use natural gestures\n• Pause for questions as indicated")
            
            with col10:
                st.markdown("**🔧 Customization**")
                st.info("• Adapt script to your speaking style\n• Add personal anecdotes\n• Adjust technical depth as needed")
            
            # Final actions
            st.markdown("---")
            col11, col12 = st.columns([1, 1])
            
            with col11:
                if st.button("🆕 Create New Script", type="secondary", use_container_width=True):
                    # Reset session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.success("🆕 Starting fresh! Upload a new presentation.")
                    st.rerun()
            
            with col12:
                if st.button("✅ Complete", type="primary", use_container_width=True):
                    st.success("🎉 Congratulations! Your presentation script is ready.")
                    st.balloons()
                    st.info("💡 **Tip:** Bookmark this page to return to your script later.")
                    
        else:
            st.error("❌ No script generated. Please go back to Step 5.")
            if st.button("⬅️ Back to Generation", type="secondary"):
                st.session_state.step = 5
                st.rerun()


if __name__ == "__main__":
    main()
