from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

# 벡터DB 경로 설정
law_name = "Police_Duties_Act"
VECTOR_DB_DIR = os.path.abspath("../faiss_indexes")  # 너가 실행하는 위치에 따라 ../ 조정
vector_path = os.path.join(VECTOR_DB_DIR, law_name)

# 임베딩 모델 (저장할 때 사용한 것과 동일하게)
embedding_model = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"}
)

# FAISS 벡터DB 로드
vector_store = FAISS.load_local(vector_path, embedding_model, allow_dangerous_deserialization=True)

# 전체 문서 리스트 가져오기
docs = vector_store.docstore._dict.values()

# 조항 출력
for i, doc in enumerate(docs):
    article = doc.metadata.get("article", "알 수 없음")
    print(f"\n--- 조항 {i+1} ---")
    print(f"📌 조항 번호: {article}")
    print(f"📖 내용:\n{doc.page_content}")