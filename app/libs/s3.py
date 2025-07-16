import boto3
import uuid
import logging
from botocore.exceptions import BotoCoreError, ClientError

from app.config.settings import settings

logger = logging.getLogger(__name__)

# S3 클라이언트 생성
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

# 이미지 바이트 데이터, content_type을 받아, S3에 저장된 이미지의 URL 반환
def upload_image_to_s3(png_bytes: bytes, content_type="image/png") -> str:
    """
    PNG 바이트를 S3에 업로드하고 URL을 반환
    """
    # S3 내부 경로
    filename = f"fastapi/{uuid.uuid4()}.png"
    try:
        s3.put_object(  # S3에 이미지 파일을 저장
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=filename,  # S3에서의 파일 경로
            Body=png_bytes,
            ContentType=content_type,
        )
        s3_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
        logger.info("✅ S3 업로드 성공: %s", s3_url)
        return s3_url

    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 업로드 실패: {e}")
