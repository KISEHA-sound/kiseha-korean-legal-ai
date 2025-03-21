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

  // ✅ GraphQL 요청 함수
  const fetchAnswer = async (question) => {
    const GRAPHQL_URL = "http://127.0.0.1:8000/graphql";

    const query = `
      query SearchLaws($query: String!) {
        searchLaws(query: $query)
      }
    `;

    try {
      const response = await axios.post(GRAPHQL_URL, {
        query,
        variables: { query: question }, // ✅ 변수명 맞춤
      });

      if (response.data.errors) {
        throw new Error("GraphQL 오류 발생!");
      }

      // ✅ 올바른 필드 참조
      const data = response.data.data.searchLaws;

      // ✅ 배열을 문자열로 변환하여 표시
      const formattedAnswer = data.join("\n\n");

      setAnswer(formattedAnswer);
      setElapsedTime(response.data.data.elapsedTime || "N/A");

      // ✅ 토큰 사용량 업데이트 (GraphQL 응답에 따라 반영)
      setQueryTokens(response.data.data.tokens?.queryTokens || 0);
      setPromptTokens(response.data.data.tokens?.promptTokens || 0);
      setResponseTokens(response.data.data.tokens?.responseTokens || 0);
      setTotalTokens(response.data.data.tokens?.totalTokens || 0);

      // ✅ 최신 대화 기록 유지 (최대 3개만)
      setChatHistory((prevHistory) => {
        const updatedHistory = [...prevHistory, { question, answer: formattedAnswer }];
        return updatedHistory.slice(-3); // 최신 3개만 유지
      });

    } catch (error) {
      setAnswer("오류 발생! 다시 시도해 주세요.");
      console.error(error);
    }
  };

  // ✅ 질문 제출 함수
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setAnswer("답변을 생성 중입니다...");
    setElapsedTime("");
    setQueryTokens(0);
    setPromptTokens(0);
    setResponseTokens(0);
    setTotalTokens(0);

    await fetchAnswer(question);
    setQuestion("");
  };

  return (
    <div style={{ maxWidth: "800px", margin: "50px auto", fontFamily: "Arial, sans-serif" }}>
      {/* 제목 */}
      <h1 style={{ color: "#1e40af", textAlign: "center" }}>📜 이한죽하 변호사 AI (GraphQL 적용)</h1>

      {/* 질문 입력 폼 */}
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px", textAlign: "center" }}>
        <input
          type="text"
          placeholder="법률 질문을 입력하세요..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit(e)}
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
          onMouseOver={(e) => (e.target.style.backgroundColor = "#162d6b")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#1e40af")}
        >
          질문하기
        </button>
      </form>

      {/* AI의 답변 */}
      <div style={{ backgroundColor: "#f8f9fa", padding: "20px", borderRadius: "5px", marginBottom: "20px" }}>
        <h2 style={{ borderBottom: "2px solid #1e40af", paddingBottom: "5px" }}>📌 AI의 답변</h2>
        <p style={{ fontSize: "16px", lineHeight: "1.6", whiteSpace: "pre-line" }}>{answer}</p>
        <h3 style={{ marginTop: "10px", fontWeight: "bold" }}>⏳ 응답 시간: {elapsedTime}</h3>
      </div>

      {/* 토큰 사용량 표시 */}
      <div style={{ backgroundColor: "#e3f2fd", padding: "20px", borderRadius: "5px", marginBottom: "20px" }}>
        <h2 style={{ borderBottom: "2px solid #1e40af", paddingBottom: "5px" }}>🔢 토큰 사용량</h2>
        <p><strong>질문 토큰:</strong> {queryTokens}</p>
        <p><strong>프롬프트 토큰:</strong> {promptTokens}</p>
        <p><strong>응답 토큰:</strong> {responseTokens}</p>
        <p><strong>총 사용 토큰:</strong> {totalTokens}</p>
      </div>

      {/* ✅ 대화 기록 표시 */}
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