import json
import logging
import os
import urllib.parse
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def extract_project_id_from_key(key: str) -> str | None:
    
    parts = key.split("/")
    if len(parts) < 3:
        return None

    if parts[0] != "projects":
        return None

    return parts[1]


def calculate_project_total_size(bucket: str, project_id: str) -> int:
    prefix = f"projects/{project_id}/"
    total_size = 0
    continuation_token = None

    while True:
        kwargs: dict[str, Any] = {
            "Bucket": bucket,
            "Prefix": prefix,
            "MaxKeys": 1000,
        }
        if continuation_token:
            kwargs["ContinuationToken"] = continuation_token

        response = s3.list_objects_v2(**kwargs)

        for obj in response.get("Contents", []):
            total_size += obj.get("Size", 0)

        if response.get("IsTruncated"):
            continuation_token = response.get("NextContinuationToken")
        else:
            break

    return total_size


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    logger.info("Received event: %s", json.dumps(event))

    records = event.get("Records", [])
    if not records:
        logger.warning("No records in event")
        return {"statusCode": 200, "body": "No records"}

    results = []

    for record in records:
        try:
            bucket = record["s3"]["bucket"]["name"]
            encoded_key = record["s3"]["object"]["key"]
            key = urllib.parse.unquote_plus(encoded_key)
            event_name = record.get("eventName", "")

            project_id = extract_project_id_from_key(key)
            if not project_id:
                logger.warning("Could not extract project_id from key: %s", key)
                results.append(
                    {"bucket": bucket, "key": key, "status": "skipped_invalid_key"}
                )
                continue

            total_size = calculate_project_total_size(bucket, project_id)

            logger.info(
                "Event=%s | Bucket=%s | Project=%s | Key=%s | TotalSizeBytes=%s",
                event_name,
                bucket,
                project_id,
                key,
                total_size,
            )

            limit_bytes = os.getenv("PROJECT_SIZE_LIMIT_BYTES")
            if limit_bytes:
                try:
                    limit_value = int(limit_bytes)
                    if total_size > limit_value:
                        logger.warning(
                            "Project %s exceeded size limit: %s > %s",
                            project_id,
                            total_size,
                            limit_value,
                        )
                except ValueError:
                    logger.warning(
                        "Invalid PROJECT_SIZE_LIMIT_BYTES env var: %s", limit_bytes
                    )

            results.append(
                {
                    "bucket": bucket,
                    "key": key,
                    "project_id": project_id,
                    "event_name": event_name,
                    "total_size_bytes": total_size,
                    "status": "ok",
                }
            )

        except ClientError as exc:
            logger.exception("AWS client error while processing record")
            results.append({"status": "error", "error": str(exc)})
        except Exception as exc:
            logger.exception("Unexpected error while processing record")
            results.append({"status": "error", "error": str(exc)})

    return {
        "statusCode": 200,
        "body": json.dumps(results),
    }