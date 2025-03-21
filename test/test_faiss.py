from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# 768차원 SBERT 임베딩 모델 (벡터 검색 시 필요)
embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"})

# 저장된 FAISS 벡터DB 불러오기 (보안 옵션 추가)
vectorstore = FAISS.load_local("../faiss_index", embeddings=embedding_model, allow_dangerous_deserialization=True)

# 검색할 쿼리 입력 (예: "경찰관이 불심검문할 수 있는 경우는?")
query = "경찰관이 불심검문할 수 있는 경우는?"

# 쿼리를 벡터화한 후 FAISS에서 유사한 문서 검색
search_results = vectorstore.similarity_search(query, k=3)  # 상위 3개 검색

# 검색 결과 출력
print("🔎 검색 쿼리:", query)
print("========================================")
for idx, result in enumerate(search_results, start=1):
    print(f"📌 [결과 {idx}]\n{result.page_content}\n")
    print("-" * 50)
