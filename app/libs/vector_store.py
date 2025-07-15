# app/libs/vector_store.py
from pathlib import Path

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

from app.config.settings import settings

# ── (A) 모듈 기준 “app/” 폴더
BASE_DIR = Path(__file__).resolve().parent.parent  # …/app/libs → …/app

# ── (B) 문서·인덱스 경로
TXT_SOURCE = (BASE_DIR / settings.VECTOR_DOC_PATH).resolve()
VECTORSTORE_PATH = (BASE_DIR / "vector_store" / "faiss_index").resolve()

# ── (C) 문서 파일 체크
if not TXT_SOURCE.exists():
    raise FileNotFoundError(f"[VectorStore] document not found: {TXT_SOURCE}")

def get_vectorstore() -> FAISS:
    """
    • 저장된 FAISS 인덱스를 로드하거나,
    • 없으면 raw_text → split → FAISS.build → 저장
    """
    # 1) 임베딩 객체
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    # 2) 이미 훈련된 인덱스가 있으면 바로 로드
    if VECTORSTORE_PATH.exists():
        return FAISS.load_local(
            str(VECTORSTORE_PATH),
            embeddings,
            allow_dangerous_deserialization=True
        )

    # 3) 없으면 문서 읽어서 청크 분할
    raw_text = TXT_SOURCE.read_text(encoding="utf-8")
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_text(raw_text)
    docs = [Document(page_content=t) for t in texts]

    # 4) FAISS 생성 & 디렉터리 보장 후 저장
    vs = FAISS.from_documents(docs, embeddings)
    VECTORSTORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    vs.save_local(str(VECTORSTORE_PATH))
    return vs
