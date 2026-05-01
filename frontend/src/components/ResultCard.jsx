/**
 * ResultCard.jsx
 *
 * Beginner-friendly note:
 * - A UI component dedicated to displaying the highest-level result
 *   (Decision, Risk Level, and Explanation).
 * - This lets our logic page stay focused on data-fetching, while
 *   this component focuses completely on styling the data.
 */

import React from "react";
import "./ResultCard.css";

function ResultCard({ decision, riskLevel, explanation }) {
  // If no decision passed yet, don't show the card.
  if (!decision) return null;

  // Let's figure out what color classes to attach
  // based on the risk level.
  // Converting to lowercase so "high" or "High" both work
  const risk = String(riskLevel).toLowerCase();

  let riskClass = "risk-low"; // default simple CSS class

  if (risk === "high" || risk === "critical") {
    riskClass = "risk-high";
  } else if (risk === "medium") {
    riskClass = "risk-med";
  }

  return (
    <div className="result-card">
      <div className="result-header">
        <div className="decision-wrapper">
          <span className="label">Decision:</span>
          <h2>{decision}</h2>
        </div>

        <div className={`risk-badge ${riskClass}`}>
          Risk: {String(riskLevel).toUpperCase()}
        </div>
      </div>

      <div className="explanation-section">
        <span className="label">Explanation:</span>
        <p className="explanation-text">{explanation}</p>
      </div>
    </div>
  );
}

export default ResultCard;
