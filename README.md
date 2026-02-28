# AWS Bedrock Application Inference Profiles (AIP)

A comprehensive solution for implementing multi-tenant architectures with Amazon Bedrock using Application Inference Profiles. This repository provides tools for creating, managing, and monitoring tenant-specific inference profiles with cost allocation and usage tracking.

## 🎯 What are Application Inference Profiles?

Application Inference Profiles (AIPs) are a feature of Amazon Bedrock that enables:
- **Multi-tenant isolation**: Separate inference profiles per tenant
- **Cost attribution**: Track usage and costs per tenant/department
- **Usage monitoring**: CloudWatch metrics per profile
- **Tag-based management**: Organize profiles with custom tags
- **Quota enforcement**: Set limits per profile (when combined with CCWB)

## 🚀 Features

- **Multi-Tenant Support**: Create isolated profiles for different tenants
- **CloudWatch Integration**: Automatic metrics per profile
- **Cost Tracking**: Tag-based cost allocation
- **Simple API**: Easy-to-use Python scripts
- **Visualization Tools**: Generate usage charts and reports
- **Testing Suite**: Validate profile separation

## 📋 Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured (`aws configure`)
- Python 3.8+ installed
- boto3 and matplotlib libraries
- Access to Claude models in Amazon Bedrock

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/cmsrb4u/aws-bedrock-application-inference-profile.git
cd aws-bedrock-application-inference-profile
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Region
Edit `config/settings.py` to set your preferred AWS region (default: us-west-2)

## 🚀 Quick Start

### 1. Create Tenant Profiles
```bash
python scripts/create_tenant_profiles.py
```

This creates two example profiles:
- `aip-tenant-a-marketing` (Marketing Department)
- `aip-tenant-b-sales` (Sales Department)

### 2. Test Profile Separation
```bash
python scripts/test_profiles.py
```

### 3. Generate Metrics and Visualizations
```bash
python scripts/invoke_and_visualize.py
```

## 📁 Repository Structure

```
aws-bedrock-application-inference-profile/
├── README.md                    # Main documentation
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── config/                     # Configuration files
│   ├── settings.py            # AWS settings and model IDs
│   └── tenant_config.json    # Tenant profile definitions
│
├── scripts/                    # Main scripts
│   ├── setup_aip.py          # Initialize AIP environment
│   ├── create_tenant_profiles.py  # Create multi-tenant profiles
│   ├── list_profiles.py      # List existing profiles
│   ├── delete_profiles.py    # Clean up profiles
│   └── invoke_and_visualize.py   # Generate metrics
│
├── tests/                      # Test scripts
│   ├── test_profiles.py      # Test profile separation
│   └── test_metrics.py       # Validate CloudWatch metrics
│
├── examples/                   # Example implementations
│   ├── multi_tenant_demo.py  # Complete multi-tenant demo
│   └── cost_analysis.py      # Cost tracking example
│
└── docs/                       # Documentation
    ├── ARCHITECTURE.md        # System architecture
    ├── API_REFERENCE.md       # API documentation
    └── TROUBLESHOOTING.md     # Common issues and solutions
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Application   │────▶│  AIP for Tenant  │────▶│  Claude Models   │
│   (Tenant A)    │     │        A         │     │   on Bedrock     │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   CloudWatch     │
                        │  Metrics (A)     │
                        └──────────────────┘

┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Application   │────▶│  AIP for Tenant  │────▶│  Claude Models   │
│   (Tenant B)    │     │        B         │     │   on Bedrock     │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   CloudWatch     │
                        │  Metrics (B)     │
                        └──────────────────┘
```

## 📊 CloudWatch Metrics

Each Application Inference Profile publishes the following metrics:

| Metric Name | Description | Unit | Dimension |
|------------|-------------|------|-----------|
| Invocations | Number of inference calls | Count | InferenceProfileId |
| InputTokenCount | Input tokens processed | Count | InferenceProfileId |
| OutputTokenCount | Output tokens generated | Count | InferenceProfileId |
| InvocationLatency | Response time | Milliseconds | InferenceProfileId |
| ThrottledCount | Throttled requests | Count | InferenceProfileId |

## 🏷️ Tagging Strategy

Recommended tags for cost allocation:

```python
tags = [
    {"key": "tenant", "value": "tenant_name"},
    {"key": "department", "value": "department_name"},
    {"key": "costcenter", "value": "cost_center_id"},
    {"key": "environment", "value": "production"},
    {"key": "application", "value": "app_name"}
]
```

## 💰 Cost Tracking

View costs per profile in AWS Cost Explorer:
1. Navigate to Cost Explorer
2. Filter by tag: `tenant`
3. Group by: `Service` and `Tag`
4. View Bedrock costs per tenant

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/
```

### Test Specific Profile
```bash
python tests/test_profiles.py --tenant tenant_a
```

## 📝 Usage Examples

### Create a Custom Profile

```python
import boto3

bedrock = boto3.client('bedrock', region_name='us-west-2')

response = bedrock.create_inference_profile(
    inferenceProfileName='my-custom-profile',
    modelSource={
        'copyFrom': 'arn:aws:bedrock:us-west-2::inference-profile/us.anthropic.claude-sonnet-4-6'
    },
    tags=[
        {"key": "department", "value": "engineering"},
        {"key": "project", "value": "chatbot"}
    ]
)

print(f"Created profile: {response['inferenceProfileArn']}")
```

### Make Inference Call with Profile

```python
import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

response = bedrock_runtime.invoke_model(
    modelId='arn:aws:bedrock:us-west-2:123456789012:inference-profile/my-custom-profile',
    body=json.dumps({
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": "Hello!"}]
        }],
        "max_tokens": 100,
        "anthropic_version": "bedrock-2023-05-31"
    })
)

result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

## 🔍 Monitoring

### CloudWatch Dashboard
A CloudWatch dashboard is automatically created showing:
- Invocations per profile
- Token usage per profile
- Error rates
- Latency metrics

### Alarms
Set up alarms for:
- High token usage
- Error rate thresholds
- Latency spikes

## 🛠️ Troubleshooting

### Common Issues

1. **Profile Creation Fails**
   - Verify Bedrock model access
   - Check IAM permissions
   - Ensure unique profile names

2. **No Metrics in CloudWatch**
   - Wait 3-5 minutes for propagation
   - Verify profile ARN in calls
   - Check CloudWatch permissions

3. **Access Denied Errors**
   - Verify IAM role has `bedrock:*` permissions
   - Check model access in Bedrock console

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- AWS Bedrock team for Application Inference Profiles
- Based on AWS best practices for multi-tenant architectures

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Check the [troubleshooting guide](docs/TROUBLESHOOTING.md)
- Review AWS Bedrock documentation

## 🔗 Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Application Inference Profiles Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/application-inference-profiles.html)
- [CloudWatch Metrics for Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-cloudwatch.html)
- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)