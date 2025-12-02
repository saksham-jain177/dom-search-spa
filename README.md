# Semantic Search SPA

A powerful, AI-driven search tool that helps you find exactly what you're looking for within any website. Simply enter a URL and a question, and watch it find the most relevant content!

## Key Features

- **Smart Search**: Uses Artificial Intelligence (AI) to understand the *meaning* of your query, not just keyword matching.
- **Deep Content Analysis**: Breaks down websites into small, meaningful chunks (500 tokens) to find precise answers.
- **Visual Results**:
  - **Match Percentage**: See how confident the AI is in the result.
  - **DOM Path**: Know exactly where on the page the content is located.
  - **HTML Snippets**: View the raw code behind the text.
- **Robust Architecture**:
  - **Rate Limiting**: Prevents spam and ensures fair usage (5 requests/minute).
  - **Caching**: Instant results for repeated searches.
  - **Input Validation**: Ensures URLs and queries are correctly formatted.
- **Modern UI**: Beautiful dark mode design with helpful tooltips.

## Getting Started (Simple Guide)

Follow these steps to run the application on your computer.

### Prerequisites

1.  **Node.js** (v18+): [Download Here](https://nodejs.org/)
2.  **Python** (v3.9+): [Download Here](https://www.python.org/)
3.  **Pinecone API Key**:
    - Go to [Pinecone.io](https://app.pinecone.io/)
    - Sign up for a free account.
    - Click "Create API Key" and copy it.

### Step 1: Setup Backend (The Brain)

1.  Open your terminal (Command Prompt or PowerShell).
2.  Navigate to the backend folder:
    ```bash
    cd backend
    ```
3.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  Install the required tools:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Important**: Create a file named `.env` in the `backend` folder and add your API key:
    ```
    PINECONE_API_KEY=your_actual_api_key_here
    ```
6.  Start the server:
    ```bash
    python main.py
    ```
    You should see: `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Setup Frontend (The Interface)

1.  Open a **new** terminal window.
2.  Navigate to the frontend folder:
    ```bash
    cd frontend
    ```
3.  Install the interface tools:
    ```bash
    npm install
    ```
4.  Start the website:
    ```bash
    npm run dev
    ```
5.  Open your browser and go to: **http://localhost:3000**

## How to Use

1.  **Enter URL**: Paste the full address of the website you want to search (e.g., `https://en.wikipedia.org/wiki/Artificial_intelligence`).
2.  **Enter Query**: Type your question or keywords (e.g., "What is machine learning?").
3.  **Search**: Click the "Search" button.
4.  **Explore Results**:
    - **Relevance**: The green badge shows how well the result matches your query.
    - **Context**: Read the text snippet.
    - **Technical Details**: Hover over the "DOM Path" or "Relevance Score" for more info.
    - **Raw HTML**: Click "Show Raw HTML" to see the underlying code.

## Technical Architecture

- **Frontend**: Next.js (React), TypeScript, CSS Modules.
- **Backend**: FastAPI (Python).
- **AI/ML**:
  - **Tokenizer**: `bert-base-uncased` (Splits text into chunks).
  - **Embeddings**: `all-MiniLM-L6-v2` (Converts text to numbers).
  - **Vector DB**: Pinecone (Stores and searches these numbers).
- **Security & Performance**:
  - **SlowAPI**: Rate limiting.
  - **Cachetools**: In-memory caching.
  - **Validators**: Input sanitization.

## Troubleshooting

- **"Rate Limit Exceeded"**: You are making too many requests too fast. Wait a minute.
- **"Invalid URL"**: Make sure your URL starts with `http://` or `https://`.
- **Backend won't start**: Check if you created the `.env` file with your API Key.
- **Frontend error**: Ensure the backend terminal is running and shows no errors.

## API Documentation

The backend provides automatic documentation at: **http://localhost:8000/docs**

### Endpoint: `POST /search`
- **Input**: `{"url": "string", "query": "string"}`
- **Output**: JSON object with top 10 results, scores, and metadata.
