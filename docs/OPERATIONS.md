# Operations Manual

## Overview

This manual provides operational guidance for deploying, monitoring, and maintaining the AWS PPTX Script Generator in production environments.

## Deployment

### Prerequisites

- AWS Account with Bedrock access
- Python 3.10+ environment
- Streamlit deployment platform
- Monitoring tools (CloudWatch, etc.)

### Production Deployment

1. **Environment Setup**
```bash
# Create production environment
python -m venv prod-env
source prod-env/bin/activate
pip install -r requirements.txt
```

2. **Configuration**
```bash
# Set environment variables
export AWS_REGION=us-west-2
export BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
export CACHE_ENABLED=true
export MAX_WORKERS=8
```

3. **Launch Application**
```bash
streamlit run streamlit_app.py --server.port 8501 --server.headless true
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.headless=true"]
```

## Monitoring

### Key Metrics

1. **Performance Metrics**
   - Script generation time
   - Cache hit rate
   - Memory usage
   - CPU utilization

2. **Quality Metrics**
   - Success rate
   - Quality scores
   - User satisfaction

3. **System Metrics**
   - API response times
   - Error rates
   - Resource utilization

### Monitoring Setup

```python
# CloudWatch integration
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_metrics(metrics):
    cloudwatch.put_metric_data(
        Namespace='PPTX-Generator',
        MetricData=[
            {
                'MetricName': 'ExecutionTime',
                'Value': metrics['execution_time'],
                'Unit': 'Seconds'
            },
            {
                'MetricName': 'CacheHitRate',
                'Value': metrics['cache_hit_rate'],
                'Unit': 'Percent'
            }
        ]
    )
```

## Maintenance

### Regular Tasks

1. **Daily**
   - Check system health
   - Review error logs
   - Monitor resource usage

2. **Weekly**
   - Analyze performance trends
   - Review cache efficiency
   - Update configurations

3. **Monthly**
   - Performance optimization
   - Security updates
   - Capacity planning

### Cache Management

```bash
# Cache status check
python -c "
from src.script_generation.claude_script_generator_cached import ClaudeScriptGeneratorCached
gen = ClaudeScriptGeneratorCached()
print(gen.get_cache_performance())
"

# Clear cache if needed
rm -rf .cache/*
```

### Log Management

```bash
# Log rotation
logrotate /etc/logrotate.d/pptx-generator

# Log analysis
grep ERROR logs/app.log | tail -20
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
```bash
# Check memory usage
ps aux | grep streamlit
free -h

# Solution: Restart application
pkill -f streamlit
streamlit run streamlit_app.py
```

2. **Slow Performance**
```bash
# Check cache status
python check_cache.py

# Clear cache if needed
python clear_cache.py
```

3. **API Errors**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models
```

### Emergency Procedures

1. **Service Restart**
```bash
#!/bin/bash
# restart_service.sh
pkill -f streamlit
sleep 5
nohup streamlit run streamlit_app.py > /dev/null 2>&1 &
```

2. **Cache Reset**
```bash
#!/bin/bash
# reset_cache.sh
rm -rf .cache/*
rm -rf __pycache__/*
python -c "print('Cache cleared')"
```

## Security

### Access Control

1. **AWS IAM Policies**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

2. **Network Security**
- Use VPC endpoints
- Implement security groups
- Enable CloudTrail logging

### Data Protection

1. **Encryption**
   - Encrypt data at rest
   - Use TLS for data in transit
   - Secure API communications

2. **Privacy**
   - No PII storage
   - Secure file handling
   - Regular data cleanup

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
version: '3.8'
services:
  pptx-generator:
    build: .
    ports:
      - "8501-8510:8501"
    environment:
      - MAX_WORKERS=4
    deploy:
      replicas: 3
```

### Vertical Scaling

```bash
# Increase resources
export MAX_WORKERS=16
export MEMORY_LIMIT=8GB
```

## Backup and Recovery

### Backup Procedures

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d)
tar -czf backup_$DATE.tar.gz \
    config/ \
    logs/ \
    .cache/ \
    requirements.txt
```

### Recovery Procedures

```bash
#!/bin/bash
# restore.sh
tar -xzf backup_$1.tar.gz
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Performance Tuning

### Optimization Guidelines

1. **Cache Optimization**
   - Monitor hit rates
   - Adjust cache size
   - Optimize prompt structure

2. **Resource Optimization**
   - Tune worker count
   - Monitor memory usage
   - Optimize I/O operations

3. **Network Optimization**
   - Use connection pooling
   - Implement retry logic
   - Monitor API latency

### Configuration Tuning

```python
# config/optimization.py
OPTIMIZATION_CONFIG = {
    'cache': {
        'enabled': True,
        'size_limit': '1GB',
        'ttl': 300
    },
    'parallel': {
        'max_workers': 8,
        'timeout': 600
    },
    'quality': {
        'min_score': 0.7,
        'retry_threshold': 0.5
    }
}
```
