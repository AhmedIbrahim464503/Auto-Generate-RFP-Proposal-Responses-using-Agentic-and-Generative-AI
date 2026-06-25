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

## Phase 3 Ingestion UI Modules
- Implemented `src/components/UploadCenter.tsx`: Drag-and-drop workspace panel performing client-side validation checks (e.g. extension, max size) and tracking progress indicators.
- Implemented `src/components/DocumentLibrary.tsx`: Document listing grid providing real-time queries for extracted structural intelligence metadata (pages, author, format).
- Updated landing page routing `src/app/page.tsx` as a dashboard container displaying upload widgets.
