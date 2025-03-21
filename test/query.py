from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory

# 대화형 메모리 설정
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


# FAISS 벡터DB 불러오기
vectorstore = FAISS.load_local(
    "faiss_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True
)

# 법률 질문 입력
query = "길을 걸어가다가 눈을 마주쳤다는 이유로 폭행을 행사한 A씨에게 어떤 처벌을 할 수 있을까요?"

# 가장 관련 있는 법률 조항 검색
search_results = vectorstore.similarity_search(query, k=3)

# 결과 출력
for idx, result in enumerate(search_results):
    print(f"{idx+1}. 관련 법률 조항:\n{result.page_content}\n")