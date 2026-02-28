# Complete Installation Guide

This guide provides comprehensive installation instructions for AWS Bedrock Application Inference Profiles (AIP) and the optional Claude Code with Bedrock (CCWB) integration.

## 📋 Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured (`aws configure`)
- Python 3.8+ installed
- Git installed

## 🚀 Quick Start (Basic AIP Only)

If you only need Application Inference Profiles without quota management:

```bash
# Clone this repository
git clone https://github.com/cmsrb4u/aws-bedrock-application-inference-profile.git
cd aws-bedrock-application-inference-profile

# Install dependencies
pip install -r requirements.txt

# Run setup
python scripts/setup_aip.py
```

## 🔧 Complete Installation (AIP + CCWB Quota Management)

For the full solution with user-level quota management, follow these steps:

### Step 1: Install Poetry (Optional but Recommended)

Poetry provides better dependency management for Python projects.

#### Ubuntu/Debian:
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

#### macOS (with Homebrew):
```bash
brew install poetry
```

#### Verify Installation:
```bash
poetry --version
```

### Step 2: Install CCWB CLI

Choose one of these methods:

#### Method A: Install from PyPI (Simplest)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install CCWB
pip install git+https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock.git#subdirectory=source
```

#### Method B: Install with Poetry (Development)
```bash
# Clone CCWB repository
git clone https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock.git
cd guidance-for-claude-code-with-amazon-bedrock

# Checkout stable version
git checkout v2.2.0

# Navigate to source
cd source

# Install with Poetry
poetry install

# Use CCWB
poetry run ccwb --version
```

### Step 3: Verify CCWB Installation

```bash
# Check version
ccwb --version

# List available commands
ccwb list

# Show help
ccwb --help
```

### Step 4: Install AIP Repository

```bash
# Clone AIP repository
git clone https://github.com/cmsrb4u/aws-bedrock-application-inference-profile.git
cd aws-bedrock-application-inference-profile

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Install CCWB Quota Monitoring

```bash
# Clone quota monitoring repository
git clone https://github.com/cmsrb4u/aws-Claude-Code-Quota-Monitoring.git
cd aws-Claude-Code-Quota-Monitoring

# Install dependencies
pip install -r requirements.txt

# Deploy infrastructure
python scripts/setup_complete.py
```

## 📦 Installation Options Summary

| Component | Required | Purpose | Installation |
|-----------|----------|---------|--------------|
| **AIP Scripts** | ✅ Yes | Create & manage inference profiles | `pip install -r requirements.txt` |
| **Poetry** | ⭕ Optional | Better dependency management | `curl -sSL https://install.python-poetry.org \| python3 -` |
| **CCWB CLI** | ⭕ Optional | Full CCWB features | `pip install git+...` or `poetry install` |
| **Quota Monitoring** | ⭕ Optional | User-level quotas | Clone & run setup_complete.py |

## 🔍 Troubleshooting

### Poetry Installation Issues

If poetry command not found:
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### CCWB Installation Issues

If CCWB v2.2.0 has issues with quota commands:
1. Edit `source/claude_code_with_bedrock/cli/commands/quota.py` line 987
2. Change `required=False` to `optional=True`
3. Reinstall

### Virtual Environment Issues

Always use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### AWS Credentials

Ensure AWS CLI is configured:
```bash
aws configure
aws sts get-caller-identity  # Verify credentials
```

## 🎯 What to Install When

### Scenario 1: Basic Multi-Tenant Setup
- ✅ Install: AIP repository only
- ⭕ Skip: Poetry, CCWB CLI, Quota Monitoring

### Scenario 2: Development Environment
- ✅ Install: Everything with Poetry
- ✅ Use: Poetry for all Python projects

### Scenario 3: Production with Quotas
- ✅ Install: AIP + Quota Monitoring
- ⭕ Optional: CCWB CLI (if using full CCWB features)

### Scenario 4: Enterprise CCWB Deployment
- ✅ Install: Everything
- ✅ Configure: OIDC authentication
- ✅ Deploy: All CCWB stacks

## 📚 Next Steps

After installation:

1. **For AIP only:**
   ```bash
   python scripts/create_tenant_profiles.py
   python tests/test_profiles.py
   ```

2. **For AIP + Quota Monitoring:**
   ```bash
   # Create profiles
   python scripts/create_tenant_profiles.py

   # Deploy quota infrastructure
   cd ../aws-Claude-Code-Quota-Monitoring
   python scripts/setup_complete.py
   python scripts/create_dashboard.py
   ```

3. **For Full CCWB:**
   ```bash
   ccwb init          # Initialize configuration
   ccwb deploy auth   # Deploy authentication
   ccwb deploy quota  # Deploy quota monitoring
   ccwb status        # Check deployment
   ```

## 🔗 Resources

- [AIP Repository](https://github.com/cmsrb4u/aws-bedrock-application-inference-profile)
- [CCWB Quota Monitoring](https://github.com/cmsrb4u/aws-Claude-Code-Quota-Monitoring)
- [Official CCWB](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)