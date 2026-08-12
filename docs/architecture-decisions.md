# Architecture Decisions

## 2026-08-12: Backend Uses AWS SAM

Decision:
Use AWS Serverless Application Model (SAM) to define and deploy the backend API infrastructure.

Context:
The project originally had AWS resources created outside a dedicated source-controlled backend structure. Moving to SAM gives the backend an infrastructure-as-code foundation.

Details:
- The backend stack lives in `template.yaml`.
- Deployment configuration lives in `samconfig.toml`.
- The dev stack deploys to `af-south-1`.
- The configured dev stack name is `mtg-stats-sam-dev`.

Why:
SAM keeps API Gateway, Lambda, DynamoDB, Cognito, and related permissions versioned together, making changes easier to review and reproduce.

## 2026-08-12: API Authentication Uses Cognito

Decision:
Use Amazon Cognito User Pools as the authentication provider for protected API endpoints.

Context:
The frontend is not being built yet, but the API needs a real authentication boundary that can later be used by a web or mobile client.

Details:
- Cognito resources are defined in `template.yaml`.
- API Gateway uses a Cognito authorizer.
- Cognito is configured as the default authorizer for the API.
- `/ping` is explicitly public with `Authorizer: NONE`.
- `/counter` requires authentication by default.
- Clients sign in with Cognito and send `Authorization: Bearer <IdToken>` when calling protected endpoints.

Why:
API Gateway can validate Cognito tokens before Lambda is invoked, so Lambda handlers do not need to duplicate JWT validation logic.

## 2026-08-12: Backend and Frontend Should Be Separate Repositories

Decision:
Keep the backend and frontend in separate Git repositories.

Context:
The local workspace currently contains both `API` and `FrontEnd` folders. The backend and frontend have different toolchains, deployment flows, and lifecycles.

Details:
- The backend repo root should be the folder containing `template.yaml`.
- The current backend root is the `mtg-stats-api` repo.
- The frontend should have its own repo and its own `AGENTS.md` if/when active development resumes there.

Why:
Separate repos keep deployment history, CI/CD, dependencies, and project instructions focused on the code they apply to.

## 2026-08-12: Backend Source of Truth Is `mtg-stats-api`

Decision:
Use the `mtg-stats-api` repository as the backend source of truth.

Context:
The previous local `API/mtg-stats-stack` folder was migrated into a dedicated GitHub-backed repository.

Details:
- Backend development should happen in `mtg-stats-api`.
- `template.yaml`, `samconfig.toml`, `src`, `docs`, and `AGENTS.md` live at the repo root.
- The old `API` folder is no longer needed after migration.

Why:
The dedicated backend repo keeps SAM infrastructure, Lambda code, and backend decisions versioned together in the right project boundary.

## 2026-08-12: Cognito `sub` Is the Internal User ID

Decision:
Use the Cognito `sub` claim as the stable internal user identifier.

Context:
The previous data model used human-readable player keys such as `p#carli`. Cognito users can sign in with email, and human-facing names may change over time.

Details:
- Lambda handlers read authenticated user claims from `event.requestContext.authorizer.claims`.
- The internal player key should be derived as `p#<sub>`.
- Human-facing names such as `carli` should be stored as profile data, not as primary identity.
- The `/me` endpoint returns the authenticated user's `sub`, derived `playerKey`, email, email verification state, and Cognito username.

Why:
The Cognito `sub` claim is stable and unique for a user in the user pool, making it safer for DynamoDB keys and relationships than email or display names.
