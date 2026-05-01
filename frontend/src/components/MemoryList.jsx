/**
 * MemoryList.jsx
 *
 * Beginner-friendly note:
 * - This file displays an array of past memories that were fetched.
 * - This allows the user to see the exact items the decision was based on.
 */

import React from "react";
import "./MemoryList.css";

function MemoryList({ memories }) {
  // If zero memories, don't show the list
  if (!memories || memories.length === 0) {
    return null;
  }

  return (
    <div className="memory-list-container">
      <h3>Relevant Memories</h3>
      <ul className="memory-list">
        {memories.map((memoryItem) => {
          // Because memory is nested inside 'memoryItem' (for some API responses)
          // or at the top level, let's extract it safely:
          const item = memoryItem.memory ? memoryItem.memory : memoryItem;

          // React needs a unique string `key` for every item in an array rendering
          const key = item.id || Math.random().toString();

          return (
            <li
              key={key}
              className={`memory-item ${item.is_stale ? "stale" : "fresh"}`}
            >
              <div className="memory-header">
                {/* The tags (type vs stale/fresh check) */}
                <span className="memory-type">{item.type}</span>
                {item.is_stale && (
                  <span className="stale-badge">Stale/Old</span>
                )}
              </div>

              {/* The main text */}
              <p className="memory-content">{item.content}</p>

              {/* Extra details (optional, but requested for transparency) */}
              <div className="memory-meta">
                <span>
                  Date: {new Date(item.timestamp).toLocaleDateString()}
                </span>
                {/* If there's an issue_type, print it */}
                {item.metadata?.issue_type && (
                  <span> | Issue: {item.metadata.issue_type}</span>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default MemoryList;
