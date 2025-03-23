# 💼 나만의 AI 변호사: GPT-3.5/4 + LangChain RAG 기반 법률 상담 시스템

## 📑 목차
- [✨ 개요](#-개요)
- [🚀 사용 기술](#-사용-기술)
- [🗂️ 폴더 구조](#%EF%B8%8F-프로젝트-폴더-구조)
- [🔍 핵심 기능](#-주요-기능-요약)
- [✅ 현재 결과](#-현재-결과-요약)
- [⚙️ 시스템 구조](#-시스템-구조와-흐름)
- [🌱 확장 가능성](#-확장-가능성)

## ✨ 개요
GPT-3.5 및 GPT-4, LangChain과 RAG 기법을 활용하여 사용자의 법률 질문에 대해 분석과 전략을 제공하는 개인 맞춤형 AI 법률 상담 시스템입니다.

## ▶️ 시연 영상
👉 클릭하면 실제 사용 장면을 영상으로 확인할 수 있습니다!
[![AI 변호사 시연 영상](images/메인화면.png)](https://youtube.com/shorts/YbzWqVs7EgY?feature=share)

## 🚀 사용 기술
- LLM: GPT-3.5-turbo / GPT-4-turbo - 자연어 처리 및 답변 생성
- LangChain: RAG 구조 구성에 사용되며, LLM 호출(GPT API)은 LangChain 없이 직접 구현
- FAISS + KoSBERT: 한국어 문서를 벡터화하여 유사도 검색 (모델: `jhgan/ko-sbert-nli`)
- FastAPI: 백엔드 API 서버 구축
- React: 프론트엔드 사용자 인터페이스

## 🗂️ 프로젝트 폴더 구조
```
kiseha-p1/
├── backend/            # FastAPI 백엔드 (main.py)
├── front/              # React 프론트엔드 (App.js)
├── faiss_indexes/      # FAISS 벡터 DB (법률 종류별 분리)
├── pdf/
│   └── txt/            # 원본 법률 정제된 텍스트 파일 (형법, 경찰관직무집행법 등)
├── images/             # 결과 비교 이미지 자료
```

## 🔍 주요 기능 요약

### ✅ FAISS 벡터 DB 구축
- `pdf/txt`의 법률 원문을 정규표현식으로 `제XX조` 기준 분할
- 각 조항을 청크화 후, `FAISS.from_documents()`로 저장
- 문서마다 `source`, `article` 메타데이터 추가
- `normalize_L2=True` 설정으로 코사인 유사도 기반 검색 가능

#### FAISS 개선 전 결과(기존 DB)
![FAISS 개선 전 결과](images/FAISS벡터DB_before.png)  
**조항 기준이 아닌 단순 청크 분할 → 유사도 낮고 정확도 떨어짐**

#### FAISS 개선 후 결과(제XX조 기반 정제된 DB)
![제XX조 기반 정제된 DB](images/FAISS벡터DB_after.png)
**정규표현식으로 제XX조 기준 분할 → 유사도 높고 정밀도 향상**

### ✅ 법률 질의 RAG 흐름
- 프론트에서 질문 + 법률 종류 전달 → 백엔드에서 해당 FAISS DB 로딩
- `Top-K` 관련 법 조항 검색 (예: 2~3개)  - 현재: 2개
- 관련 조항 기반 `context` 구성 → GPT에 전달

#### 유사도 기준 비교(개선 전)
![유사도 기준 비교](images/유사도_before.png)
#### 유사도 기준 비교(개선 후)
![유사도 기준 비교](images/유사도_after.png)
  

### ✅ GPT 기반 법률 상담 생성
- GPT-3.5 / GPT-4 모델로 응답 생성 - 현재 : gpt-4-turbo
- 피해자 / 피고인 입장을 나눠 전략 제시
- 핵심 법 조항, 법적 리스크, 대응 전략을 포함한 실무형 답변

## 🧠 프롬프트 구조
```python
system_prompt = """
당신은 대한민국의 법률 전문 변호사입니다.
사용자는 특정 상황에 대한 법률적 질문을 하고 있으며, 아래의 관련 법률 조항을 기반으로 답변해야 합니다.

다음 항목을 반드시 포함해 주세요:
1. 해당 조항의 핵심 요약 (조항 번호 포함)
2. 발생 가능한 법적 리스크 분석
3. 피해자 입장에서의 대응 전략
4. 피고인 입장에서의 방어 전략
"""
```
#### 프롬프트 개선 전 결과 예시
![프롬프트 비교](images/결과_before.png)
#### 프롬프트 개선 후 결과 - 형법 질문
![프롬프트 비교](images/결과(형법)_after.png)
#### 프롬프트 개선 후 결과 - 경찰관직무집행법 질문
![프롬프트 비교](images/결과(경찰관)_after.png)

## ✅ 현재 결과 요약
- GPT-4 기반으로 질문에 가장 관련 있는 법률 조항 자동 요약
- 피해자 / 피고인 입장에서 각각 법적 대응 전략까지 제시
- 정확한 조항 번호 + 리스크 분석 + 조치 방안 포함
- 단순 정보 제공이 아닌 상황 중심 실무 상담 가능

## ⚙️ 시스템 구조와 흐름
- React에서 법률 종류 선택 → 질문 전송
- FastAPI에서 해당 법률의 FAISS DB 로드
- LangChain RAG가 관련 법 조항 Top-K 추출
- GPT-3.5/4가 요약 + 전략 제시

## 🧠 LLM & 벡터 DB 조합의 강점
- 법 조항을 ‘제XX조’ 단위로 정리해 맥락 유지
- `FAISS.from_documents()` + 메타데이터 → 출처 추적 가능
- 코사인 유사도 기반 정렬로 정확한 검색 결과 보장
- 결과에 따라 토큰 수 / 응답 시간도 리턴

## 🌱 확장 가능성
- 형법, 민법 외에 행정법, 헌법 등등 DB로 확장 가능
- 법률 선택이 아니라 질문을 하면 법률을 자동 선택하여 요약, 리스크 리포트 생성, 해당 관련 판례 추천 등 기능 추가 가능 - 이 기능을 넣기 위해 공부 중 입니다!


