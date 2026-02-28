"""Configuration settings for AWS Bedrock Application Inference Profiles."""

# AWS Region configuration
REGION = "us-west-2"

# Model IDs for Anthropic Claude models on Bedrock
class ModelId:
    """Claude model IDs available on AWS Bedrock."""

    # Claude 4.x models
    CLAUDE_OPUS_4_6 = "anthropic.claude-opus-4-6-v1"
    CLAUDE_SONNET_4_6 = "anthropic.claude-sonnet-4-6"
    CLAUDE_HAIKU_4_5 = "anthropic.claude-haiku-4-5-20251001-v1:0"

    # Claude 3.x models
    CLAUDE_3_5_SONNET_V2 = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    CLAUDE_3_5_HAIKU = "anthropic.claude-3-5-haiku-20241022-v1:0"
    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"

    # System inference profiles (for creating AIPs)
    SYSTEM_PROFILE_SONNET = "us.anthropic.claude-sonnet-4-6"
    SYSTEM_PROFILE_HAIKU = "us.anthropic.claude-haiku-4-5-20251001-v1"

    # Default system profile to copy from
    DEFAULT = SYSTEM_PROFILE_SONNET


# Inference configuration defaults
class InferenceConfig:
    """Default inference configuration parameters."""

    MAX_TOKENS = 2048
    TEMPERATURE = 1.0
    TOP_P = 0.999
    TOP_K = 250

    @classmethod
    def get_default_config(cls):
        """Return default inference configuration."""
        return {
            "maxTokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE,
            "topP": cls.TOP_P
        }


# Default tenant configurations
TENANT_CONFIGS = {
    "tenant_a": {
        "profile_name": "aip-tenant-a-marketing",
        "description": "Application Inference Profile for Tenant A (Marketing)",
        "tags": [
            {"key": "tenant", "value": "tenant_a"},
            {"key": "department", "value": "marketing"},
            {"key": "costcenter", "value": "marketing-ops"},
            {"key": "environment", "value": "production"},
            {"key": "application", "value": "marketing-ai"}
        ]
    },
    "tenant_b": {
        "profile_name": "aip-tenant-b-sales",
        "description": "Application Inference Profile for Tenant B (Sales)",
        "tags": [
            {"key": "tenant", "value": "tenant_b"},
            {"key": "department", "value": "sales"},
            {"key": "costcenter", "value": "sales-ops"},
            {"key": "environment", "value": "production"},
            {"key": "application", "value": "sales-ai"}
        ]
    },
    "tenant_c": {
        "profile_name": "aip-tenant-c-engineering",
        "description": "Application Inference Profile for Tenant C (Engineering)",
        "tags": [
            {"key": "tenant", "value": "tenant_c"},
            {"key": "department", "value": "engineering"},
            {"key": "costcenter", "value": "engineering-ops"},
            {"key": "environment", "value": "production"},
            {"key": "application", "value": "dev-assistant"}
        ]
    }
}


# Sample prompts for testing
class TestPrompts:
    """Sample prompts for testing inference profiles."""

    SIMPLE = "Hello! How are you today?"

    MARKETING = "Generate a brief marketing campaign for a B2B SaaS DevOps automation platform targeting CTOs."

    SALES = "Create a sales pitch for enterprise cloud migration services."

    ENGINEERING = "Write a Python function to calculate the Fibonacci sequence."

    ANALYTICS = "Analyze the key trends in artificial intelligence adoption in 2024."

    CREATIVE = "Write a haiku about cloud computing."


# CloudWatch configuration
class CloudWatchConfig:
    """CloudWatch metrics configuration."""

    NAMESPACE = "AWS/Bedrock"

    # Metric names
    METRICS = {
        "INVOCATIONS": "Invocations",
        "INPUT_TOKENS": "InputTokenCount",
        "OUTPUT_TOKENS": "OutputTokenCount",
        "LATENCY": "InvocationLatency",
        "THROTTLED": "ThrottledCount",
        "ERRORS": "InvocationClientErrors"
    }

    # Default metric period (seconds)
    PERIOD = 60

    # Default lookback window (minutes)
    LOOKBACK_MINUTES = 15