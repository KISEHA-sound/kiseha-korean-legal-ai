from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
import time
import tiktoken
import requests
from langchain.memory import ConversationBufferMemory
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

# GPT 모델 설정
llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.3)

# 대화 메모리 적용 (연속된 대화 기억)
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="question",
    output_key="answer"
)

# ✅ **법률 카테고리 자동 분류**
law_categories = {
    "폭행": "형법", "상해": "형법", "사기": "형법", "절도": "형법", "재물손괴": "형법",
    "협박": "형법", "강도": "형법", "횡령": "형법", "배임": "형법", "강간": "형법",
    "이혼": "민법", "위자료": "민법", "재산분할": "민법", "양육권": "민법", "친권": "민법",
    "노동": "근로기준법", "해고": "근로기준법", "부당해고": "근로기준법", "징계해고": "근로기준법",
}

def get_law_category(query):
    """사용자 질문에서 키워드를 찾아서 법률 카테고리를 반환"""
    for keyword, category in law_categories.items():
        if keyword in query:
            return category
    return "일반 법률"

# ✅ **GraphQL을 통한 법 조항 검색 (카테고리 기반)**
GRAPHQL_URL = "http://127.0.0.1:8000/graphql"

def search_laws_with_graphql(query, law_category):
    graphql_query = """
    query ($query: String!, $category: String!) {
        searchLaws(query: $query, category: $category)
    }
    """
    response = requests.post(GRAPHQL_URL, json={"query": graphql_query, "variables": {"query": query, "category": law_category}})
    
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("searchLaws", [])
    return []

# ✅ **토큰 수 계산 함수**
def count_tokens(text):
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")
    return len(encoder.encode(text))

# ✅ **요청 데이터 모델**
class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_law_ai(request: QueryRequest):
    start_time = time.time()
    query = request.question

    # ✅ **1단계: 법률 카테고리 분석**
    law_category = get_law_category(query)

    # ✅ **2단계: GraphQL 검색 (카테고리 기반)**
    search_results = search_laws_with_graphql(query, law_category)
    relevant_laws = "\n\n".join(search_results) if search_results else "적절한 법 조항을 찾을 수 없습니다."

    # ✅ **3단계: 이전 대화 기록 불러오기**
    chat_history_dict = memory.load_memory_variables({})
    chat_history = chat_history_dict.get("chat_history", [])

    # ✅ **4단계: 최적화된 LLM 프롬프트 생성**
    prompt = f"""
    당신은 대한민국 법률 전문가이자 변호사입니다.  
    사용자의 질문에 대해 **법률적 근거를 바탕으로 신뢰성 있는 답변**을 제공하세요. 

    ---  
    **법률 카테고리:** {law_category}  
    **이전 대화 기록:**  
    {chat_history}  

    ---  
    **관련 법률 조항 (GraphQL 검색 결과)**  
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

    # ✅ **5단계: 토큰 수 계산**
    query_tokens = count_tokens(query)
    prompt_tokens = count_tokens(prompt)

    # ✅ **6단계: GPT 호출 (스트리밍)**
    response_text = ""
    for chunk in llm.stream(prompt):
        response_text += chunk.content  

    response_tokens = count_tokens(response_text)
    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)

    # ✅ **7단계: 대화 기록 업데이트**
    memory.save_context({"question": query}, {"answer": response_text})

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