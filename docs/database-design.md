# Database Design - StudyPilot

The database uses PostgreSQL with the `pgvector` extension to store both structured relational data and unstructured vector embeddings in a single system.

## 1. ER Diagram

```mermaid
erDiagram
    USER ||--o{ DOCUMENT : owns
    USER ||--o{ CHAT_SESSION : creates
    USER ||--o{ STUDY_PLAN : has
    USER ||--o{ FLASHCARD_DECK : owns
    
    DOCUMENT ||--o{ DOCUMENT_CHUNK : contains
    DOCUMENT ||--o{ QUIZ : generates
    
    CHAT_SESSION ||--o{ MESSAGE : contains
    DOCUMENT ||--o{ MESSAGE : referenced_in
    
    FLASHCARD_DECK ||--o{ FLASHCARD : contains
    FLASHCARD ||--o{ REVIEW_LOG : tracks
    
    USER {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        datetime created_at
    }
    
    DOCUMENT {
        uuid id PK
        uuid user_id FK
        string filename
        string storage_path
        string status "pending | processing | indexed"
        datetime created_at
    }
    
    DOCUMENT_CHUNK {
        uuid id PK
        uuid document_id FK
        text content
        vector embedding "1536 dim"
        int page_number
        int chunk_index
    }
    
    CHAT_SESSION {
        uuid id PK
        uuid user_id FK
        string title
        datetime created_at
    }
    
    MESSAGE {
        uuid id PK
        uuid session_id FK
        uuid user_id FK
        string role "user | assistant"
        text content
        datetime created_at
    }
    
    QUIZ {
        uuid id PK
        uuid document_id FK
        uuid user_id FK
        jsonb quiz_data "questions, options, correct_answers"
        datetime created_at
    }
    
    FLASHCARD_DECK {
        uuid id PK
        uuid user_id FK
        string name
        datetime created_at
    }
    
    FLASHCARD {
        uuid id PK
        uuid deck_id FK
        text front
        text back
        int interval "days"
        int ease_factor "float"
        datetime next_review
        int repetitions
    }
    
    REVIEW_LOG {
        uuid id PK
        uuid flashcard_id FK
        int quality "0-5"
        datetime reviewed_at
    }
    
    STUDY_PLAN {
        uuid id PK
        uuid user_id FK
        jsonb plan_details
        datetime start_date
        datetime end_date
        string status "active | completed"
    }
```

## 2. Table Descriptions

### Users & Auth
- `USER`: Stores basic account information. `email` is unique for authentication.

### Knowledge Base (RAG)
- `DOCUMENT`: Metadata for uploaded PDFs.
- `DOCUMENT_CHUNK`: The core of the RAG system. Stores text segments and their corresponding embeddings. The `embedding` column uses `pgvector`.

### AI Interactions
- `CHAT_SESSION`: Groups messages into conversations.
- `MESSAGE`: Stores the history of user and AI interactions.

### Learning Tools
- `QUIZ`: Stores AI-generated quizzes as JSONB for flexibility in question types.
- `FLASHCARD`: Stores flashcards using the SM-2 spaced repetition model (interval, ease\_factor, repetitions).
- `REVIEW_LOG`: History of flashcard reviews to analyze learning curves.
- `STUDY_PLAN`: AI-generated schedules stored as JSONB.

## 3. Indexing Strategy
- **B-Tree Indexes**: On all Foreign Keys (`user_id`, `document_id`, `session_id`) for fast relational joins.
- **HNSW Index**: On `DOCUMENT_CHUNK.embedding` for fast approximate nearest neighbor (ANN) search.
- **GIN Index**: On `QUIZ.quiz_data` if complex JSON searches are needed.

## 4. Data Isolation
All queries to `DOCUMENT`, `DOCUMENT_CHUNK`, `MESSAGE`, `FLASHCARD`, and `STUDY_PLAN` must include a `WHERE user_id = :current_user_id` clause to ensure strict data isolation.
