# Security Design - StudyPilot

StudyPilot handles user-uploaded intellectual property and personal data. Security is integrated into every layer of the architecture.

## 1. Authentication & Authorization
- **Identity**: JWT (JSON Web Tokens) for stateless authentication.
- **Tokens**: Short-lived Access Tokens (15m) and long-lived Refresh Tokens (7d).
- **Passwords**: Hashed using `Argon2` or `bcrypt` with unique salts.
- **Authorization**: Role-Based Access Control (RBAC), although the primary role is `USER`.

## 2. User Data Isolation (The "Hard Wall")
To prevent cross-user data leakage:
- **Row-Level Filtering**: Every database query for user-specific data MUST include the `user_id` in the `WHERE` clause.
- **Service Layer Enforcement**: The `Repository` methods are designed to take `user_id` as a mandatory first argument.
- **Vector Store Isolation**: Vector queries to `pgvector` use a metadata filter: `filter={"user_id": current_user_id}`.

## 3. Document & File Security
- **Filename Sanitization**: All uploaded filenames are sanitized to prevent path traversal attacks.
- **Storage Isolation**: Files are stored in directories named by `user_id` (`/storage/{user_id}/{doc_id}.pdf`).
- **PDF Validation**: Files are validated for MIME type and size before processing.

## 4. AI Security
- **Prompt Injection Mitigation**: 
    - Use of system prompts to strictly define AI behavior.
    - Input sanitization for user queries.
    - Use of "LLM-as-a-Judge" (in LangGraph) to verify that AI responses don't reveal system prompts or perform unauthorized actions.
- **Data Privacy**: Ensure that documents are not used for training the underlying LLMs (using API providers with "zero data retention" or "no training" policies).

## 5. Infrastructure Security
- **HTTPS**: All traffic encrypted via TLS.
- **Environment Variables**: Sensitive keys (API keys, DB passwords) stored in `.env` and never committed to git.
- **CORS**: Strict Cross-Origin Resource Sharing policy allowing only the official frontend domain.
