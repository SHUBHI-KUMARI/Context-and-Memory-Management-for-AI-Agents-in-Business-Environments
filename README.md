# Context and Memory Management System

This project contains a Python FastAPI backend with FAISS vector memory retrieval, and a simple React (Vite) frontend UI.

## Backend Setup Instructions

Open a new terminal and follow these steps to set up and run the backend.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate it (macOS/Linux)
   source venv/bin/activate
   # (For Windows use: venv\Scripts\activate)
   ```

3. **Install dependencies:**
   Make sure you have your requirements installed (FastAPI, FAISS, LangChain, etc.).
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   If using OpenAI embeddings or models, ensure you have a `.env` file in the `backend` folder:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   *(If you are exclusively using local HuggingFace embeddings like `all-MiniLM-L6-v2`, this may not be necessary)*

5. **Seed the memory database (Dummy Data):**
   Since the app uses an in-memory vector database, it starts empty on every restart. We have provided `seed_data.py` which contains predefined "dummy data" (e.g., past vendor issues, discounts, and supply chain experiences) so you can test the decision engine immediately.

   To inject this dummy data into the running backend, run:
   ```bash
   # Make sure the FastAPI server is running from Step 6 before running this!
   python seed_data.py
   ```
   *Tip: You can open `backend/seed_data.py` in your editor to add or modify the dummy memories to match your specific business use-case.*

6. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will now be listening at `http://127.0.0.1:8000`. You can also view the interactive API docs at `http://127.0.0.1:8000/docs`.


## Frontend Setup Instructions

Open a separate terminal window and follow these steps to start the UI.

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node modules:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The application will start, usually accessible at `http://localhost:5173`.
