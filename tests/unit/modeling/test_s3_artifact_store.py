from unittest.mock import MagicMock, patch

from bootstrap.settings import Settings
from contexts.modeling.infrastructure.s3.artifact_store import S3ArtifactStore


class TestS3ArtifactStoreClient:
    @patch("contexts.modeling.infrastructure.s3.artifact_store.boto3")
    def test_create_client_assumes_role_when_role_arn_set(self, mock_boto3):
        settings = Settings(
            database_url="postgresql://user:pass@localhost/db",
            s3_bucket="bucket",
            aws_region="eu-west-1",
            aws_role_arn="arn:aws:iam::123456789012:role/models-api-role",
            aws_access_key_id="base-key",
            aws_secret_access_key="base-secret",
        )

        mock_session = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_sts = MagicMock()
        mock_session.client.return_value = mock_sts
        mock_sts.assume_role.return_value = {
            "Credentials": {
                "AccessKeyId": "temp-key",
                "SecretAccessKey": "temp-secret",
                "SessionToken": "temp-token",
            }
        }
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3

        client = S3ArtifactStore._create_client(settings)

        mock_boto3.Session.assert_called_once_with(
            region_name="eu-west-1",
            aws_access_key_id="base-key",
            aws_secret_access_key="base-secret",
        )
        mock_session.client.assert_called_once_with("sts")
        mock_sts.assume_role.assert_called_once_with(
            RoleArn="arn:aws:iam::123456789012:role/models-api-role",
            RoleSessionName="model-api",
        )
        mock_boto3.client.assert_called_once_with(
            "s3",
            region_name="eu-west-1",
            aws_access_key_id="temp-key",
            aws_secret_access_key="temp-secret",
            aws_session_token="temp-token",
        )
        assert client is mock_s3

    @patch("contexts.modeling.infrastructure.s3.artifact_store.boto3")
    def test_create_client_uses_access_keys_when_no_role_arn(self, mock_boto3):
        settings = Settings(
            database_url="postgresql://user:pass@localhost/db",
            s3_bucket="bucket",
            aws_region="eu-west-1",
            aws_role_arn=None,
            aws_access_key_id="direct-key",
            aws_secret_access_key="direct-secret",
        )

        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3

        client = S3ArtifactStore._create_client(settings)

        mock_boto3.Session.assert_not_called()
        mock_boto3.client.assert_called_once_with(
            "s3",
            region_name="eu-west-1",
            aws_access_key_id="direct-key",
            aws_secret_access_key="direct-secret",
        )
        assert client is mock_s3
