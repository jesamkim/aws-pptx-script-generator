# AWS PPTX Script Generator User Guide

## Introduction

The AWS PPTX Script Generator is a powerful tool that helps you create professional presentation scripts using Claude 3.7 Sonnet AI. This guide will walk you through the features and usage of the application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Performance Optimization](#performance-optimization)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

## Getting Started

### System Requirements

- Python 3.9 or higher
- AWS account with Bedrock access
- 4GB RAM minimum (8GB recommended)
- Internet connection

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jesamkim/aws-pptx-script-generator.git
cd aws-pptx-script-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt -U
```

3. Configure AWS credentials:
```bash
aws configure
```

4. Start the application:
```bash
streamlit run streamlit_app.py
```

## Basic Usage

### Step 1: Upload PowerPoint

1. Click "Upload PowerPoint" button
2. Select your PPTX file
3. Wait for initial analysis

Tips:
- Use PPTX format (not PPT)
- Keep images and fonts embedded
- Ensure readable text content

### Step 2: AI Analysis

The system will analyze your presentation for:
- Content structure
- Technical depth
- Key themes
- AWS services mentioned

Review the analysis results and adjust if needed.

### Step 3: Presenter Information

Enter your details:
- Full name
- Job title
- Experience level
- Presentation style
- Language preference

### Step 4: Presentation Settings

Configure:
- Duration
- Target audience
- Technical depth
- Q&A preferences
- Timing requirements

### Step 5: Generate Script

1. Click "Generate Script"
2. Monitor progress
3. Review generated content

### Step 6: Export

Available formats:
- Markdown
- Plain text
- Copy to clipboard

## Advanced Features

### Prompt Caching

The system uses intelligent prompt caching to improve performance:
- Reduces generation time
- Lowers API costs
- Maintains consistency

To optimize caching:
1. Use consistent presentation structures
2. Keep similar technical levels
3. Monitor cache performance

### Performance Monitoring

Access the performance dashboard:
1. Click "View Performance" in sidebar
2. Monitor:
   - Execution times
   - Cache hit rates
   - Resource usage
   - Quality metrics

### Customization Options

Fine-tune your scripts:
- Adjust technical depth
- Modify speaking time
- Add speaker notes
- Include Q&A preparation

## Performance Optimization

### Best Practices

1. **Presentation Structure**
   - Use clear slide titles
   - Include speaker notes
   - Maintain consistent formatting

2. **Content Organization**
   - Group related topics
   - Balance technical depth
   - Include transition slides

3. **Resource Management**
   - Monitor memory usage
   - Clear cache when needed
   - Use appropriate worker count

### Cache Management

1. **When to Clear Cache**
   - After major content changes
   - When switching presentation styles
   - If performance degrades

2. **Optimizing Cache Usage**
   - Use consistent terminology
   - Maintain similar structures
   - Monitor hit rates

## Troubleshooting

### Common Issues

1. **Slow Generation**
   - Check internet connection
   - Monitor system resources
   - Clear browser cache
   - Reduce parallel workers

2. **Poor Quality Output**
   - Review input content
   - Adjust technical level
   - Check language settings
   - Verify slide content

3. **System Errors**
   - Verify AWS credentials
   - Check Python version
   - Update dependencies
   - Review error logs

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "API Error" | Connection issue | Check internet/AWS access |
| "Memory Error" | Resource limit | Reduce worker count |
| "Cache Error" | Cache corruption | Clear cache and retry |
| "Timeout" | Slow processing | Adjust timeout settings |

## FAQ

### General Questions

**Q: How long does script generation take?**
A: Typically 1-3 minutes, depending on presentation size and cache status.

**Q: What languages are supported?**
A: English and Korean, with English optimized for technical content.

**Q: Can I modify generated scripts?**
A: Yes, all scripts are fully editable in the review phase.

### Technical Questions

**Q: How does caching work?**
A: The system caches common prompt patterns and responses to improve performance.

**Q: What's the optimal presentation size?**
A: 15-30 slides work best, but the system can handle up to 100 slides.

**Q: How is quality measured?**
A: Through multiple factors including coherence, technical accuracy, and timing accuracy.

### Performance Questions

**Q: When should I clear cache?**
A: When switching between very different presentations or if performance degrades.

**Q: How many parallel workers should I use?**
A: Start with 4 workers and adjust based on system performance.

**Q: What affects generation time?**
A: Slide count, technical depth, cache status, and system resources.

## Support

For additional support:
- Check the [GitHub Issues](https://github.com/yourusername/aws-pptx-script-generator/issues)
- Review the [API Documentation](API.md)
- Contact AWS Support for Bedrock-related issues

## Updates and Maintenance

### Staying Updated

1. Regular updates:
```bash
git pull origin main
pip install -r requirements.txt -U
```

2. Cache maintenance:
```bash
# Clear cache
rm -rf .cache/*
```

3. Log rotation:
```bash
# Check logs
tail -f logs/app.log
```

### Performance Monitoring

Regular checks:
1. Review dashboard metrics
2. Monitor resource usage
3. Optimize cache settings
4. Update configurations

## Security Considerations

1. **AWS Credentials**
   - Use IAM roles
   - Rotate credentials
   - Monitor usage

2. **Data Protection**
   - No PII in scripts
   - Secure file handling
   - Clean temporary files

3. **Access Control**
   - Use AWS best practices
   - Monitor API access
   - Review logs regularly
