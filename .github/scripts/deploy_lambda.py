#!/usr/bin/env python3
"""Deploy a Lambda container image and sync runtime env vars from Secrets Manager."""

from __future__ import annotations

import argparse
import json
import sys

import boto3
from botocore.exceptions import ClientError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy Lambda image and sync environment from Secrets Manager.",
    )
    parser.add_argument("--function-name", required=True)
    parser.add_argument("--image-uri", required=True)
    parser.add_argument(
        "--secret-id",
        help="Secrets Manager secret id or ARN (defaults to the function name)",
    )
    parser.add_argument("--region", help="AWS region (defaults to the boto3 session region)")
    return parser.parse_args()


def load_env_from_secret(
    secrets_client,
    secret_id: str,
    function_name: str,
) -> dict[str, str]:
    response = secrets_client.get_secret_value(SecretId=secret_id)
    raw = response.get("SecretString")
    if not raw:
        raise ValueError(f"Secret {secret_id} has no SecretString value")

    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Secret {secret_id} must contain a JSON object")

    env = {str(key): str(value) for key, value in data.items() if value not in (None, "")}
    env.setdefault("S3_BUCKET", f"{function_name}-artifacts")
    env.setdefault("S3_PREFIX", "models")

    if "DATABASE_URL" not in env:
        raise ValueError("Secret must include DATABASE_URL")

    return env


def wait_for_lambda(lambda_client, function_name: str) -> None:
    lambda_client.get_waiter("function_updated").wait(FunctionName=function_name)


def main() -> int:
    args = parse_args()
    secret_id = args.secret_id or args.function_name

    session = boto3.session.Session(region_name=args.region)
    lambda_client = session.client("lambda")
    secrets_client = session.client("secretsmanager")

    print(f"Loading environment from secret {secret_id}...")
    env_vars = load_env_from_secret(secrets_client, secret_id, args.function_name)

    print(f"Updating Lambda {args.function_name} image...")
    lambda_client.update_function_code(
        FunctionName=args.function_name,
        ImageUri=args.image_uri,
    )
    wait_for_lambda(lambda_client, args.function_name)

    print(f"Updating Lambda {args.function_name} environment...")
    lambda_client.update_function_configuration(
        FunctionName=args.function_name,
        Environment={"Variables": env_vars},
    )
    wait_for_lambda(lambda_client, args.function_name)

    print("Deploy complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ClientError, ValueError, json.JSONDecodeError) as exc:
        print(f"Deploy failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
