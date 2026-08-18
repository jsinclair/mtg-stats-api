# Project Instructions

This repository contains the MTG Stats backend API.

## Context Loading

- Before making backend architecture changes, read `docs/architecture-decisions.md`.
- Before changing deployment, authentication, or AWS resource structure, read `template.yaml` and `samconfig.toml`.
- Treat `README.md` as the developer-facing runbook for common backend tasks.

## Decision Logging

- When a durable technical decision is made, update `docs/architecture-decisions.md`.
- Keep decisions concise, dated, and focused on the choice, context, and reason.
- Prefer adding a new dated entry over rewriting history unless correcting an error.

## Repo Boundaries

- This repo is for the backend only: AWS SAM, API Gateway, Lambda, DynamoDB, Cognito, and backend docs.
- Do not add frontend application code here.
- The frontend should live in its own repo with its own instructions and decisions.

## Current Architecture

- AWS SAM manages backend infrastructure.
- API Gateway fronts Lambda functions.
- Cognito User Pools provide API authentication.
- Cognito is the default API authorizer.
- `/ping` is public.
- `/counter` requires authentication.
- `/me` returns authenticated Cognito identity claims.
- `/me/profile` reads and updates the authenticated user's app profile in DynamoDB.
