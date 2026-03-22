# CLAUDE.md — Project Guidelines

## Overview

This is a language learning app called LangMentor with a Next.js 16 frontend and a Python FastAPI backend.

## Quick Reference

See [AGENTS.md](./AGENTS.md) for full guidelines. Key commands:

```bash
# Frontend
npm run dev      # Start dev server
npm run build    # Production build
npm run lint     # Run ESLint (next/core-web-vitals + typescript)

# Backend
cd backend && uv run main.py   # Run backend
```

## Critical Rules

1. **Next.js 16 is NOT standard Next.js** — check `node_modules/next/dist/docs/` before writing any code. APIs may have changed.
2. **No test framework** — do not assume a test runner exists. Check AGENTS.md for updates.
3. **Strict TypeScript** — `tsconfig.json` uses `"strict": true`. Always provide explicit types.
4. **Path aliases** — use `@/*` for project imports, never `../../`.
5. **Styling** — use Tailwind CSS v4 and shadcn/ui (radix-nova). Add components via `npx shadcn@latest add <component>`.
6. **No comments** — do not add comments unless essential for non-obvious logic.
7. **Lint after changes** — always run `npm run lint` after TypeScript modifications.
8. **Commits** — do not commit unless explicitly asked.

## Architecture

```
app/          # Next.js App Router
components/   # React components (UI in components/ui/)
lib/          # Utilities (cn() in lib/utils.ts)
backend/      # Python/FastAPI (uv-managed, Python >= 3.13)
```

## Key Libraries

- Next.js 16.2.1 / React 19.2.4
- Tailwind CSS v4 + tw-animate-css
- shadcn/ui (radix-nova style) + lucide-react icons
- class-variance-authority for component variants
