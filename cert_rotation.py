import boto3
from OpenSSL import crypto
from datetime import datetime
import requests
import logging
from typing import Dict, Tuple
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AWSCredentialsError(Exception):
    """Custom exception for AWS credentials issues"""
    pass

def get_aws_session(region_name: str = 'us-east-1') -> boto3.Session:
    """
    Create an AWS session using the available credentials
    """
    try:
        session = boto3.Session(region_name=region_name)
        # Verify the session has credentials
        credentials = session.get_credentials()
        if credentials is None:
            raise AWSCredentialsError("No AWS credentials found")

        # Test the credentials
        sts = session.client('sts')
        sts.get_caller_identity()

        return session

    except Exception as e:
        logger.error(f"Error creating AWS session: {str(e)}")
        raise AWSCredentialsError(f"Failed to create AWS session: {str(e)}")

def generate_certificate(common_name: str, ca_cert_path: str, ca_key_path: str, validity_days: int = 365) -> Tuple[str, str]:
    """
    Generate a client certificate signed by the CA
    """
    try:
        # Load the CA certificate and private key
        with open(ca_cert_path, 'rb') as ca_cert_file:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_file.read())
        with open(ca_key_path, 'rb') as ca_key_file:
            ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, ca_key_file.read())

        # Generate key pair for client
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        # Generate certificate request
        cert = crypto.X509()
        cert.get_subject().CN = common_name
        cert.set_serial_number(int(datetime.now().timestamp()))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(validity_days * 24 * 60 * 60)
        cert.set_issuer(ca_cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(ca_key, 'sha256')

        # Convert to PEM format
        cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

        return cert_pem.decode('utf-8'), key_pem.decode('utf-8')

    except Exception as e:
        logger.error(f"Error generating certificate: {str(e)}")
        raise

def store_in_secret_manager(secret_name: str, secret_value: str, aws_session: boto3.Session) -> Dict:
    """
    Store a secret in AWS Secret Manager
    """
    client = aws_session.client('secretsmanager')

    try:
        try:
            response = client.create_secret(
                Name=secret_name,
                SecretString=secret_value
            )
            logger.info(f"Created new secret: {secret_name}")
        except client.exceptions.ResourceExistsException:
            response = client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )
            logger.info(f"Updated existing secret: {secret_name}")

        return response

    except Exception as e:
        logger.error(f"Error storing secret in Secret Manager: {str(e)}")
        raise

def create_confluent_identity_pool(api_key: str, api_secret: str, cloud_api_url: str,
                                 identity_pool_name: str, common_name: str) -> Dict:
    """
    Create an identity pool in Confluent Cloud
    """
    headers = {
        'Content-Type': 'application/json'
    }

    auth = (api_key, api_secret)

    payload = {
        "display_name": identity_pool_name,
        "identity_claim": common_name
    }

    try:
        response = requests.post(
            f"{cloud_api_url}/identity-pools",
            headers=headers,
            auth=auth,
            json=payload
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating Confluent identity pool: {str(e)}")
        raise

def main():
    try:
        # Validate configuration
        config.validate_config()

        # Initialize AWS session
        logger.info("Initializing AWS session...")
        aws_session = get_aws_session(region_name=config.AWS_CONFIG['region'])

        # Generate certificate
        logger.info("Generating certificate...")
        cert_pem, key_pem = generate_certificate(
            config.CERT_SUBJECT['common_name'],
            config.CERT_CONFIG['ca_cert_path'],
            config.CERT_CONFIG['ca_key_path'],
            config.CERT_CONFIG['validity_days']
        )

        # Store certificate and key in Secret Manager
        logger.info("Storing certificate and key in Secret Manager...")
        store_in_secret_manager(config.SECRETS_CONFIG['secret_name_cert'], cert_pem, aws_session)
        store_in_secret_manager(config.SECRETS_CONFIG['secret_name_key'], key_pem, aws_session)

        # Create Confluent Cloud Identity Pool
        logger.info("Creating Confluent Cloud Identity Pool...")
        create_confluent_identity_pool(
            config.CONFLUENT_CONFIG['api_key'],
            config.CONFLUENT_CONFIG['api_secret'],
            config.CONFLUENT_CONFIG['cloud_api_url'],
            config.CONFLUENT_CONFIG['identity_pool_name'],
            config.CERT_SUBJECT['common_name']
        )

        logger.info("Certificate rotation completed successfully!")

    except Exception as e:
        logger.error(f"Error occurred during certificate rotation: {str(e)}")
        raise

if __name__ == "__main__":
    main()