from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import os
import re

# 저장할 법률 파일 경로 (경찰관 직무 집행법만 저장)
law_name = "Police_Duties_Act"
file_path = "../pdf/txt/경찰관직무집행법.txt"

# FAISS 인덱스 저장 경로 설정
FAISS_INDEX_DIR = "../faiss_indexes"
index_path = os.path.join(FAISS_INDEX_DIR, law_name)
os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

# SBERT 임베딩 모델 (768차원)
embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli", model_kwargs={"device": "cpu"})

# 기존 벡터DB 덮어쓰기 여부 설정
overwrite = True  

# 법률 텍스트 로드
if not os.path.exists(file_path):
    print(f"❌ 오류: 파일을 찾을 수 없습니다 - {file_path}")
else:
    print(f"📖 {law_name} 벡터DB를 생성하는 중...")

    with open(file_path, "r", encoding="utf-8") as f:
        text_content = f.read()

    # 1. 정규표현식으로 법 조항 단위로 분할
    def split_law_articles(text):
        pattern = r"(제\d+조\([^)]+\))"  # "제123조(제목)" 패턴을 기준으로 분할
        matches = re.split(pattern, text)
        
        articles = []
        for i in range(1, len(matches), 2):  # 번호와 본문을 합쳐서 리스트 생성
            article_title = matches[i]
            article_body = matches[i+1] if i+1 < len(matches) else ""
            articles.append(article_title + article_body.strip())
        
        return articles

    text_chunks = split_law_articles(text_content)

    if not text_chunks:
        print(f"⚠️ {law_name}에서 유효한 텍스트 청크를 찾을 수 없습니다. 건너뜁니다...")
    else:
        # 2. 각 청크에 메타데이터 추가 (출처 정보 + 법 조항 번호)
        documents = []
        for chunk in text_chunks:
            article_num = re.search(r"제\d+조", chunk)  # 조항 번호 추출
            article_title = article_num.group() if article_num else "Unknown"
            documents.append(Document(
                page_content=chunk,
                metadata={"source": law_name, "article": article_title}  # 법명 + 조항 번호 추가
            ))

        # 3. FAISS 벡터DB 생성 (`from_documents` 사용 + L2 정규화)
        vector_store = FAISS.from_documents(documents, embedding_model, normalize_L2=True)

        # 4. 개별 폴더에 저장
        vector_store.save_local(index_path)

        print(f"✅ {law_name} 벡터DB가 저장되었습니다! ({len(text_chunks)}개의 조항이 처리됨)")

print("🎉 경찰관 직무 집행법 데이터가 FAISS 벡터DB에 저장 완료되었습니다! 🚀")
