import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# 저장된 FAISS 인덱스 로드
embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"})

# 현재 실행 디렉토리 확인
current_dir = os.getcwd()
faiss_path = os.path.join(current_dir, "../faiss_index")  # 상위 폴더에 있는 경우

# FAISS 벡터DB 로드 (보안 옵션 추가)
vectorstore = FAISS.load_local(faiss_path, embedding_model, allow_dangerous_deserialization=True)


# 저장된 문서의 ID 목록 확인
print(f"✅ 저장된 문서 ID 목록: {vectorstore.index_to_docstore_id}")

# 첫 번째 문서 내용 출력 (존재하는 경우)
if vectorstore.index_to_docstore_id:
    first_doc_id = list(vectorstore.index_to_docstore_id.values())[0]
    print("✅ 첫 번째 문서 내용:")
    print(vectorstore.docstore._dict[first_doc_id].page_content[:200])
else:
    print("🚨 FAISS 벡터DB에 저장된 문서가 없습니다.")
