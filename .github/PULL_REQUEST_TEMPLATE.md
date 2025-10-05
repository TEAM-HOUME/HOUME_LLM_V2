# PR 제목

> 간결하고 구체적으로: ex) feat(imagehash): for-plan API 추가 및 DTO 정리

---

## 개요
- 이 PR의 목적과 배경을 간단히 설명해 주세요.
- 관련 이슈가 있다면 번호를 함께 적어 주세요.

## 변경 사항
- 주요 변경점을 bullet로 정리합니다.
- 코드/구조/스키마 변경 등 Breaking Change 여부를 명시합니다.

## 이슈 연결
- Close: #123
- Related: #456

## 세부 내용
- [ ] API 스펙 변경 여부 (요청/응답 필드, 상태코드 등)
- [ ] DB/스토리지 마이그레이션 필요 여부
- [ ] 설정값(.env)/시크릿 변경 필요 여부
- [ ] 퍼포먼스 영향도 (시간/메모리/네트워크)
- [ ] 보안 영향도 (권한/입력검증/민감정보)

## 테스트
- [ ] 단위 테스트 추가/수정
- [ ] 통합 테스트 추가/수정
- [ ] 로컬 수동 테스트 방법
  - 요청 예시:
    ```json
    {
      "baseImageUrl": "https://picsum.photos/400/300",
      "products": [
        {"imageUrl": "https://picsum.photos/400/300?random=1", "productId": 1001},
        {"imageUrl": "https://picsum.photos/400/300?random=2", "productId": 1002}
      ],
      "pHash": 70,
      "colorHash": 30
    }
    ```
  - 예상 응답 요약:
    - 상위 5개 `rankedProducts` 반환, 각 항목은 `productId`, `imageUrl`, `similarity`

## 스크린샷/로그(옵션)
- UI/문서/Swagger 캡처나 에러 로그가 있다면 첨부해 주세요.

## 배포/롤백
- 배포 전 체크리스트:
  - [ ] 마이그레이션 수행
  - [ ] 환경변수/시크릿 반영
- 롤백 전략:
  - [ ] 태그/커밋 해시 지정하여 원복 방법 명시

## 체크리스트
- [ ] 코드 스타일 및 Lint 통과
- [ ] 불필요한 디버그/로그 제거
- [ ] 주석/문서화 반영 (README/Swagger 등)
- [ ] 리뷰어가 이해할 수 있는 충분한 설명 제공

## 기타
- 리뷰에 유의할 포인트, 추후 후속 작업 계획 등이 있다면 적어 주세요.
