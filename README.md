## 🧠 Prompt Flow: How RAG generates a better image prompt

| Step | Description |
|------|-------------|
| **1. Load my_docs.txt** | 사용자 지식 문서 로드 |
| **2. CharacterTextSplitter** | LangChain을 이용해 문서를 청크(chunk)로 나눔 |
| **3. OpenAIEmbeddings** | 각 청크를 벡터화하여 의미를 수치화 |
| **4. FAISS 벡터 DB 생성** | 메모리/디스크에 벡터 저장하여 검색 가능하게 구성 |
| **5. .as_retriever()** | 사용자 프롬프트와 관련된 유사 문서 검색 |
| **6. ChatOpenAI + RetrievalQA** | 검색된 문서 기반으로 GPT가 프롬프트 정교화 |
| **7. gpt-image-1 API** | 보강된 프롬프트로 OpenAI 이미지 생성 API 호출 |


<br><br>


## 🚀 남은 개발 과제 (Roadmap)

- [ ] 벡터 DB → S3 업로드 및 로드 처리 구현
- [ ] 벡터 DB 구성용 문서 수집 전략 수립
    - 인테리어 디자인 가이드라인
    - 구조별 평면 설명
    - 사용자 피드백 및 사례
