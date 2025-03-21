import React, { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [elapsedTime, setElapsedTime] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [queryTokens, setQueryTokens] = useState(0);
  const [promptTokens, setPromptTokens] = useState(0);
  const [responseTokens, setResponseTokens] = useState(0);
  const [totalTokens, setTotalTokens] = useState(0);

  // 질문 제출 함수
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return; // 빈 입력 방지

    setAnswer("답변을 생성 중입니다...");
    setElapsedTime("");
    setQueryTokens(0);
    setPromptTokens(0);
    setResponseTokens(0);
    setTotalTokens(0);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/query",
        { question },
        { headers: { "Content-Type": "application/json" } }
      );

      setAnswer(response.data.answer);
      setElapsedTime(response.data.elapsed_time);

      // 토큰 수 업데이트
      setQueryTokens(response.data.tokens.query_tokens);
      setPromptTokens(response.data.tokens.prompt_tokens);
      setResponseTokens(response.data.tokens.response_tokens);
      setTotalTokens(response.data.tokens.total_tokens);

      // 기존 대화 기록 + 새 질문/답변을 chatHistory에 반영
      setChatHistory([
        ...response.data.chat_history, // FastAPI에서 반환한 전체 대화 기록 유지
        { question, answer: response.data.answer }
      ]);
    } catch (error) {
      setAnswer("오류 발생! 다시 시도해 주세요.");
    }
  };

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "50px auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      {/* 제목 */}
      <h1 style={{ color: "#1e40af", textAlign: "center" }}>📜 이한죽하 변호사 AI</h1>

      {/* 질문 입력 폼 */}
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px", textAlign: "center" }}>
        <input
          type="text"
          placeholder="법률 질문을 입력하세요..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit(e)} // Enter 키 제출 기능 추가
          style={{
            width: "100%",
            padding: "12px",
            marginBottom: "10px",
            border: "1px solid #ccc",
            borderRadius: "5px",
            fontSize: "16px",
          }}
        />
        <button
          type="submit"
          style={{
            backgroundColor: "#1e40af",
            color: "white",
            padding: "12px 24px",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            fontSize: "16px",
            transition: "background 0.3s ease",
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#162d6b")} // Hover 효과 추가
          onMouseOut={(e) => (e.target.style.backgroundColor = "#1e40af")}
        >
          질문하기
        </button>
      </form>

      {/* AI의 답변 */}
      <div
        style={{
          backgroundColor: "#f8f9fa",
          padding: "20px",
          borderRadius: "5px",
          marginBottom: "20px",
        }}
      >
        <h2 style={{ borderBottom: "2px solid #1e40af", paddingBottom: "5px" }}>📌 AI의 답변</h2>
        <p style={{ fontSize: "16px", lineHeight: "1.6", whiteSpace: "pre-line" }}>{answer}</p>
        <h3 style={{ marginTop: "10px", fontWeight: "bold" }}>⏳ 응답 시간: {elapsedTime}</h3>
      </div>

      {/* 토큰 사용량 표시 */}
      <div
        style={{
          backgroundColor: "#e3f2fd",
          padding: "20px",
          borderRadius: "5px",
          marginBottom: "20px",
        }}
      >
        <h2 style={{ borderBottom: "2px solid #1e40af", paddingBottom: "5px" }}>🔢 토큰 사용량</h2>
        <p><strong>질문 토큰:</strong> {queryTokens}</p>
        <p><strong>프롬프트 토큰:</strong> {promptTokens}</p>
        <p><strong>응답 토큰:</strong> {responseTokens}</p>
        <p><strong>총 사용 토큰:</strong> {totalTokens}</p>
      </div>

      {/* 대화 기록 */}
      <div style={{ marginTop: "30px" }}>
        <h2 style={{ borderBottom: "2px solid #1e40af", paddingBottom: "5px" }}>💬 대화 기록</h2>
        <ul style={{ listStyleType: "none", padding: "0" }}>
          {chatHistory.map((chat, index) => (
            <li
              key={index}
              style={{
                backgroundColor: "#eef2ff",
                padding: "15px",
                borderRadius: "5px",
                marginBottom: "10px",
              }}
            >
              <p style={{ color: "#1e40af", fontWeight: "bold", marginBottom: "5px" }}>
                <strong>Q:</strong> {chat.question}
              </p>
              <p
                style={{
                  color: "#000",
                  fontSize: "16px",
                  lineHeight: "1.6",
                  whiteSpace: "pre-line",
                }}
              >
                <strong>A:</strong> {chat.answer}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
