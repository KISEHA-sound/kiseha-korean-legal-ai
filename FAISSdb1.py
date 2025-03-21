from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import os
import re

# 저장할 법률 파일 목록 (경로 설정 유지)
law_files = {
    "Police_Duties_Act": "pdf/txt/경찰관직무집행법.txt",
    "Labor_Standards_Act": "pdf/txt/근로기준법.txt",
    "Road_Traffic_Act": "pdf/txt/도로교통법.txt",
    "Civil_Law": "pdf/txt/민법.txt",
    "Criminal_Law": "pdf/txt/형법.txt"
}

# FAISS 인덱스 저장 경로 설정
FAISS_INDEX_DIR = "faiss_indexes"
os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

# SBERT 임베딩 모델 (768차원)
embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"})

# 기존 벡터DB 덮어쓰기 여부 설정
overwrite = True  

# 정규표현식으로 법 조항 단위로 분할
def split_law_articles(text):
    pattern = r"(제\d+조\([^)]+\))"  # "제123조(제목)" 패턴을 기준으로 분할
    matches = re.split(pattern, text)

    articles = []
    for i in range(1, len(matches), 2):  # 번호와 본문을 합쳐서 리스트 생성
        article_title = matches[i]
        article_body = matches[i+1] if i+1 < len(matches) else ""
        articles.append(article_title + article_body.strip())

    return articles

# 모든 법률에 대해 FAISS 벡터DB 생성
for law_name, file_path in law_files.items():
    index_path = os.path.join(FAISS_INDEX_DIR, law_name)

    # 기존 벡터DB가 있고, 덮어쓰지 않는다면 스킵
    if not overwrite and os.path.exists(index_path):
        print(f"⚠️ {law_name} 벡터DB가 이미 존재합니다. 건너뜁니다...")
        continue

    print(f"📖 {law_name} 벡터DB를 생성하는 중...")

    # 법률 파일 존재 여부 확인
    if not os.path.exists(file_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다 - {file_path}")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        text_content = f.read()

    # 법 조항 단위로 분할
    text_chunks = split_law_articles(text_content)

    if not text_chunks:
        print(f"⚠️ {law_name}에서 유효한 텍스트 청크를 찾을 수 없습니다. 건너뜁니다...")
        continue

    # 각 청크에 메타데이터 추가 (출처 정보 + 법 조항 번호)
    documents = []
    for chunk in text_chunks:
        article_num = re.search(r"제\d+조", chunk)  # 조항 번호 추출
        article_title = article_num.group() if article_num else "Unknown"
        documents.append(Document(
            page_content=chunk,
            metadata={"source": law_name, "article": article_title}  # 법명 + 조항 번호 추가
        ))

    # FAISS 벡터DB 생성 (`from_documents` 사용 + L2 정규화 적용)
    vector_store = FAISS.from_documents(documents, embedding_model, normalize_L2=True)

    # 개별 폴더에 저장
    vector_store.save_local(index_path)

    print(f"✅ {law_name} 벡터DB가 저장되었습니다! ({len(text_chunks)}개의 조항이 처리됨)")

print("🎉 모든 법률 데이터가 FAISS 벡터DB에 저장 완료되었습니다! 🚀")
