# 17. Frontend Architecture

## Stack
- Framework: Next.js (App Router)
- Language: TypeScript
- State Management: React Context / Zustand
- Styling: Tailwind CSS or Custom CSS

## Folder Structure
- `/src/app`: Page routing and layouts.
- `/src/components`: Reusable UI elements.
- `/src/hooks`: Custom React hooks.
- `/src/services`: API clients.

## Phase 1 Bootstrap Status
- Setup Next.js 15 App router structure.
- Configured custom TSConfig path mapping (`@/*` pointing to `./src/*`).
- Defined Zustand state store (`src/store/useStore.ts`) for human approval gate states.
- Created `src/services/api.ts` API Fetch client with health endpoints connectivity template.
- Integrated HSL dark/light variable systems inside `globals.css` and customized display fonts in `tailwind.config.ts`.
