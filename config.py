import os

# AWS Configuration
AWS_CONFIG = {
    'region': os.getenv('AWS_REGION', 'us-east-1')
}

# AWS Secrets Manager Configuration
SECRETS_CONFIG = {
    'secret_name_cert': os.getenv('SECRET_NAME_CERT', 'kafka/client1/cert'),
    'secret_name_key': os.getenv('SECRET_NAME_KEY', 'kafka/client1/key')
}

# Certificate Configuration
CERT_CONFIG = {
    'ca_cert_path': os.getenv('CA_CERT_PATH', '/path/to/ca.crt'),
    'ca_key_path': os.getenv('CA_KEY_PATH', '/path/to/ca.key'),
    'validity_days': int(os.getenv('CERT_VALIDITY_DAYS', '365'))
}

# Certificate Subject Configuration
CERT_SUBJECT = {
    'common_name': os.getenv('COMMON_NAME', 'client1.example.com')
}

# Confluent Cloud Configuration
CONFLUENT_CONFIG = {
    'api_key': os.getenv('CONFLUENT_API_KEY'),
    'api_secret': os.getenv('CONFLUENT_API_SECRET'),
    'cloud_api_url': os.getenv('CONFLUENT_CLOUD_API', 'https://api.confluent.cloud/v2'),
    'identity_pool_name': os.getenv('IDENTITY_POOL_NAME', 'client1-pool')
}



# Required environment variables
REQUIRED_ENV_VARS = [
    'CONFLUENT_API_KEY',
    'CONFLUENT_API_SECRET',
    'CA_CERT_PATH',
    'CA_KEY_PATH'
]

def validate_config():
    """Validate that all required environment variables are set"""
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Validate file paths
    if not os.path.exists(CERT_CONFIG['ca_cert_path']):
        raise FileNotFoundError(f"CA certificate not found at: {CERT_CONFIG['ca_cert_path']}")
    if not os.path.exists(CERT_CONFIG['ca_key_path']):
        raise FileNotFoundError(f"CA key not found at: {CERT_CONFIG['ca_key_path']}")