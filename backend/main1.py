from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_huggingface import HuggingFaceEmbeddings
from fastapi.middleware.cors import CORSMiddleware
import time
import tiktoken
from transformers import pipeline
from backend.graphql import get_graphql_app  # GraphQL 엔드포인트 추가


# FastAPI 앱 생성
app = FastAPI()

# CORS 설정 (React에서 요청 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL 엔드포인트 추가
app.include_router(get_graphql_app(), prefix="/graphql")

# Hugging Face 요약 모델 사용
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# **법률 특화 임베딩 모델**
law_embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli")

# **FAISS 벡터DB 로드**
INDEX_PATH = "/home/kiseha/dev/kiseha-p1/faiss_index"
vectorstore = FAISS.load_local(INDEX_PATH, law_embedding_model, allow_dangerous_deserialization=True)

# **GPT-4 → GPT-3.5-turbo-16k로 변경 가능**
llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.3)

# **대화 메모리 적용**
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="question",
    output_key="answer"
)

# **법률 카테고리 자동 분류**
law_categories = {
    "폭행": "형법", "상해": "형법", "사기": "형법", "절도": "형법", "재물손괴": "형법",
    "협박": "형법", "강도": "형법", "횡령": "형법", "배임": "형법", "강간": "형법",
    "이혼": "민법", "위자료": "민법", "재산분할": "민법", "양육권": "민법", "친권": "민법",
    "노동": "근로기준법", "해고": "근로기준법", "부당해고": "근로기준법", "징계해고": "근로기준법",
}

# **법률 카테고리 추출 함수**
def get_law_category(query):
    for keyword, category in law_categories.items():
        if keyword in query:
            return category
    return "일반 법률"

# **FAISS 검색 함수 (점수 필터링 포함)**
def search_law(query, vectorstore, top_k=5, score_threshold=0.5):
    search_results_with_scores = vectorstore.similarity_search_with_score(query, k=top_k)
    filtered_results = [result for result, score in search_results_with_scores if score > score_threshold]

    if not filtered_results:  
        filtered_results = vectorstore.similarity_search(query, k=top_k)

    return filtered_results

# **토큰 수 계산 함수**
def count_tokens(text):
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")
    return len(encoder.encode(text))

# **법률 조항 요약 함수 (요약 모델 적용)**
def summarize_law_results(results, max_length=2000):
    text = "\n\n".join([result.page_content for result in results])
    if len(text) > max_length:
        summary = summarizer(text, max_length=200, min_length=100, do_sample=False)
        return summary[0]["summary_text"]
    return text

# **요청 데이터 모델**
class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_law_ai(request: QueryRequest):
    start_time = time.time()
    query = request.question

    # **1단계: 법률 카테고리 분석**
    law_category = get_law_category(query)

    # **2단계: FAISS 검색 (점수 기반 필터링 포함)**
    search_results = search_law(query, vectorstore, top_k=5, score_threshold=0.5)

    # **3단계: 법 조항 요약 적용**
    relevant_laws = summarize_law_results(search_results, max_length=2000)

    # **이전 대화 기록 로드**
    chat_history_dict = memory.load_memory_variables({})
    chat_history = chat_history_dict.get("chat_history", [])

    # **최적화된 LLM 프롬프트**
    prompt = f"""
    당신은 대한민국 법률 전문가이자 변호사입니다.  
    사용자의 질문에 대해 **법률적 근거를 바탕으로 신뢰성 있는 답변**을 제공하세요. 

    ---  

    **관련 법률 조항 (FAISS 검색 결과)**  
    {relevant_laws}

    ---  

    **사용자 질문:**  
    {query}  

    ---  

    ✔ **반드시 신뢰할 수 있는 법률 조항을 바탕으로 답변하세요.**  
    ✔ **검색된 법률 조항이 적절하지 않다면, "적절한 법 조항을 찾을 수 없습니다"라고 답변하세요.**  
    ✔ **법적 리스크 분석:** 이 사안에서 사용자가 주의해야 할 점은?  
    ✔ **피고인/피해자 입장에서 각각 어떤 대응 전략이 가능한가?**  
    ✔ **추가 정보가 필요하면, 명확한 질문을 사용자에게 제시하세요.**  
    ✔ **부정확한 정보를 제공하지 마세요. (출처 없는 내용을 생성하지 않도록 설정)**  
    """

    # **토큰 수 계산**
    query_tokens = count_tokens(query)
    prompt_tokens = count_tokens(prompt)

    # **GPT 호출 (스트리밍)**
    response_text = ""
    for chunk in llm.stream(prompt):
        response_text += chunk.content  

    response_tokens = count_tokens(response_text)

    # **대화 기록 업데이트**
    memory.save_context({"question": query}, {"answer": response_text})

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)# 실행 시간 계산

    return {
        "answer": response_text,
        "law_category": law_category,
        "elapsed_time": f"{elapsed_time}초",
        "tokens": {
            "query_tokens": query_tokens,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "total_tokens": query_tokens + prompt_tokens + response_tokens
        }
    }
