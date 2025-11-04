#!/usr/bin/env python3
"""CLI Script Generator for AWS PowerPoint Presentations.

This script provides a command-line interface for generating presentation scripts
without requiring the Streamlit UI. It processes PowerPoint files and generates
professional presentation scripts using Claude Sonnet 4.5.

Usage:
    python gen_script.py --pptx sample.pptx --name "Jesam Kim" --duration 30

Author: Jesam Kim (AWS SA)
Version: 2.1.1
"""

import argparse
import sys
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# Configure logger for CLI
logger.remove()
logger.add(sys.stderr, format="<level>{level: <8}</level> | {message}", level="INFO")


class CLIScriptGenerator:
    """Command-line interface for script generation."""

    def __init__(self):
        """Initialize CLI script generator."""
        self.temp_files = []

    def analyze_powerpoint(self, pptx_path: str) -> Optional[Dict[str, Any]]:
        """
        Analyze PowerPoint file using Claude Sonnet 4.5.

        Args:
            pptx_path: Path to PowerPoint file

        Returns:
            Analysis result dictionary or None if failed
        """
        try:
            logger.info(f"Loading PowerPoint file: {pptx_path}")

            # Import required modules
            from src.processors.pptx_processor import PowerPointProcessor
            from src.analysis.multimodal_analyzer import MultimodalAnalyzer
            from src.processors.slide_image_converter import SlideImageConverter

            # Initialize processors
            processor = PowerPointProcessor()
            analyzer = MultimodalAnalyzer()
            converter = SlideImageConverter()

            # Load and process presentation
            logger.info("Processing PowerPoint file...")
            processor.load_presentation(pptx_path)
            presentation_data = processor.process_presentation()

            # Convert slides to images
            logger.info("Converting slides to images for multimodal analysis...")
            slide_images = converter.convert_presentation_to_images(pptx_path)

            # Prepare data for analysis
            logger.info("Analyzing presentation content with Claude Sonnet 4.5...")
            slides_data = []
            for i, slide_content in enumerate(presentation_data.slides):
                slide_number = i + 1
                image_data = slide_images.get(slide_number, b'')
                text_content = slide_content.text_content
                slides_data.append((slide_number, image_data, text_content))

            # Perform multimodal analysis
            presentation_analysis = analyzer.analyze_complete_presentation(slides_data)

            # Generate comprehensive analysis result
            logger.info("Generating analysis summary...")
            analysis_summary = analyzer.get_analysis_summary(presentation_analysis)

            # Extract main topic
            main_topic = presentation_analysis.overall_theme
            if not main_topic or main_topic == "General AWS":
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
                    "key_points": slide_analysis.key_concepts[:5],
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

            # Create analysis result
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
                "recommendations": presentation_analysis.recommendations
            }

            logger.success(f"Analysis completed: {len(slide_summaries)} slides analyzed")
            return analysis_result

        except Exception as e:
            logger.error(f"PowerPoint analysis failed: {str(e)}")
            return None

    def generate_script(
        self,
        analysis_result: Dict[str, Any],
        persona_data: Dict[str, str],
        presentation_params: Dict[str, Any],
        mode: str = "cached"
    ) -> Optional[str]:
        """
        Generate presentation script.

        Args:
            analysis_result: Analysis result from PowerPoint
            persona_data: Presenter information
            presentation_params: Presentation parameters
            mode: Generation mode ('cached' or 'optimized')

        Returns:
            Generated script string or None if failed
        """
        if not analysis_result:
            return None

        try:
            logger.info(f"Generating script using {mode} mode...")

            if mode == "optimized":
                return self._generate_optimized_script(
                    analysis_result, persona_data, presentation_params
                )
            else:
                return self._generate_cached_script(
                    analysis_result, persona_data, presentation_params
                )

        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            return None

    def _generate_cached_script(
        self,
        analysis_result: Dict[str, Any],
        persona_data: Dict[str, str],
        presentation_params: Dict[str, Any]
    ) -> Optional[str]:
        """Generate script using cached mode."""
        from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached

        # Initialize generator
        claude_generator = ClaudeScriptGeneratorCached(enable_caching=True)

        # Create mock presentation analysis
        class MockPresentationAnalysis:
            def __init__(self, analysis_result):
                self.overall_theme = analysis_result['main_topic']
                self.technical_complexity = 3.0
                self.slide_analyses = []

                for slide_summary in analysis_result.get('slide_summaries', []):
                    mock_slide = type('MockSlideAnalysis', (), {
                        'slide_number': slide_summary['slide_number'],
                        'content_summary': slide_summary['title'],
                        'visual_description': slide_summary['main_content'],
                        'key_concepts': slide_summary.get('key_points', []),
                        'aws_services': slide_summary.get('aws_services', [])
                    })()
                    self.slide_analyses.append(mock_slide)

        presentation_analysis = MockPresentationAnalysis(analysis_result)

        # Merge parameters
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

        # Generate script
        script_content = claude_generator.generate_complete_presentation_script(
            presentation_analysis=presentation_analysis,
            persona_data=persona_data,
            presentation_params=enhanced_params,
            mcp_enhanced_services=analysis_result.get('mcp_enhanced_services')
        )

        logger.success(f"Script generated: {len(script_content)} characters")
        return script_content

    def _generate_optimized_script(
        self,
        analysis_result: Dict[str, Any],
        persona_data: Dict[str, str],
        presentation_params: Dict[str, Any]
    ) -> Optional[str]:
        """Generate script using optimized agent mode."""
        import asyncio
        import concurrent.futures
        from src.agent.optimized_script_agent import OptimizedScriptAgent, OptimizedPersonaProfile

        # Initialize agent
        script_agent = OptimizedScriptAgent(enable_caching=True, max_workers=4)

        # Create mock presentation analysis
        class MockPresentationAnalysis:
            def __init__(self, analysis_result):
                self.overall_theme = analysis_result['main_topic']
                self.technical_complexity = 3.0
                self.slide_analyses = []

                for slide_summary in analysis_result.get('slide_summaries', []):
                    mock_slide = type('MockSlideAnalysis', (), {
                        'slide_number': slide_summary['slide_number'],
                        'content_summary': slide_summary['title'],
                        'visual_description': slide_summary['main_content'],
                        'key_concepts': slide_summary.get('key_points', []),
                        'aws_services': slide_summary.get('aws_services', [])
                    })()
                    self.slide_analyses.append(mock_slide)

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

        # Merge parameters
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

        # Generate script
        try:
            try:
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, script_agent.generate_script_optimized(
                        presentation_analysis=presentation_analysis,
                        persona_profile=optimized_persona,
                        presentation_params=enhanced_params,
                        mcp_enhanced_services=analysis_result.get('mcp_enhanced_services')
                    ))
                    result = future.result()
            except RuntimeError:
                result = asyncio.run(
                    script_agent.generate_script_optimized(
                        presentation_analysis=presentation_analysis,
                        persona_profile=optimized_persona,
                        presentation_params=enhanced_params,
                        mcp_enhanced_services=analysis_result.get('mcp_enhanced_services')
                    )
                )

            if result.success:
                logger.success(f"Optimized script generated: {len(result.script_content)} characters")
                return result.script_content
            else:
                logger.error(f"Optimized script generation failed: {result.metadata.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            logger.error(f"Optimized script generation error: {str(e)}")
            return None

    def save_script(self, script: str, output_path: str) -> bool:
        """
        Save script to file.

        Args:
            script: Script content
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script)

            logger.success(f"Script saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save script: {str(e)}")
            return False

    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_file}: {str(e)}")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate professional presentation scripts from PowerPoint files using Claude Sonnet 4.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python gen_script.py --pptx sample.pptx --name "Jesam Kim" --duration 30

  # Full configuration
  python gen_script.py \\
    --pptx sample.pptx \\
    --name "Jesam Kim" \\
    --title "Senior Solutions Architect" \\
    --company "AWS" \\
    --language Korean \\
    --duration 30 \\
    --output my_script.md \\
    --mode optimized

  # Quick test with defaults
  python gen_script.py --pptx presentation.pptx
        """
    )

    # Required arguments
    parser.add_argument(
        '--pptx',
        required=True,
        type=str,
        help='Path to PowerPoint (.pptx) file'
    )

    # Presenter information
    presenter = parser.add_argument_group('Presenter Information')
    presenter.add_argument('--name', type=str, default='Presenter', help='Presenter full name (default: Presenter)')
    presenter.add_argument('--title', type=str, default='Solutions Architect', help='Job title (default: Solutions Architect)')
    presenter.add_argument('--company', type=str, default='AWS', help='Company name (default: AWS)')
    presenter.add_argument('--experience', type=str, default='Senior', choices=['Junior', 'Mid-level', 'Senior', 'Expert'], help='Experience level (default: Senior)')
    presenter.add_argument('--confidence', type=str, default='Comfortable', choices=['Beginner', 'Comfortable', 'Experienced', 'Expert'], help='Presentation confidence (default: Comfortable)')
    presenter.add_argument('--style', type=str, default='Conversational', choices=['Formal', 'Conversational', 'Interactive', 'Q&A Focused'], help='Interaction style (default: Conversational)')

    # Presentation settings
    presentation = parser.add_argument_group('Presentation Settings')
    presentation.add_argument('--language', type=str, default='English', choices=['English', 'Korean'], help='Presentation language (default: English)')
    presentation.add_argument('--duration', type=int, default=30, help='Total presentation duration in minutes (default: 30)')
    presentation.add_argument('--audience', type=str, default='Technical', choices=['Technical', 'Business', 'Mixed', 'Executive'], help='Target audience (default: Technical)')
    presentation.add_argument('--pres-style', type=str, default='Professional', choices=['Professional', 'Conversational', 'Technical', 'Educational'], help='Presentation style (default: Professional)')
    presentation.add_argument('--technical-depth', type=int, default=3, choices=[1, 2, 3, 4, 5], help='Technical detail level 1-5 (default: 3)')
    presentation.add_argument('--time-per-slide', type=float, default=2.0, help='Average time per slide in minutes (default: 2.0)')
    presentation.add_argument('--include-qa', action='store_true', default=True, help='Include Q&A section (default: True)')
    presentation.add_argument('--no-qa', dest='include_qa', action='store_false', help='Exclude Q&A section')
    presentation.add_argument('--qa-duration', type=int, default=10, help='Q&A duration in minutes (default: 10)')

    # Output settings
    output = parser.add_argument_group('Output Settings')
    output.add_argument('--output', type=str, default='output_script.md', help='Output file path (default: output_script.md)')
    output.add_argument('--mode', type=str, default='cached', choices=['cached', 'optimized'], help='Generation mode: cached (faster) or optimized (better quality) (default: cached)')

    # Logging
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress all output except errors')

    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()

    # Configure logging level
    if args.quiet:
        logger.remove()
        logger.add(sys.stderr, level="ERROR")
    elif args.verbose:
        logger.remove()
        logger.add(sys.stderr, format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | {message}", level="DEBUG")

    # Validate input file
    pptx_path = Path(args.pptx)
    if not pptx_path.exists():
        logger.error(f"PowerPoint file not found: {args.pptx}")
        sys.exit(1)

    if not pptx_path.suffix.lower() == '.pptx':
        logger.error(f"File must be a PowerPoint (.pptx) file: {args.pptx}")
        sys.exit(1)

    # Initialize generator
    generator = CLIScriptGenerator()

    try:
        # Step 1: Analyze PowerPoint
        logger.info("=" * 60)
        logger.info("Step 1/3: Analyzing PowerPoint Presentation")
        logger.info("=" * 60)

        analysis_result = generator.analyze_powerpoint(str(pptx_path))
        if not analysis_result:
            logger.error("PowerPoint analysis failed")
            sys.exit(1)

        # Step 2: Prepare parameters
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 2/3: Preparing Script Generation Parameters")
        logger.info("=" * 60)

        persona_data = {
            'full_name': args.name,
            'job_title': args.title,
            'company': args.company,
            'experience_level': args.experience,
            'presentation_confidence': args.confidence,
            'interaction_style': args.style
        }

        presentation_params = {
            'language': args.language,
            'duration': args.duration,
            'target_audience': args.audience,
            'presentation_style': args.pres_style,
            'technical_depth': args.technical_depth,
            'time_per_slide': args.time_per_slide,
            'include_qa': args.include_qa,
            'qa_duration': args.qa_duration if args.include_qa else 0,
            'include_timing': True,
            'include_transitions': True,
            'include_speaker_notes': True,
            'include_qa_prep': args.include_qa
        }

        logger.info(f"Presenter: {args.name} ({args.title})")
        logger.info(f"Language: {args.language}, Duration: {args.duration} min")
        logger.info(f"Mode: {args.mode.upper()}")

        # Step 3: Generate script
        logger.info("")
        logger.info("=" * 60)
        logger.info("Step 3/3: Generating Presentation Script")
        logger.info("=" * 60)

        script = generator.generate_script(
            analysis_result=analysis_result,
            persona_data=persona_data,
            presentation_params=presentation_params,
            mode=args.mode
        )

        if not script:
            logger.error("Script generation failed")
            sys.exit(1)

        # Save script
        logger.info("")
        if generator.save_script(script, args.output):
            logger.info("")
            logger.success("=" * 60)
            logger.success("Script Generation Completed Successfully!")
            logger.success("=" * 60)
            logger.success(f"Output file: {args.output}")
            logger.success(f"Script length: {len(script)} characters")
            logger.success(f"Word count: {len(script.split())} words")
        else:
            logger.error("Failed to save script")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\nScript generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        generator.cleanup()


if __name__ == "__main__":
    main()
