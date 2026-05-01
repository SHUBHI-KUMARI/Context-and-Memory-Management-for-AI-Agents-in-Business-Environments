/**
 * api.js
 * 
 * Beginner-friendly note:
 * - This file handles all communication with our Python FastAPI backend.
 * - We keep backend URLs here so it's easy to change later.
 * - Right now, we assume the backend is running locally on port 8000.
 */

// If you want to deploy later, you would change this base URL
const BASE_URL = 'http://127.0.0.1:8000';

/**
 * Send a query to the decision engine.
 * 
 * @param {string} query User input text, e.g. "Supplier XYZ"
 * @returns {Promise<Object>} The decision, risk_level, explanation, and memories
 */
export const fetchDecision = async (query) => {
  try {
    // POST request to backend endpoint
    const response = await fetch(`${BASE_URL}/decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // send our query string as JSON
      // Note: We use top_k: 2 so we don't accidentally retrieve the entire database 
      // when we only have 5 dummy items total!
      body: JSON.stringify({ query: query, top_k: 2 }),
    });

    if (!response.ok) {
      throw new Error(`Server returned error: ${response.statusText}`);
    }

    // Backend responds with structured JSON
    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('API fetchDecision error:', error);
    throw error;
  }
};
