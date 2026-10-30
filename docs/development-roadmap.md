# Development Roadmap - StudyPilot

This roadmap breaks down the construction of StudyPilot into manageable phases, focusing on delivering a functional MVP (Minimum Viable Product) first.

## Phase 1: Foundation & Auth (Weeks 1-2)
**Goal**: Establish the core infrastructure and user identity system.
- [ ] Set up Project Structure (Modular Monolith).
- [ ] Configure PostgreSQL + `pgvector`.
- [ ] Implement User Model and Auth Service (JWT, Registration, Login).
- [ ] Build Basic API Shell with FastAPI.
- [ ] **Acceptance Criteria**: User can register, login, and receive a valid JWT.

## Phase 2: Document Ingestion & RAG (Weeks 3-5)
**Goal**: Enable users to upload documents and ask questions.
- [ ] Implement PDF Upload and Storage.
- [ ] Build Background Worker for PDF Processing (Text extraction, Chunking).
- [ ] Implement Embedding Pipeline (OpenAI/Anthropic/Local).
- [ ] Design and Implement the RAG LangGraph workflow.
- [ ] Create the Chat API endpoints.
- [ ] **Acceptance Criteria**: User can upload a PDF and get a grounded answer to a question about it.

## Phase 3: AI Learning Tools (Weeks 6-8)
**Goal**: Transform static documents into interactive study materials.
- [ ] Implement Quiz Generation workflow (LangGraph).
- [ ] Implement Flashcard Generation workflow.
- [ ] Build Quiz submission and evaluation logic.
- [ ] Implement Flashcard CRUD API.
- [ ] **Acceptance Criteria**: User can generate a quiz and a deck of flashcards from an uploaded document.

## Phase 4: Retention & Planning (Weeks 9-11)
**Goal**: Optimize long-term learning with SRS and Planning.
- [ ] Implement SM-2 Spaced Repetition Algorithm.
- [ ] Build "Due for Review" flashcard logic.
- [ ] Implement AI Study Plan generation.
- [ ] Build Learning Analytics dashboard.
- [ ] **Acceptance Criteria**: User can review flashcards on a schedule and see their progress over time.

## Phase 5: Polish & Deployment (Weeks 12+)
**Goal**: Production-ready stability and UX.
- [ ] Develop Streamlit/React Frontend.
- [ ] Implement full error handling and logging.
- [ ] Perform Security Audit (based on `docs/security.md`).
- [ ] Deploy to Cloud/VPS using Docker.
- [ ] **Acceptance Criteria**: Full end-to-end flow working in a deployed environment.

---

## Summary of Deliverables
| Phase | Focus | Primary Tech | Key Outcome |
| :--- | :--- | :--- | :--- |
| 1 | Infrastructure | FastAPI, Postgres | Auth System |
| 2 | Knowledge | pgvector, LangGraph | RAG Chat |
| 3 | Content | LangGraph, JSONB | Quizzes/Cards |
| 4 | Retention | Python, SQL | SRS/Analytics |
| 5 | Delivery | Streamlit, Docker | Live App |
