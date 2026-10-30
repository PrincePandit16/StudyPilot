# API Design - StudyPilot

The API is designed as a RESTful service using FastAPI, providing structured endpoints for the frontend to interact with the core services.

## 1. Authentication
All endpoints except `/auth/*` require a Bearer Token in the `Authorization` header.

### Auth Endpoints
- `POST /auth/register`: Register a new account.
- `POST /auth/login`: Authenticate and receive a JWT.
- `POST /auth/logout`: Invalidate the session.
- `GET /auth/me`: Get current user profile.

## 2. Document Management
- `POST /documents/upload`: Upload a PDF file.
- `GET /documents`: List all uploaded documents for the user.
- `GET /documents/{id}`: Get document metadata and status.
- `DELETE /documents/{id}`: Remove document and its associated chunks.

## 3. AI Learning Tools

### RAG Chat
- `POST /chat/sessions`: Create a new chat session.
- `GET /chat/sessions`: List previous sessions.
- `POST /chat/sessions/{id}/messages`: Send a message to the AI (RAG powered).
- `GET /chat/sessions/{id}/messages`: Retrieve message history for a session.

### Quizzes & Flashcards
- `POST /documents/{id}/quiz`: Generate a quiz from a specific document.
- `POST /quizzes/{id}/submit`: Submit quiz answers for evaluation.
- `POST /documents/{id}/flashcards`: Generate flashcards from a document.
- `GET /flashcards`: List flashcards due for review (SRS filtered).
- `PATCH /flashcards/{id}/review`: Update flashcard state after review (SM-2 update).

### Study Planning
- `POST /study-plans/generate`: Generate a plan based on goals and documents.
- `GET /study-plans/active`: Get the current active study plan.

## 4. Analytics & Profile
- `GET /analytics/progress`: Get overall learning progress.
- `GET /analytics/mastery`: Get mastery levels for flashcard decks.
- `PATCH /profile`: Update user preferences.

## 5. Error Handling
The API uses standard HTTP status codes:
- `200 OK`: Success.
- `201 Created`: Resource created.
- `400 Bad Request`: Validation error.
- `401 Unauthorized`: Authentication failed.
- `403 Forbidden`: User doesn't own the resource.
- `404 Not Found`: Resource not found.
- `500 Internal Server Error`: Server-side crash.

### Error Response Body
```json
{
  "error": "Error Code",
  "message": "Human readable description",
  "details": {}
}
```
