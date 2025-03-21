from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI
import time, os
import tiktoken

# ===== FastAPI 기본 설정 =====
app = FastAPI()

# ===== CORS 설정 (프론트 연결 허용) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중엔 전체 허용, 배포 시 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 데이터 클래스 정의 =====
class QueryRequest(BaseModel):
    question: str
    law: str  # 예: "Criminal_Law"

# ===== 벡터DB 및 임베딩 모델 준비 =====
embedding_model = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"}
)

VECTOR_DB_DIR = os.path.abspath("faiss_indexes")
LOADED_VECTOR_STORES = {}

# ===== 토큰 계산 함수 (GPT-4-turbo 기준) =====
def count_tokens(text, model="gpt-4-turbo"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

# ===== Chat 기록 유지 =====
chat_history = []

# ===== 쿼리 요청 처리 =====
@app.post("/query")
async def query_law(request: QueryRequest):
    start_time = time.time()

    # 1. 벡터DB 로딩 (캐시 활용)
    law = request.law
    if law not in LOADED_VECTOR_STORES:
        vector_path = os.path.join(VECTOR_DB_DIR, law)
        vector_store = FAISS.load_local(vector_path, embedding_model, allow_dangerous_deserialization=True)
        LOADED_VECTOR_STORES[law] = vector_store
    else:
        vector_store = LOADED_VECTOR_STORES[law]

    # 2. 유사도 검색
    top_k = 2
    search_results = vector_store.similarity_search_with_score(request.question, k=top_k)

    # 3. 점수 정규화
    scores = [score for _, score in search_results]
    min_score, max_score = min(scores), max(scores)
    def normalize(score):
        return 1 - (score - min_score) / (max_score - min_score) if max_score > min_score else 1.0

    # 4. 검색 결과 요약
    context = "\n".join([
        f"[{doc.metadata.get('article', '알 수 없음')}] {doc.page_content.strip()}"
        for doc, _ in search_results
    ])

    # 5. GPT 프롬프트 구성
    system_prompt = """
    당신은 대한민국의 법률 전문 변호사입니다.
    사용자는 특정 상황에 대한 법률적 질문을 하고 있으며, 아래의 관련 법률 조항을 기반으로 답변해야 합니다.

    아래의 사항을 반드시 포함하여 작성해 주세요:
    1. 핵심 법률 조항에 대한 요약 (조항 번호 포함)
    2. 해당 상황에서 발생할 수 있는 법적 리스크 분석
    3. 피해자 입장에서 취할 수 있는 대응 전략
    4. 피고인 입장에서 고려해야 할 법적 방어 전략

    모호하거나 과도한 일반론을 피하고, 조항을 정확히 요약하여 현실적인 조언을 제공하세요.
    """
    user_prompt = f"질문: {request.question}\n\n관련 법률 조항:\n{context}"

    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    # 6. OpenAI GPT 호출
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    response_text = completion.choices[0].message.content.strip()

    # 7. 토큰 계산
    prompt_tokens = count_tokens(full_prompt)
    response_tokens = count_tokens(response_text)
    total_tokens = prompt_tokens + response_tokens
    query_tokens = count_tokens(request.question)

    # 8. 대화 기록 추가
    chat_history.append({"question": request.question, "answer": response_text})

    # 9. 응답 반환
    return {
        "answer": response_text,
        "elapsed_time": f"{(time.time() - start_time):.2f}초",
        "tokens": {
            "query_tokens": query_tokens,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
        },
        "chat_history": chat_history[-10:]  # 최근 10개만 유지
    }