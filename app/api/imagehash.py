# app/api/imagehash.py
"""
이미지 해시 기반 유사도 계산 API 라우터

Spring Boot의 FastApiImageHashClient와 연동되는 엔드포인트 제공
POST /imagehash/similarity - 이미지 유사도 계산 및 상위 5개 상품 반환
"""
import logging
from fastapi import APIRouter, HTTPException, status

from app.models.imagehash_dto import ImageHashRequest, SimilarityResponse, RankedProduct
from app.services.imagehash_service import calculate_top_k_similar_images

# 라우터 설정
router = APIRouter(
    prefix="/imagehash",
    tags=["ImageHash"],
    responses={
        400: {"description": "잘못된 요청"},
        500: {"description": "서버 내부 오류"}
    }
)

logger = logging.getLogger(__name__)


@router.post(
    "/similarity",
    response_model=SimilarityResponse,
    summary="이미지 유사도 계산",
    description="""
    기준 이미지와 상품 이미지들의 유사도를 계산하여 상위 5개 반환
    
    **알고리즘:**
    - pHash (Perceptual Hash): 이미지 구조/형태 분석 (70% 가중치)
    - colorHash: 이미지 색상 분포 분석 (30% 가중치)
    
    **반환:**
    - 유사도가 높은 순으로 정렬된 상위 5개 상품
    - 유사도는 0.0 ~ 1.0 범위 (1.0에 가까울수록 유사)
    """,
    status_code=status.HTTP_200_OK
)
async def get_top_k_similar_images(request: ImageHashRequest) -> SimilarityResponse:
    """
    이미지 유사도 계산 API
    
    Spring Boot의 FastApiImageHashClient.getTopKSimilarImages()와 매핑
    
    Args:
        request: 기준 이미지 URL과 비교할 상품 목록
        
    Returns:
        SimilarityResponse: 유사도 순으로 정렬된 상위 5개 상품
        
    Raises:
        HTTPException 400: 요청 데이터 검증 실패
        HTTPException 500: 이미지 다운로드 또는 처리 실패
    """
    try:
        # 요청 데이터 검증
        if not request.baseImageUrl:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="baseImageUrl은 필수입니다"
            )
        
        if not request.products or len(request.products) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="products는 최소 1개 이상이어야 합니다"
            )
        
        logger.info(
            f"유사도 계산 요청 - 기준 이미지: {request.baseImageUrl}, "
            f"상품 수: {len(request.products)}"
        )
        
        # 유사도 계산 서비스 호출
        ranked_products = await calculate_top_k_similar_images(
            base_image_url=request.baseImageUrl,
            products=request.products
        )
        
        # 응답 생성
        response = SimilarityResponse(rankedProducts=ranked_products)
        
        logger.info(f"유사도 계산 완료 - 반환 상품 수: {len(ranked_products)}")
        
        return response
        
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
        
    except Exception as e:
        # 기타 예외는 500 에러로 변환
        logger.error(f"유사도 계산 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 유사도 계산 중 오류가 발생했습니다: {str(e)}"
        )
