/*
 * InputBox.jsx
 *
 * Beginner-friendly note:
 * - A reusable component just for typing a query and submitting it.
 * - By passing the `onSubmit` and `isLoading` props down, it stays separate
 *   from the overall page state (good React habit).
 */

import React, { useState } from "react";
import "./InputBox.css";

function InputBox({ onSubmit, isLoading }) {
  // Local state to keep track of what the user is typing
  const [text, setText] = useState("");

  // Run when "Analyze" is clicked or Enter is pressed
  const handleSubmit = (e) => {
    // prevent default form submit (page reload)
    e.preventDefault();

    // Only submit if user typed something
    if (text.trim() !== "") {
      onSubmit(text.trim());
    }
  };

  return (
    <form className="input-box-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="input-field"
        placeholder='e.g. "Process invoice for Supplier XYZ"'
        value={text}
        // update exactly what is typed into our state
        onChange={(e) => setText(e.target.value)}
        disabled={isLoading}
      />
      <button
        type="submit"
        className="submit-button"
        disabled={isLoading || !text.trim()}
      >
        {isLoading ? "Thinking..." : "Analyze"}
      </button>
    </form>
  );
}

export default InputBox;
