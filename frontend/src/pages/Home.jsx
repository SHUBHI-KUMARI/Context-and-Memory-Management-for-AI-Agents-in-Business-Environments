/**
 * Home.jsx
 *
 * Beginner-friendly note:
 * - This is our main "Page". It connects the Input, Result, and Memories together.
 * - We hold the "app state" inside useState.
 * - When a user clicks Analyze in <InputBox/>, the function here runs
 *   to fetch data, and then we send the data down to <ResultCard/>.
 */

import React, { useState } from "react";
import { fetchDecision } from "../services/api";

// Components
import InputBox from "../components/InputBox";
import ResultCard from "../components/ResultCard";
import MemoryList from "../components/MemoryList";

function Home() {
  // --- STATE VARIABLES ---
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Data we get back from the API
  const [decision, setDecision] = useState(null);
  const [riskLevel, setRiskLevel] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [memories, setMemories] = useState([]);

  // --- THE MAGIC BEAN PIPELINE (Submit Handler) ---
  const handleQuerySubmit = async (queryText) => {
    // 1. Clean the slate
    setLoading(true);
    setErrorMsg(null);
    setDecision(null);
    setRiskLevel(null);
    setExplanation(null);
    setMemories([]);

    try {
      // 2. Make the API Call from services/api.js
      const data = await fetchDecision(queryText);

      // 3. Populate state with API Response
      setDecision(data.decision);
      setRiskLevel(data.risk_level);
      setExplanation(data.explanation);
      setMemories(data.memories || []);
    } catch (err) {
      // Uh oh. The backend is down or returned an error.
      setErrorMsg(
        "Failed to connect to the brain (backend). Ensure the Python API is running!",
      );
      console.error(err);
    } finally {
      // 4. Stop loading ring
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "0 1rem" }}>
      <p
        style={{ textAlign: "center", color: "#4b5563", marginBottom: "2rem" }}
      >
        Ask the system to process an action, and it will query its memory.
      </p>

      {/* 1. Input Box (Wait for query text from the child logic) */}
      <InputBox onSubmit={handleQuerySubmit} isLoading={loading} />

      {/* 2. Error box (Red text) */}
      {errorMsg && (
        <div
          style={{
            color: "red",
            textAlign: "center",
            marginBottom: "1rem",
            padding: "1rem",
            backgroundColor: "#fee2e2",
            borderRadius: "6px",
          }}
        >
          {errorMsg}
        </div>
      )}

      {/* 3. The Big Decision Result */}
      <ResultCard
        decision={decision}
        riskLevel={riskLevel}
        explanation={explanation}
      />

      {/* 4. The raw memory evidence below */}
      <MemoryList memories={memories} />
    </div>
  );
}

export default Home;
