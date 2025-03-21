from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# 768차원 SBERT 임베딩 모델 로드
embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"})

# FAISS 벡터DB 로드 (보안 옵션 추가)
vectorstore = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

print("✅ FAISS 벡터DB가 정상적으로 로드되었습니다!")
