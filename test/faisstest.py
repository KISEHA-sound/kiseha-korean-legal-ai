from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

# ✅ 로드할 벡터DB 설정
law_name = "Criminal_Law"
FAISS_INDEX_DIR = os.path.abspath("../faiss_indexes")
index_path = os.path.join(FAISS_INDEX_DIR, law_name)

# ✅ SBERT 임베딩 모델
embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"})

# ✅ FAISS 벡터DB 로드
print(f"\n📂 {law_name} 벡터DB를 로드하는 중... (경로: {index_path})")
vector_store = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)

# ✅ 검색 테스트
query = "폭행죄 처벌"  # 쿼리 수정
top_k = 5
search_results = vector_store.similarity_search_with_score(query, k=top_k)

# ✅ 점수 정규화 (Cosine Similarity 변환)
scores = [score for _, score in search_results]
min_score, max_score = min(scores), max(scores)

def normalize_score(score):
    return 1 - (score - min_score) / (max_score - min_score) if max_score > min_score else 1.0

# ✅ "폭행"이 포함된 조항 우선 필터링
filtered_results = sorted(search_results, key=lambda x: ("폭행" in x[0].metadata.get("article", ""), normalize_score(x[1])), reverse=True)

print(f"\n🔎 '{query}' 검색 결과 (Top {top_k}):")
for i, (result, score) in enumerate(filtered_results):
    normalized_score = normalize_score(score)  # 점수 정규화
    article = result.metadata.get("article", "알 수 없음")
    print(f"\n--- 🔹 검색 결과 {i+1} ---")
    print(f"📌 출처: {result.metadata['source']} | 조항: {article}")
    print(f"📖 내용:\n{result.page_content}")
    print(f"🎯 유사도 점수 (0~1): {normalized_score:.4f}")