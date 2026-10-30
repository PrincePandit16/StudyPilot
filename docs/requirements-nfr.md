# Non-Functional Requirements - StudyPilot

## 1. Performance
- **Latency**: AI responses should start streaming within 2 seconds. Vector retrieval should occur in < 500ms.
- **Scalability**: The modular monolith should handle concurrent requests through background worker processing for heavy tasks (PDF indexing, quiz generation).
- **Availability**: The system should aim for 99% uptime.

## 2. Security & Privacy
- **Data Isolation**: Strict row-level security or tenant-based filtering to ensure users never access other users' data.
- **Authentication**: Use industry-standard protocols (e.g., JWT, OAuth2) for secure session management.
- **Input Validation**: Strict validation of PDF uploads to prevent malicious file injection.
- **AI Safety**: Implementation of prompt filtering to prevent jailbreaking or misuse of the AI agents.

## 3. Maintainability & Extensibility
- **Modular Architecture**: Use a clear separation between API, Services, and Repositories to allow independent updates.
- **Provider Agnostic**: AI integrations should be wrapped in an interface to allow switching between LLM providers (e.g., OpenAI to Anthropic or Local LLMs via Ollama).
- **Documentation**: All API endpoints must be documented (e.g., OpenAPI/Swagger).

## 4. Cost Efficiency (Solo Developer/OSS Focus)
- **Open Source**: Prioritize OSS technologies (PostgreSQL, FastAPI, LangGraph, ChromaDB/PGVector).
- **Resource Optimization**: Use asynchronous processing to minimize server load during document ingestion.
- **Free Tier Compatibility**: Design the system to work within the free tiers of cloud providers or on a single VPS.

## 5. Usability
- **Responsive Design**: The frontend must be usable on both desktop and mobile devices.
- **Intuitive UX**: AI interactions should be conversational and minimize the need for complex prompt engineering by the user.
