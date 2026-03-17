# ThreadCore

ThreadCore is a production-ready, multi-user AI knowledge processing system that ingests media (YouTube, audio, video, text), converts it into embeddings, and enables thread-based contextual intelligence using a scalable backend architecture.

Built with FastAPI, Redis, PostgreSQL, and Qdrant.

---

## 🚀 Features

- Multi-user authentication (JWT-based)
- Media ingestion (YouTube, audio, video, text)
- Background processing pipeline
- Automatic transcription & chunking
- Embedding generation
- Vector storage with Qdrant
- Thread-based conversation memory
- Redis status tracking
- Scalable FastAPI backend
- Streamlit frontend interface

---

## 🧠 Architecture Overview

ThreadCore follows a modular backend architecture:

User → FastAPI → Background Task → Processing Pipeline → Embeddings → Qdrant  
                                  ↓  
                               Redis (status tracking)  

### Core Components

- **FastAPI** → API layer
- **PostgreSQL** → Users & thread metadata
- **Redis** → Task state management
- **Qdrant** → Vector storage
- **Streamlit** → Frontend UI

---


## 🔐 Authentication Flow

- Passwords hashed using bcrypt
- Login generates JWT token
- Protected routes require Bearer token
- user_id extracted from JWT
- Embeddings filtered per user for data isolation

---

## ⚙️ Processing Pipeline

1. Media ingestion (YouTube / audio / video / text)
2. Transcription (if required)
3. Chunking
4. Document conversion
5. Metadata attachment (thread_id, user_id, media_type)
6. Embedding generation
7. Vector storage in Qdrant

---

## 🧵 Thread-Based System

Each upload is associated with:

- `thread_id`
- `user_id`
- `media_type`

This enables:

- Multi-session conversations
- User-level data isolation
- Contextual retrieval

---

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/threadcore.git
cd threadcore

