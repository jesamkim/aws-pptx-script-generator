"""Professional Markdown Report Generator.

This module generates comprehensive, well-structured presentation script reports
with multi-language support and professional formatting.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import datetime
from pathlib import Path
from loguru import logger

from src.script_generation.script_engine import GeneratedScript, ScriptSection
from src.analysis.multimodal_analyzer import PresentationAnalysis
from src.mcp_integration.knowledge_enhancer import EnhancedContent
from src.utils.logger import log_execution_time


@dataclass
class ReportSection:
    """Individual report section.
    
    Attributes:
        title: Section title
        content: Section content
        level: Heading level (1-6)
        metadata: Section metadata
    """
    title: str
    content: str
    level: int
    metadata: Dict[str, Any]


@dataclass
class MarkdownReport:
    """Complete markdown report.
    
    Attributes:
        title: Report title
        sections: List of report sections
        metadata: Report metadata
        language: Report language
        generated_at: Generation timestamp
        quality_score: Overall quality score
    """
    title: str
    sections: List[ReportSection]
    metadata: Dict[str, Any]
    language: str
    generated_at: datetime.datetime
    quality_score: float


class MarkdownGenerator:
    """Professional markdown report generator with multi-language support."""
    
    def __init__(self):
        """Initialize markdown generator."""
        # Language-specific templates
        self.templates = {
            'english': {
                'title': "# AWS SA Presentation Script Report",
                'toc_title': "## Table of Contents",
                'overview_title': "## Executive Summary",
                'script_title': "## Presentation Script",
                'appendix_title': "## Technical Appendix",
                'qa_title': "## Q&A Preparation",
                'metrics_title': "## Quality Metrics",
                'slide_prefix': "### Slide",
                'time_label': "Time",
                'notes_label': "Speaker Notes",
                'key_points_label': "Key Points",
                'generated_label': "Generated on",
                'presenter_label': "Presenter",
                'duration_label': "Duration",
                'audience_label': "Target Audience"
            },
            'korean': {
                'title': "# AWS SA 프레젠테이션 스크립트 보고서",
                'toc_title': "## 목차",
                'overview_title': "## 개요",
                'script_title': "## 프레젠테이션 스크립트",
                'appendix_title': "## 기술 부록",
                'qa_title': "## Q&A 준비",
                'metrics_title': "## 품질 지표",
                'slide_prefix': "### 슬라이드",
                'time_label': "소요 시간",
                'notes_label': "발표자 노트",
                'key_points_label': "핵심 포인트",
                'generated_label': "생성일",
                'presenter_label': "발표자",
                'duration_label': "총 시간",
                'audience_label': "대상 청중"
            }
        }
        
        logger.info("Initialized markdown generator with multi-language support")
    
    @log_execution_time
    def generate_comprehensive_report(
        self,
        generated_script: GeneratedScript,
        presentation_analysis: PresentationAnalysis,
        enhanced_contents: List[EnhancedContent],
        persona: Dict[str, Any],
        context: Dict[str, Any]
    ) -> MarkdownReport:
        """Generate comprehensive markdown report.
        
        Args:
            generated_script: Generated script object
            presentation_analysis: Presentation analysis results
            enhanced_contents: MCP-enhanced content
            persona: Presenter persona
            context: Presentation context
            
        Returns:
            MarkdownReport object
        """
        try:
            language = generated_script.language
            templates = self.templates.get(language, self.templates['english'])
            
            # Generate report sections
            sections = []
            
            # 1. Title and metadata
            title_section = self._generate_title_section(
                generated_script, persona, context, templates
            )
            sections.append(title_section)
            
            # 2. Table of contents
            toc_section = self._generate_toc_section(
                generated_script, templates
            )
            sections.append(toc_section)
            
            # 3. Executive summary
            overview_section = self._generate_overview_section(
                generated_script, presentation_analysis, templates
            )
            sections.append(overview_section)
            
            # 4. Main script content
            script_sections = self._generate_script_sections(
                generated_script, templates
            )
            sections.extend(script_sections)
            
            # 5. Technical appendix
            appendix_section = self._generate_technical_appendix(
                presentation_analysis, enhanced_contents, templates
            )
            sections.append(appendix_section)
            
            # 6. Q&A preparation
            qa_section = self._generate_qa_section(
                presentation_analysis, enhanced_contents, templates
            )
            sections.append(qa_section)
            
            # 7. Quality metrics
            metrics_section = self._generate_metrics_section(
                generated_script, templates
            )
            sections.append(metrics_section)
            
            # Create complete report
            report = MarkdownReport(
                title=generated_script.title,
                sections=sections,
                metadata={
                    'presenter': persona,
                    'context': context,
                    'generation_stats': generated_script.metadata
                },
                language=language,
                generated_at=datetime.datetime.now(),
                quality_score=generated_script.quality_metrics.get('overall_score', 0.8)
            )
            
            logger.info(f"Generated comprehensive markdown report: {len(sections)} sections")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {str(e)}")
            raise
    
    def _generate_title_section(
        self,
        script: GeneratedScript,
        persona: Dict[str, Any],
        context: Dict[str, Any],
        templates: Dict[str, str]
    ) -> ReportSection:
        """Generate title and metadata section."""
        content_parts = [
            templates['title'],
            "",
            f"**{templates['presenter_label']}**: {persona.get('full_name', '')}, {persona.get('job_title', '')}",
            f"**{templates['duration_label']}**: {script.total_duration} minutes",
            f"**{templates['audience_label']}**: {context.get('target_audience', '')}",
            f"**{templates['generated_label']}**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]
        
        return ReportSection(
            title="Title",
            content="\n".join(content_parts),
            level=1,
            metadata={'type': 'title'}
        )
    
    def _generate_toc_section(
        self,
        script: GeneratedScript,
        templates: Dict[str, str]
    ) -> ReportSection:
        """Generate table of contents."""
        toc_items = [
            templates['toc_title'],
            "",
            "1. [Executive Summary](#executive-summary)",
            "2. [Presentation Script](#presentation-script)"
        ]
        
        # Add slide entries
        for i, section in enumerate(script.sections, 3):
            slide_title = section.title[:30] + "..." if len(section.title) > 30 else section.title
            toc_items.append(f"   - [{templates['slide_prefix']} {section.slide_number}: {slide_title}](#slide-{section.slide_number})")
        
        toc_items.extend([
            f"{len(script.sections) + 3}. [Technical Appendix](#technical-appendix)",
            f"{len(script.sections) + 4}. [Q&A Preparation](#qa-preparation)",
            f"{len(script.sections) + 5}. [Quality Metrics](#quality-metrics)",
            ""
        ])
        
        return ReportSection(
            title="Table of Contents",
            content="\n".join(toc_items),
            level=2,
            metadata={'type': 'toc'}
        )
    
    def _generate_overview_section(
        self,
        script: GeneratedScript,
        analysis: PresentationAnalysis,
        templates: Dict[str, str]
    ) -> ReportSection:
        """Generate executive summary section."""
        content_parts = [
            templates['overview_title'],
            "",
            script.overview,
            "",
            f"**Theme**: {analysis.overall_theme}",
            f"**Technical Complexity**: {analysis.technical_complexity:.1f}/5",
            f"**Estimated Duration**: {analysis.estimated_duration:.1f} minutes",
            f"**Flow Assessment**: {analysis.flow_assessment.title()}",
            ""
        ]
        
        if analysis.recommendations:
            content_parts.extend([
                "**Key Recommendations**:",
                ""
            ])
            for rec in analysis.recommendations[:3]:
                content_parts.append(f"- {rec}")
            content_parts.append("")
        
        return ReportSection(
            title="Executive Summary",
            content="\n".join(content_parts),
            level=2,
            metadata={'type': 'overview'}
        )
    
    def _generate_script_sections(
        self,
        script: GeneratedScript,
        templates: Dict[str, str]
    ) -> List[ReportSection]:
        """Generate main script sections."""
        sections = []
        
        # Main script header
        header_section = ReportSection(
            title="Presentation Script",
            content=templates['script_title'],
            level=2,
            metadata={'type': 'script_header'}
        )
        sections.append(header_section)
        
        # Individual slide sections
        for section in script.sections:
            slide_content = self._format_slide_section(section, templates)
            slide_section = ReportSection(
                title=f"Slide {section.slide_number}",
                content=slide_content,
                level=3,
                metadata={'type': 'slide', 'slide_number': section.slide_number}
            )
            sections.append(slide_section)
        
        return sections
    
    def _format_slide_section(
        self,
        section: ScriptSection,
        templates: Dict[str, str]
    ) -> str:
        """Format individual slide section."""
        content_parts = [
            f"{templates['slide_prefix']} {section.slide_number}: {section.title}",
            "",
            f"*{templates['time_label']}: {section.time_allocation} minutes*",
            "",
            section.content,
            ""
        ]
        
        # Add speaker notes if available
        if section.speaker_notes:
            content_parts.extend([
                f"#### {templates['notes_label']}",
                "",
                section.speaker_notes,
                ""
            ])
        
        # Add key points if available
        if section.key_points:
            content_parts.extend([
                f"#### {templates['key_points_label']}",
                ""
            ])
            for point in section.key_points:
                content_parts.append(f"- {point}")
            content_parts.append("")
        
        # Add interaction cues if available
        if section.interaction_cues:
            content_parts.extend([
                "#### Interaction Opportunities",
                ""
            ])
            for cue in section.interaction_cues:
                content_parts.append(f"💬 {cue}")
            content_parts.append("")
        
        content_parts.append("---")
        content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _generate_technical_appendix(
        self,
        analysis: PresentationAnalysis,
        enhanced_contents: List[EnhancedContent],
        templates: Dict[str, str]
    ) -> ReportSection:
        """Generate technical appendix section."""
        content_parts = [
            templates['appendix_title'],
            ""
        ]
        
        # AWS Services Summary
        all_services = set()
        for slide_analysis in analysis.slide_analyses:
            all_services.update(slide_analysis.aws_services)
        
        if all_services:
            content_parts.extend([
                "### AWS Services Covered",
                ""
            ])
            for service in sorted(all_services):
                content_parts.append(f"- **{service}**")
            content_parts.append("")
        
        # Best Practices Summary
        all_practices = []
        for enhanced in enhanced_contents:
            all_practices.extend(enhanced.best_practices)
        
        if all_practices:
            content_parts.extend([
                "### Key Best Practices",
                ""
            ])
            for practice in all_practices[:5]:  # Top 5 practices
                content_parts.append(f"💡 {practice}")
                content_parts.append("")
        
        # Code Examples
        all_examples = []
        for enhanced in enhanced_contents:
            all_examples.extend(enhanced.code_examples)
        
        if all_examples:
            content_parts.extend([
                "### Code Examples",
                ""
            ])
            for example in all_examples[:3]:  # Top 3 examples
                content_parts.extend([
                    f"**{example.get('description', 'Code Example')}**",
                    "",
                    f"```{example.get('language', 'text')}",
                    example.get('code', ''),
                    "```",
                    ""
                ])
        
        return ReportSection(
            title="Technical Appendix",
            content="\n".join(content_parts),
            level=2,
            metadata={'type': 'appendix'}
        )
    
    def _generate_qa_section(
        self,
        analysis: PresentationAnalysis,
        enhanced_contents: List[EnhancedContent],
        templates: Dict[str, str]
    ) -> ReportSection:
        """Generate Q&A preparation section."""
        content_parts = [
            templates['qa_title'],
            "",
            "### Anticipated Questions",
            ""
        ]
        
        # Generate questions based on technical depth and services
        questions = self._generate_anticipated_questions(analysis, enhanced_contents)
        
        for i, question in enumerate(questions[:5], 1):
            content_parts.extend([
                f"**Q{i}: {question['question']}**",
                "",
                f"*Suggested Answer*: {question['answer']}",
                ""
            ])
        
        # Add troubleshooting tips
        content_parts.extend([
            "### Common Issues and Solutions",
            "",
            "- **Technical Questions**: Refer to AWS documentation links in appendix",
            "- **Pricing Questions**: Direct to AWS Pricing Calculator",
            "- **Implementation Details**: Offer follow-up technical session",
            "- **Security Concerns**: Emphasize AWS security best practices",
            ""
        ])
        
        return ReportSection(
            title="Q&A Preparation",
            content="\n".join(content_parts),
            level=2,
            metadata={'type': 'qa'}
        )
    
    def _generate_anticipated_questions(
        self,
        analysis: PresentationAnalysis,
        enhanced_contents: List[EnhancedContent]
    ) -> List[Dict[str, str]]:
        """Generate anticipated questions based on content."""
        questions = []
        
        # Questions based on AWS services
        all_services = set()
        for slide_analysis in analysis.slide_analyses:
            all_services.update(slide_analysis.aws_services)
        
        if 'Amazon S3' in all_services:
            questions.append({
                'question': 'What are the security features of Amazon S3?',
                'answer': 'S3 provides encryption at rest and in transit, access controls through IAM, bucket policies, and VPC endpoints for secure access.'
            })
        
        if 'AWS Lambda' in all_services:
            questions.append({
                'question': 'How does Lambda pricing work?',
                'answer': 'Lambda charges based on the number of requests and compute time. You pay only for what you use with no upfront costs.'
            })
        
        # Questions based on technical complexity
        if analysis.technical_complexity >= 4:
            questions.append({
                'question': 'What are the implementation challenges we should consider?',
                'answer': 'Key considerations include proper architecture design, security implementation, monitoring setup, and team training requirements.'
            })
        
        # Generic questions
        questions.extend([
            {
                'question': 'What is the typical implementation timeline?',
                'answer': 'Implementation timelines vary based on complexity, but most projects can be completed in 2-6 months with proper planning and resources.'
            },
            {
                'question': 'What support options are available?',
                'answer': 'AWS provides comprehensive support including documentation, training, professional services, and various support plans to meet your needs.'
            }
        ])
        
        return questions
    
    def _generate_metrics_section(
        self,
        script: GeneratedScript,
        templates: Dict[str, str]
    ) -> ReportSection:
        """Generate quality metrics section."""
        metrics = script.quality_metrics
        
        content_parts = [
            templates['metrics_title'],
            "",
            f"**Overall Quality Score**: {metrics.get('overall_score', 0):.2f}/1.00",
            f"**Total Word Count**: {metrics.get('total_words', 0):,}",
            f"**Average Words per Slide**: {metrics.get('avg_words_per_section', 0):.0f}",
            f"**Number of Sections**: {metrics.get('sections_count', 0)}",
            "",
            "### Quality Factors",
            ""
        ]
        
        quality_factors = metrics.get('quality_factors', {})
        for factor, score in quality_factors.items():
            factor_name = factor.replace('_', ' ').title()
            status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
            content_parts.append(f"- **{factor_name}**: {score:.2f} {status}")
        
        content_parts.extend([
            "",
            "### Recommendations for Improvement",
            ""
        ])
        
        # Generate improvement recommendations
        if metrics.get('overall_score', 0) < 0.8:
            content_parts.append("- Review content for completeness and flow")
        if metrics.get('avg_words_per_section', 0) < 50:
            content_parts.append("- Consider adding more detail to slide scripts")
        if metrics.get('avg_words_per_section', 0) > 200:
            content_parts.append("- Consider condensing scripts for better pacing")
        
        content_parts.append("")
        
        return ReportSection(
            title="Quality Metrics",
            content="\n".join(content_parts),
            level=2,
            metadata={'type': 'metrics'}
        )
    
    def format_report_as_markdown(self, report: MarkdownReport) -> str:
        """Format complete report as markdown string.
        
        Args:
            report: MarkdownReport object
            
        Returns:
            Formatted markdown string
        """
        try:
            markdown_parts = []
            
            for section in report.sections:
                markdown_parts.append(section.content)
            
            # Add footer
            markdown_parts.extend([
                "---",
                "",
                f"*Report generated by AWS SA Presentation Script Generator*",
                f"*Generated on: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*",
                f"*Language: {report.language.title()}*",
                f"*Quality Score: {report.quality_score:.2f}*"
            ])
            
            return "\n".join(markdown_parts)
            
        except Exception as e:
            logger.error(f"Failed to format report as markdown: {str(e)}")
            return f"# Report Generation Error\n\nFailed to format report: {str(e)}"
    
    def save_report_to_file(self, report: MarkdownReport, file_path: str) -> bool:
        """Save report to markdown file.
        
        Args:
            report: MarkdownReport object
            file_path: Output file path
            
        Returns:
            True if saved successfully
        """
        try:
            markdown_content = self.format_report_as_markdown(report)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Saved markdown report to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save report to {file_path}: {str(e)}")
            return False
