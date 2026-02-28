# Complete Setup Guide for AWS Bedrock Application Inference Profiles

This guide covers ALL the steps needed to successfully set up and use Application Inference Profiles, including AWS account preparation, permissions, and Bedrock enablement.

## 🔐 Step 1: AWS Account Setup

### 1.1 Enable Amazon Bedrock

1. **Sign in to AWS Console**: https://console.aws.amazon.com/
2. **Navigate to Amazon Bedrock**:
   - Search for "Bedrock" in the search bar
   - Select "Amazon Bedrock"
3. **Enable Bedrock** (if not already enabled):
   - Click "Get started" or "Manage model access"
   - Select your region (recommended: `us-west-2`)

### 1.2 Request Model Access

**IMPORTANT**: You must request access to Claude models before you can use them.

1. In Bedrock console, go to **"Model access"** (left sidebar)
2. Click **"Manage model access"** button
3. Find and select these models:
   - ✅ Claude Sonnet 4.6 (`anthropic.claude-sonnet-4-6`)
   - ✅ Claude Haiku 4.5 (`anthropic.claude-haiku-4-5`)
   - ✅ Claude 3.5 Sonnet (optional)
   - ✅ Claude 3 Opus (optional)
4. Click **"Request model access"**
5. Wait for approval (usually instant for Claude models)
6. Verify status shows **"Access granted"**

### 1.3 Verify Model Access

```bash
# List available models
aws bedrock list-foundation-models \
  --region us-west-2 \
  --query "modelSummaries[?contains(modelId, 'claude')].[modelId,modelName]" \
  --output table
```

## 🔑 Step 2: IAM Permissions Setup

### 2.1 Required IAM Permissions

Your AWS user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockFullAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchMetrics",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "cloudwatch:GetMetricData"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchDashboards",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutDashboard",
        "cloudwatch:GetDashboard",
        "cloudwatch:ListDashboards",
        "cloudwatch:DeleteDashboards"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMRoleAccess",
      "Effect": "Allow",
      "Action": [
        "iam:GetRole",
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::*:role/CCWB-*"
    }
  ]
}
```

### 2.2 Create IAM Policy

```bash
# Save the above JSON as bedrock-aip-policy.json
aws iam create-policy \
  --policy-name BedrockAIPAccess \
  --policy-document file://bedrock-aip-policy.json
```

### 2.3 Attach to Your User/Role

```bash
# For IAM user
aws iam attach-user-policy \
  --user-name YOUR_USERNAME \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAIPAccess

# For IAM role
aws iam attach-role-policy \
  --role-name YOUR_ROLE_NAME \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockAIPAccess
```

## 🖥️ Step 3: Environment Setup

### 3.1 Install AWS CLI

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download from: https://aws.amazon.com/cli/
```

### 3.2 Configure AWS CLI

```bash
# Configure credentials
aws configure

# Enter when prompted:
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: us-west-2
Default output format: json
```

### 3.3 Verify AWS Setup

```bash
# Verify credentials are working
aws sts get-caller-identity

# Should return:
{
    "UserId": "AIDAXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}

# Verify Bedrock access
aws bedrock list-inference-profiles --region us-west-2
```

### 3.4 Set Environment Variables

```bash
# Add to your ~/.bashrc or ~/.zshrc
export AWS_REGION=us-west-2
export AWS_DEFAULT_REGION=us-west-2

# Apply changes
source ~/.bashrc  # or source ~/.zshrc
```

## 🐍 Step 4: Python Environment Setup

### 4.1 Create Virtual Environment

```bash
# Navigate to the repository
cd aws-bedrock-application-inference-profile

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
which python
# Should show: /path/to/your/project/venv/bin/python
```

### 4.2 Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Verify installation
pip list | grep boto3
# Should show: boto3 1.26.0 or higher
```

### 4.3 Verify Python Setup

```python
# Test imports
python -c "import boto3; print(f'boto3 version: {boto3.__version__}')"
python -c "import matplotlib; print(f'matplotlib version: {matplotlib.__version__}')"
```

## ✅ Step 5: Validate Setup

### 5.1 Run Setup Validation Script

```bash
python scripts/setup_aip.py
```

Expected output:
```
✅ Bedrock Client initialized
   Region: us-west-2
   Service: bedrock (for AIP management)

✅ Bedrock Runtime Client initialized
   Region: us-west-2
   Service: bedrock-runtime (for model inference)

✅ Successfully connected to Bedrock
   Found X system profiles

✅ System profile found
   ARN: arn:aws:bedrock:us-west-2::inference-profile/us.anthropic.claude-sonnet-4-6
```

### 5.2 Common Setup Issues

#### Issue: "Could not connect to Bedrock"
**Solution**: Check AWS region and credentials
```bash
aws configure get region
aws sts get-caller-identity
```

#### Issue: "No system profiles found"
**Solution**: Ensure Bedrock is enabled and models are accessible
```bash
aws bedrock list-foundation-models --region us-west-2 --query 'modelSummaries[0]'
```

#### Issue: "Access Denied"
**Solution**: Check IAM permissions
```bash
aws iam get-user-policy --user-name YOUR_USERNAME --policy-name BedrockAIPAccess
```

## 🚀 Step 6: Create Your First Profile

Once setup is validated:

```bash
# Create tenant profiles
python scripts/create_tenant_profiles.py

# Test the profiles
python tests/test_profiles.py

# List all profiles
python scripts/list_profiles.py
```

## 📊 Step 7: Optional - Set Up Monitoring

### 7.1 Create CloudWatch Alarms

```bash
# Create alarms for high usage
aws cloudwatch put-metric-alarm \
  --alarm-name "AIP-HighTokenUsage" \
  --alarm-description "Alert when token usage is high" \
  --metric-name InputTokenCount \
  --namespace AWS/Bedrock \
  --statistic Sum \
  --period 3600 \
  --threshold 1000000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --region us-west-2
```

### 7.2 Create Cost Budget

```bash
# Create budget for Bedrock costs
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget-config.json \
  --notifications-with-subscribers file://notifications.json
```

## 📝 Environment Configuration File

Create `.env` file in the project root:

```bash
# .env
AWS_REGION=us-west-2
AWS_DEFAULT_REGION=us-west-2
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6
LOG_LEVEL=INFO
```

## 🎯 Quick Validation Checklist

Before running the main scripts, ensure:

- [ ] AWS CLI is installed and configured
- [ ] AWS credentials are valid (`aws sts get-caller-identity`)
- [ ] Amazon Bedrock is enabled in your AWS account
- [ ] Claude models show "Access granted" in Bedrock console
- [ ] Python 3.8+ is installed
- [ ] Virtual environment is activated
- [ ] All dependencies are installed (`pip install -r requirements.txt`)
- [ ] AWS_REGION is set to us-west-2
- [ ] IAM permissions include bedrock:* and cloudwatch:* actions
- [ ] setup_aip.py runs without errors

## 🔗 Useful Links

- [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
- [Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
- [IAM Policies for Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)
- [Application Inference Profiles Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/application-inference-profiles.html)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Review AWS CloudTrail logs for API errors
4. Open an issue on GitHub with error details