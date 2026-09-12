# ✈️ TripGenie AI

> AI-powered travel planning agent that creates personalized, budget-aware itineraries using LangGraph, LangChain, Groq, RAG, MCP, FastAPI, React, and PostgreSQL.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-Frontend-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-orange)
![LangChain](https://img.shields.io/badge/LangChain-GenAI-green)
![Groq](https://img.shields.io/badge/Groq-LLM-black)
![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)

---

## 📌 Overview

TripGenie AI is an intelligent travel assistant that generates personalized day-by-day travel plans based on destination, duration, travelers, budget, and interests.

It combines agentic AI, RAG, external tools, MCP, and persistent database storage in an end-to-end GenAI application.

---

## ✨ Features

- AI-powered personalized travel planning
- Day-by-day itinerary generation
- Budget and activity cost estimation
- Weather and attraction information
- Currency conversion and calculations
- RAG-based travel knowledge retrieval
- MCP tool integration
- Ask TripGenie AI assistant
- PostgreSQL trip storage

---

## 🛠 Tech Stack

- **AI:** Groq, LangChain, LangGraph
- **RAG:** ChromaDB, Sentence Transformers
- **Backend:** FastAPI, Pydantic, SQLAlchemy
- **Database:** PostgreSQL
- **Integration:** MCP
- **Frontend:** React, Vite, JavaScript, CSS

---

## 🏗 Architecture

```text
React
  ↓
FastAPI
  ↓
LangGraph Agent
  ↓
Tools + RAG + MCP
  ↓
Groq LLM
  ↓
Travel Plan
  ↓
PostgreSQL
```

---

## 📸 Screenshots

### Home Page

<img width="1421" height="872" alt="TripGeni-HomePage" src="https://github.com/user-attachments/assets/47806485-41c0-4dd6-adce-ab1199c3021a" />


### Generated Travel Plan

<img width="1577" height="765" alt="tripgenie-trip generate page" src="https://github.com/user-attachments/assets/302846f8-b5bb-497a-8f5e-23da014cd85c" />
<img width="1047" height="835" alt="TripGenie-result 1" src="https://github.com/user-attachments/assets/82aabc81-e7df-4ac7-8a89-7fc9872b94d9" />



---

## 🚀 Setup

### Clone Repository

```bash
git clone https://github.com/sakshikal532004/TripGenie.git
cd TripGenie
```

### Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create `.env`

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
DATABASE_URL=YOUR_POSTGRESQL_CONNECTION_STRING
```

### Run Backend

```bash
uvicorn backend.main:app --reload
```

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 👩‍💻 Author

**Sakshi Kalyankar**

- GitHub: https://github.com/sakshikal532004
- LinkedIn: https://www.linkedin.com/in/sakshi-kalyankar

---

## License

© 2026 Sakshi Kalyankar. All rights reserved.
