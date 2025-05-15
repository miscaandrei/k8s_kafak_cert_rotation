# Kafka mTLS Certificate Rotation Script

This script automates the generation and rotation of certificates for Kafka mTLS authentication and stores them securely in AWS Secrets Manager. It also integrates with Confluent Cloud to create or update Workload Identity pools.

## Features

-   **Automated Certificate Generation**: Generates client certificates signed by a specified Certificate Authority (CA).
-   **Secure Secret Storage**: Stores the generated certificates and private keys securely in AWS Secrets Manager.
-   **Confluent Cloud Integration**: Creates or updates Workload Identity pools in Confluent Cloud, associating them with the generated certificates.
-   **Configuration via Environment Variables**: Uses environment variables for easy and secure configuration.
-   **AWS Credentials Handling**: Supports IAM roles, environment variables, and AWS CLI configuration for managing AWS credentials.
-   **Logging**: Provides detailed logging for monitoring and debugging.

## Prerequisites

-   Python 3.6+
-   `pip` package manager
-   AWS CLI (optional, for local configuration)
-   An AWS account with permissions to access Secrets Manager
-   A Confluent Cloud account with API key and secret

## Installation

1.  Clone the repository:

    ```bash
    git clone [repository URL]
    cd [repository directory]
    ```

2.  Install the required Python packages:

    ```bash
    pip install boto3 pyOpenSSL requests
    ```

## Configuration

The script is configured using environment variables. You can set these variables directly in your shell or use a `.env` file.

### Required Environment Variables

-   `CONFLUENT_API_KEY`: Your Confluent Cloud API key.
-   `CONFLUENT_API_SECRET`: Your Confluent Cloud API secret.
-   `CA_CERT_PATH`: Path to your Certificate Authority (CA) certificate file.
-   `CA_KEY_PATH`: Path to your CA private key file.

### Optional Environment Variables

-   `COMMON_NAME`: The Common Name (CN) for the generated certificate (default: `client1.example.com`).
-   `SECRET_NAME_CERT`: The name for the certificate secret in AWS Secrets Manager (default: `kafka/client1/cert`).
-   `SECRET_NAME_KEY`: The name for the private key secret in AWS Secrets Manager (default: `kafka/client1/key`).
-   `CONFLUENT_CLOUD_API`: The Confluent Cloud API endpoint (default: `https://api.confluent.cloud/v2`).
-   `IDENTITY_POOL_NAME`: The name for the Confluent Cloud Workload Identity pool (default: `client1-pool`).
-   `AWS_REGION`: The AWS region to use (default: `us-east-1`).
-   `CERT_VALIDITY_DAYS`: The validity period for the generated certificate, in days (default: `365`).

### Example `.env` file

CONFLUENT_API_KEY=your-confluent-api-key
CONFLUENT_API_SECRET=your-confluent-api-secret
CA_CERT_PATH=/path/to/ca.crt
CA_KEY_PATH=/path/to/ca.key
COMMON_NAME=client1.example.com
SECRET_NAME_CERT=kafka/client1/cert
SECRET_NAME_KEY=kafka/client1/key
CONFLUENT_CLOUD_API=https://api.confluent.cloud/v2
IDENTITY_POOL_NAME=client1-pool
AWS_REGION=us-east-1
CERT_VALIDITY_DAYS=365


## Usage

1.  Ensure all required environment variables are set.
2.  Run the script:

    ```bash
    python cert_rotation.py
    ```

    The script will:

    -   Generate a new client certificate.
    -   Store the certificate and private key in AWS Secrets Manager.
    -   Create or update a Workload Identity pool in Confluent Cloud.
    -   Log all actions to the console.

## File Structure

```
.
├── cert_rotation.py   # Main script
├── config.py          # Configuration file
├── LICENSE            # License agreement
└── README.md          # Documentation
```


## AWS IAM Permissions

The IAM user or role used to run this script requires the following permissions to interact with AWS Secrets Manager:

-   `secretsmanager:CreateSecret`
-   `secretsmanager:UpdateSecret`
-   `secretsmanager:PutSecretValue` (optional, for updating secret values)
-   `secretsmanager:GetSecretValue` (optional, for reading secrets)
-   `secretsmanager:DescribeSecret` (optional, for describing secrets)

If you are using a custom KMS key for encrypting your secrets, you will also need:

-   `kms:GenerateDataKey`
-   `kms:Decrypt`

### Example IAM Policy

Here's an example IAM policy that grants the necessary permissions. Replace `REGION`, `ACCOUNT_ID`, and `SECRET_NAME` with your actual values:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:UpdateSecret",
        "secretsmanager:PutSecretValue",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:SECRET_NAME*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:GenerateDataKey",
        "kms:Decrypt"
      ],
      "Resource": "YOUR_KMS_KEY_ARN"  # Required only if using a custom KMS key
    }
  ]
}
Note: It's recommended to grant the least privilege necessary. Limit the Resource to only the secrets your script will manage.


## Error Handling

The script includes error handling for common issues, such as:

-   Missing environment variables
-   Invalid file paths
-   AWS credentials issues
-   Confluent Cloud API errors

Check the console output for detailed error messages.

## AWS Credentials

The script uses the `boto3` library to handle AWS credentials. It supports the following methods for providing credentials:

1.  **IAM Roles (Recommended)**: If running on an EC2 instance or other AWS service, assign an IAM role with the necessary permissions to the instance.
2.  **Environment Variables**: Set the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.
3.  **AWS CLI Configuration**: Configure the AWS CLI using `aws configure`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.