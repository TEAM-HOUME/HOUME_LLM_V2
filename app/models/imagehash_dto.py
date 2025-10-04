# app/models/imagehash_dto.py
"""
이미지 해시 유사도 API의 요청/응답 DTO 정의
Spring Boot의 Record 타입과 동일한 구조로 설계
"""
from pydantic import BaseModel, Field
from typing import List


class Product(BaseModel):
    """
    비교 대상 상품 정보
    Spring의 ImageHashRequest.Product와 매핑
    """
    imageUrl: str = Field(..., description="상품 이미지 URL")
    productId: int = Field(..., description="상품 식별자 (Long)")


class ImageHashRequest(BaseModel):
    """
    이미지 해시 유사도 계산 요청 DTO
    Spring의 ImageHashRequest와 매핑
    """
    baseImageUrl: str = Field(..., description="기준이 되는 이미지 URL (유사도 비교 대상)")
    products: List[Product] = Field(..., description="유사도를 계산할 상품 목록")

    class Config:
        # Swagger UI에 표시될 예시 데이터
        json_schema_extra = {
            "example": {
                "baseImageUrl": "https://picsum.photos/400/300",
                "products": [
                    {
                        "imageUrl": "https://picsum.photos/400/300?random=1",
                        "productId": 1001
                    },
                    {
                        "imageUrl": "https://picsum.photos/400/300?random=2",
                        "productId": 1002
                    }
                ]
            }
        }


class RankedProduct(BaseModel):
    """
    유사도가 계산된 상품 정보
    Spring의 SimilarityResponse.RankedProduct와 매핑
    """
    productId: int = Field(..., description="상품 식별자 (Long)")
    imageUrl: str = Field(..., description="상품 이미지 URL")
    similarity: float = Field(..., ge=0.0, le=1.0, description="유사도 점수 (0.0 ~ 1.0, 높을수록 유사)")


class SimilarityResponse(BaseModel):
    """
    유사도 계산 결과 응답 DTO
    Spring의 SimilarityResponse와 매핑
    유사도가 높은 순으로 정렬된 상위 5개 상품 반환
    """
    rankedProducts: List[RankedProduct] = Field(..., description="유사도 순으로 정렬된 상품 목록 (최대 5개)")

    class Config:
        # Swagger UI에 표시될 예시 데이터
        json_schema_extra = {
            "example": {
                "rankedProducts": [
                    {
                        "productId": 1001,
                        "imageUrl": "https://picsum.photos/400/300?random=1",
                        "similarity": 0.9234
                    },
                    {
                        "productId": 1002,
                        "imageUrl": "https://picsum.photos/400/300?random=2",
                        "similarity": 0.8756
                    }
                ]
            }
        }
