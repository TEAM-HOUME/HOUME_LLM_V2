# app/services/imagehash_service.py
"""
이미지 해시 기반 유사도 계산 서비스

pHash(Perceptual Hash)와 colorHash를 7:3 비율로 조합하여
이미지 간 유사도를 계산하는 서비스
"""
import io
import logging
from typing import List, Tuple
from PIL import Image
import imagehash
import httpx

from app.models.imagehash_dto import Product, RankedProduct

logger = logging.getLogger(__name__)

# 유사도 계산 가중치 설정
PHASH_WEIGHT = 0.7  # pHash 가중치 70%
COLOR_HASH_WEIGHT = 0.3  # colorHash 가중치 30%

# 상위 K개 상품 반환 설정
TOP_K = 5


async def download_image(url: str) -> Image.Image:
    """
    URL에서 이미지를 다운로드하여 PIL Image 객체로 반환
    
    Args:
        url: 다운로드할 이미지 URL
        
    Returns:
        PIL Image 객체
        
    Raises:
        httpx.HTTPError: HTTP 요청 실패 시
        PIL.UnidentifiedImageError: 이미지 포맷 인식 실패 시
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 이미지 다운로드
        response = await client.get(url)
        response.raise_for_status()
        
        # 바이트 데이터를 PIL Image로 변환
        image_bytes = io.BytesIO(response.content)
        image = Image.open(image_bytes)
        
        # RGBA 이미지를 RGB로 변환 (투명도 제거)
        if image.mode == 'RGBA':
            # 흰색 배경으로 변환
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # 알파 채널을 마스크로 사용
            image = background
        elif image.mode != 'RGB':
            # 기타 모드는 RGB로 변환
            image = image.convert('RGB')
            
        return image


def calculate_combined_hash(image: Image.Image, hash_size: int = 8) -> Tuple[imagehash.ImageHash, imagehash.ImageHash]:
    """
    이미지의 pHash와 colorHash를 계산
    
    pHash (Perceptual Hash):
    - 이미지의 구조적 특징을 캡처
    - 크기 변경, 약간의 색상 변화에 강건
    - 가구의 형태와 패턴을 인식하는데 효과적
    
    colorHash:
    - 이미지의 색상 분포를 캡처
    - 색상 팔레트가 유사한 이미지를 찾는데 효과적
    - 가구의 색상과 톤을 비교하는데 유용
    
    Args:
        image: PIL Image 객체
        hash_size: 해시 크기 (기본값: 8, 8x8=64비트)
        
    Returns:
        (pHash, colorHash) 튜플
    """
    # pHash: DCT(Discrete Cosine Transform) 기반 해시
    # 이미지를 주파수 도메인으로 변환하여 구조적 특징 추출
    phash = imagehash.phash(image, hash_size=hash_size)
    
    # colorHash: HSV 색공간에서 색상 분포 기반 해시
    # binbits=3은 각 색상 채널을 8개 구간으로 나눔 (2^3=8)
    color_hash = imagehash.colorhash(image, binbits=3)
    
    return phash, color_hash


def calculate_hash_similarity(hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> float:
    """
    두 이미지 해시 간의 유사도를 0~1 사이의 실수로 계산
    
    Hamming Distance를 사용하여 해시 간 차이를 측정한 후,
    이를 유사도 점수로 변환
    
    Args:
        hash1: 첫 번째 이미지 해시
        hash2: 두 번째 이미지 해시
        
    Returns:
        유사도 점수 (0.0 ~ 1.0)
        - 1.0: 완전히 동일
        - 0.0: 완전히 다름
    """
    # Hamming Distance: 두 해시에서 다른 비트의 개수
    hamming_distance = hash1 - hash2
    
    # 최대 거리 계산 (해시의 총 비트 수)
    # hash_size=8이면 8*8=64비트
    max_distance = len(hash1.hash) ** 2
    
    # 유사도 = 1 - (거리 / 최대거리)
    # 거리가 0이면 유사도 1.0 (동일)
    # 거리가 최대이면 유사도 0.0 (완전히 다름)
    similarity = 1.0 - (hamming_distance / max_distance)
    
    return max(0.0, min(1.0, similarity))  # 0~1 범위로 클리핑


def calculate_weighted_similarity(
    base_phash: imagehash.ImageHash,
    base_color_hash: imagehash.ImageHash,
    product_phash: imagehash.ImageHash,
    product_color_hash: imagehash.ImageHash
) -> float:
    """
    pHash와 colorHash의 가중 평균으로 최종 유사도 계산
    
    pHash 70% + colorHash 30% 비율로 조합하여
    형태와 색상을 모두 고려한 유사도 산출
    
    Args:
        base_phash: 기준 이미지의 pHash
        base_color_hash: 기준 이미지의 colorHash
        product_phash: 상품 이미지의 pHash
        product_color_hash: 상품 이미지의 colorHash
        
    Returns:
        가중 평균 유사도 (0.0 ~ 1.0)
    """
    # pHash 기반 유사도 계산 (형태 유사도)
    phash_similarity = calculate_hash_similarity(base_phash, product_phash)
    
    # colorHash 기반 유사도 계산 (색상 유사도)
    color_similarity = calculate_hash_similarity(base_color_hash, product_color_hash)
    
    # 가중 평균 계산: 70% pHash + 30% colorHash
    weighted_similarity = (
        PHASH_WEIGHT * phash_similarity +
        COLOR_HASH_WEIGHT * color_similarity
    )
    
    logger.debug(
        f"유사도 상세: pHash={phash_similarity:.4f} (70%), "
        f"colorHash={color_similarity:.4f} (30%), "
        f"최종={weighted_similarity:.4f}"
    )
    
    return weighted_similarity


async def calculate_top_k_similar_images(
    base_image_url: str,
    products: List[Product]
) -> List[RankedProduct]:
    """
    기준 이미지와 상품 이미지들의 유사도를 계산하여 상위 5개 반환
    
    처리 과정:
    1. 기준 이미지 다운로드 및 해시 계산 (pHash, colorHash)
    2. 각 상품 이미지 다운로드 및 해시 계산
    3. 기준 이미지와 각 상품 이미지 간 유사도 계산 (7:3 가중치)
    4. 유사도 기준 내림차순 정렬
    5. 상위 5개 상품 반환
    
    Args:
        base_image_url: 기준 이미지 URL
        products: 비교할 상품 목록
        
    Returns:
        유사도 순으로 정렬된 상위 5개 상품 목록
        
    Raises:
        Exception: 기준 이미지 다운로드 또는 해시 계산 실패 시
    """
    try:
        # ========================================
        # 1단계: 기준 이미지 처리
        # ========================================
        logger.info(f"[1/4] 기준 이미지 다운로드 중: {base_image_url}")
        base_image = await download_image(base_image_url)
        
        logger.info("[2/4] 기준 이미지 해시 계산 중 (pHash + colorHash)")
        base_phash, base_color_hash = calculate_combined_hash(base_image)
        logger.info(f"  → pHash: {base_phash}")
        logger.info(f"  → colorHash: {base_color_hash}")
        
        # ========================================
        # 2단계: 각 상품 이미지와 유사도 계산
        # ========================================
        logger.info(f"[3/4] 상품 이미지 유사도 계산 중 (총 {len(products)}개)")
        ranked_products: List[RankedProduct] = []
        
        for idx, product in enumerate(products, start=1):
            try:
                logger.info(f"  [{idx}/{len(products)}] 처리 중: productId={product.productId}")
                
                # 상품 이미지 다운로드
                product_image = await download_image(product.imageUrl)
                
                # 상품 이미지 해시 계산
                product_phash, product_color_hash = calculate_combined_hash(product_image)
                
                # 가중 유사도 계산 (pHash 70% + colorHash 30%)
                similarity = calculate_weighted_similarity(
                    base_phash=base_phash,
                    base_color_hash=base_color_hash,
                    product_phash=product_phash,
                    product_color_hash=product_color_hash
                )
                
                # 결과 저장 (소수점 4자리까지)
                ranked_products.append(
                    RankedProduct(
                        productId=int(product.productId),
                        imageUrl=product.imageUrl,
                        similarity=round(similarity, 4)
                    )
                )
                
                logger.info(f"    ✓ 유사도: {similarity:.4f}")
                
            except Exception as e:
                # 개별 상품 처리 실패 시 유사도 0.0으로 처리하고 계속 진행
                logger.error(f"    ✗ 상품 처리 실패 (productId={getattr(product, 'productId', 'N/A')}): {str(e)}")
                ranked_products.append(
                    RankedProduct(
                        productId=int(getattr(product, 'productId', 0)) if getattr(product, 'productId', None) is not None else 0,
                        imageUrl=product.imageUrl,
                        similarity=0.0
                    )
                )
        
        # ========================================
        # 3단계: 유사도 기준 정렬 및 상위 K개 선택
        # ========================================
        logger.info("[4/4] 유사도 기준 정렬 및 상위 5개 선택")
        
        # 유사도 내림차순 정렬 (높은 순서대로)
        ranked_products.sort(key=lambda x: x.similarity, reverse=True)
        
        # 상위 5개만 선택
        top_products = ranked_products[:TOP_K]
        
        logger.info(f"✓ 완료: 상위 {len(top_products)}개 상품 반환")
        for idx, product in enumerate(top_products, start=1):
            logger.info(f"  {idx}위. productId={product.productId} (유사도: {product.similarity:.4f})")
        
        return top_products
        
    except Exception as e:
        logger.error(f"✗ 이미지 유사도 계산 실패: {str(e)}", exc_info=True)
        raise
