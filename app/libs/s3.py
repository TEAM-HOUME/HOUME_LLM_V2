import boto3
import uuid
import logging
from botocore.exceptions import BotoCoreError, ClientError

from app.config.settings import settings

logger = logging.getLogger(__name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

def upload_image_to_s3(png_bytes: bytes, content_type="image/png") -> str:
    """
    PNG 바이트를 S3에 업로드하고 URL을 반환
    """
    filename = f"fastapi/{uuid.uuid4()}.png"
    try:
        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=filename,
            Body=png_bytes,
            ContentType=content_type,
        )
        s3_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
        logger.info("✅ S3 업로드 성공: %s", s3_url)
        return s3_url

    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 업로드 실패: {e}")
