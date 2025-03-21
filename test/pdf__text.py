import re
import pdfplumber
import os

# 입력 및 출력 폴더 설정
pdf_folder = "pdf"  # PDF 파일이 있는 폴더
txt_folder = "pdf/txt2"  # 변환된 TXT 파일을 저장할 폴더

os.makedirs(txt_folder, exist_ok=True)  # TXT 저장 폴더 생성

def clean_text(text):
    """
    법 조문만 남기고 불필요한 내용을 제거하고 개행을 정리하는 함수.
    """
    # 법제처 및 기타 기관명 제거
    text = re.sub(r"법제처.*?국가법령정보센터", "", text, flags=re.MULTILINE)
    # 전화번호 제거 (예: 02-3150-1192)
    text = re.sub(r"\d{2,4}-\d{3,4}-\d{4}", "", text)
    # 문장 중간 개행 제거 (단어가 중간에 끊긴 경우)
    text = re.sub(r"(?<=[가-힣])\n(?=[가-힣])", "", text)  # 한글 문장 내 개행 제거
    # 조문(제X조) 앞에 개행 추가하여 가독성 향상
    text = re.sub(r"(제\d+조)", r"\n\1", text)
    # 중복된 법률 제목 제거 (첫 번째 줄이 법률명이라면 삭제)
    first_line = text.split("\n")[0]
    text = re.sub(fr"^{re.escape(first_line)}\n+", "", text, flags=re.MULTILINE)
    # 연속 개행 정리 (두 개 이상의 개행을 하나로 줄임)
    text = re.sub(r"\n{2,}", "\n", text).strip()
    return text

def pdf_to_text(pdf_path, txt_output_path):
    """
    PDF에서 법 조문만 추출하여 텍스트 파일로 저장하는 함수.
    """
    extracted_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            words = page.extract_words()  # 단어 블록 추출
            
            print(f"\n📌 [디버깅] 페이지 {i+1} 텍스트 확인:")
            print(text[:500] if text else "⚠️ 텍스트 없음 (OCR 필요할 수도 있음)")
            
            if words:
                print(f"📌 [디버깅] 페이지 {i+1} 단어 블록 수: {len(words)}")
            
            if text:
                cleaned_text = clean_text(text)
                extracted_text.append(cleaned_text)
    
    final_text = "\n".join(extracted_text)

    with open(txt_output_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(final_text)

    print(f"✅ 변환 완료: {txt_output_path}")

# 변환할 법률 목록
law_files = [
    "경찰관직무집행법.pdf"
]

# PDF → TXT 변환 실행
for law_file in law_files:
    pdf_path = os.path.join(pdf_folder, law_file)
    txt_output_path = os.path.join(txt_folder, law_file.replace(".pdf", ".txt"))
    
    if os.path.exists(pdf_path):
        pdf_to_text(pdf_path, txt_output_path)
    else:
        print(f"⚠️ 파일 없음: {pdf_path}")
