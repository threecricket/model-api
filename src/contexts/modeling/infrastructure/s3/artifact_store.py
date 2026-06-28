import json
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from bootstrap.settings import Settings
from contexts.modeling.domain.errors import ArtifactNotFoundError
from contexts.modeling.domain.models.trained_model_ref import TrainedModelRef
from contexts.modeling.domain.ports.artifact_store import ArtifactMetadata, TrainedInstanceSummary


class S3ArtifactStore:
    def __init__(self, settings: Settings) -> None:
        self._bucket = settings.s3_bucket
        self._prefix = settings.s3_prefix.rstrip("/")
        self._client = self._create_client(settings)
        self._cache: dict[tuple[str, str], tuple[bytes, ArtifactMetadata]] = {}

    def save(self, ref: TrainedModelRef, data: bytes, metadata: ArtifactMetadata) -> str:
        base_key = self._instance_prefix(ref)
        timestamp = metadata.trained_at.strftime("%Y%m%dT%H%M%SZ")
        versioned_key = f"{base_key}/{timestamp}.pkl"
        latest_key = f"{base_key}/latest.pkl"
        metadata_key = f"{base_key}/latest.metadata.json"

        self._client.put_object(Bucket=self._bucket, Key=versioned_key, Body=data)
        self._client.put_object(Bucket=self._bucket, Key=latest_key, Body=data)
        self._client.put_object(
            Bucket=self._bucket,
            Key=metadata_key,
            Body=json.dumps(self._metadata_to_dict(metadata)).encode(),
            ContentType="application/json",
        )

        self.invalidate_cache(ref)
        return f"s3://{self._bucket}/{latest_key}"

    def load(self, ref: TrainedModelRef) -> tuple[bytes, ArtifactMetadata]:
        cache_key = (ref.model_name, ref.filter_key.value)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        base_key = self._instance_prefix(ref)
        latest_key = f"{base_key}/latest.pkl"
        metadata_key = f"{base_key}/latest.metadata.json"

        try:
            artifact_response = self._client.get_object(Bucket=self._bucket, Key=latest_key)
            metadata_response = self._client.get_object(Bucket=self._bucket, Key=metadata_key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"404", "NoSuchKey", "NotFound"}:
                raise ArtifactNotFoundError(ref.model_name, ref.filter_key.value) from exc
            raise

        data = artifact_response["Body"].read()
        metadata = self._metadata_from_dict(json.loads(metadata_response["Body"].read()))
        result = (data, metadata)
        self._cache[cache_key] = result
        return result

    def exists(self, ref: TrainedModelRef) -> bool:
        latest_key = f"{self._instance_prefix(ref)}/latest.pkl"
        try:
            self._client.head_object(Bucket=self._bucket, Key=latest_key)
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise

    def list_instances(self, model_name: str | None = None) -> list[TrainedInstanceSummary]:
        prefix = f"{self._prefix}/"
        if model_name:
            prefix = f"{self._prefix}/{model_name}/"

        summaries: list[TrainedInstanceSummary] = []
        paginator = self._client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if not key.endswith("/latest.metadata.json"):
                    continue

                metadata_response = self._client.get_object(Bucket=self._bucket, Key=key)
                metadata = self._metadata_from_dict(json.loads(metadata_response["Body"].read()))
                base_key = key.removesuffix("/latest.metadata.json")
                summaries.append(
                    TrainedInstanceSummary(
                        model_name=metadata.model_name,
                        filter_key=metadata.filter_key,
                        trained_at=metadata.trained_at,
                        metrics=metadata.metrics,
                        artifact_uri=f"s3://{self._bucket}/{base_key}/latest.pkl",
                        row_count=metadata.row_count,
                    )
                )

        return sorted(summaries, key=lambda item: (item.model_name, item.filter_key))

    def invalidate_cache(self, ref: TrainedModelRef) -> None:
        self._cache.pop((ref.model_name, ref.filter_key.value), None)

    def _instance_prefix(self, ref: TrainedModelRef) -> str:
        return f"{self._prefix}/{ref.model_name}/{ref.filter_key.value}"

    @staticmethod
    def _create_client(settings: Settings):
        if settings.aws_role_arn:
            session = boto3.Session(
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
            assumed = session.client("sts").assume_role(
                RoleArn=settings.aws_role_arn,
                RoleSessionName="model-api",
            )
            credentials = assumed["Credentials"]
            return boto3.client(
                "s3",
                region_name=settings.aws_region,
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
            )

        kwargs: dict = {"region_name": settings.aws_region}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws_access_key_id
            kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        return boto3.client("s3", **kwargs)

    @staticmethod
    def _metadata_to_dict(metadata: ArtifactMetadata) -> dict:
        return {
            "model_name": metadata.model_name,
            "filter_key": metadata.filter_key,
            "filters": metadata.filters,
            "model_type": metadata.model_type,
            "features": metadata.features,
            "metrics": metadata.metrics,
            "row_count": metadata.row_count,
            "trained_at": metadata.trained_at.isoformat(),
            "extra": metadata.extra,
        }

    @staticmethod
    def _metadata_from_dict(data: dict) -> ArtifactMetadata:
        trained_at = data["trained_at"]
        if isinstance(trained_at, str):
            trained_at = datetime.fromisoformat(trained_at)
            if trained_at.tzinfo is None:
                trained_at = trained_at.replace(tzinfo=timezone.utc)

        return ArtifactMetadata(
            model_name=data["model_name"],
            filter_key=data["filter_key"],
            filters=data.get("filters", {}),
            model_type=data["model_type"],
            features=list(data.get("features", [])),
            metrics={key: float(value) for key, value in data.get("metrics", {}).items()},
            row_count=int(data.get("row_count", 0)),
            trained_at=trained_at,
            extra=data.get("extra", {}),
        )
