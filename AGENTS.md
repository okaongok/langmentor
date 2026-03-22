<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# LangMentor

A language learning app with a Next.js 16 frontend (React 19) and a Python/FastAPI backend.

## Build / Lint / Dev Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Next.js dev server |
| `npm run dev:backend` | Start Python backend |
| `npm run dev:all` | Start both frontend and backend |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint (next/core-web-vitals + typescript) |

There is **no test framework** configured yet. If you add tests, update this section.

### Python backend (`backend/`)

- Uses `uv` for dependency management. Python >= 3.13.
- Dev server: `npm run dev:backend` (uses `fastapi dev` with auto-reload)

## Project Structure

```
app/          # Next.js App Router pages and layouts
components/   # React components (reusable UI in components/ui/)
lib/          # Shared utilities (cn() helper lives in lib/utils.ts)
backend/      # Python FastAPI backend (uv-managed)
```

Path alias `@/*` maps to the project root (e.g., `@/components/ui/button`).

## Code Style — TypeScript / React

### Imports
- Use `import type { ... }` for type-only imports (e.g., `import type { Metadata } from "next"`).
- Use `import * as React from "react"` when referencing React namespace; otherwise import named exports.
- CSS/globals imports: plain `import "./globals.css"`.
- Use the `@/` path alias for project-internal imports, never relative `../../`.

### Components
- Default-export page/layout components (`export default function Home()`).
- Named-export reusable components and re-export from barrel files where appropriate.
- Use `function` declarations, not arrow functions, for components.
- Props: destructure inline with `React.ComponentProps<"element">` for intrinsic elements,
  combine with `VariantProps<typeof variants>` for variant-based components.

### Styling
- Tailwind CSS v4 with `@import "tailwindcss"` in globals.css.
- Use the `cn()` utility from `@/lib/utils` to merge class names (`clsx` + `tailwind-merge`).
- shadcn/ui (radix-nova style) — add components via `npx shadcn@latest add <component>`.
- Prefer Tailwind utility classes; use CSS variables from the theme (e.g., `bg-primary`, `text-muted-foreground`).
- Dark mode: `.dark` class on a parent element; use `dark:` variants.

### Naming
- Files: `kebab-case.tsx` / `ts` (e.g., `user-card.tsx`).
- Components: `PascalCase`.
- Functions / variables: `camelCase`.
- Constants (truly immutable): `UPPER_SNAKE_CASE`.
- Types / Interfaces: `PascalCase`.

### Types
- `tsconfig.json` has `"strict": true` — always use explicit types for function params and returns
  where the inference is not obvious.
- Prefer `interface` for object shapes, `type` for unions/intersections/utility types.
- Use `Readonly<{ ... }>` for component prop types that should not be mutated.

### Error Handling
- For async Server Components and Route Handlers, use try/catch and return appropriate
  `NextResponse.json({ error: "..." }, { status: ... })`.
- Client-side: surface errors via state, not raw `alert()`.

## Code Style — Python (backend/)

- Follow PEP 8; format with `ruff format` if available.
- Use type hints on all function signatures.
- FastAPI router pattern: define routes in a router module, include in `main.py`.

## General Rules

- Do NOT add comments unless the logic is non-obvious and the comment is essential.
- Run `npm run lint` after every TypeScript change — fix all warnings before considering the task done.
- Do not commit unless the user explicitly asks you to.
- When using shadcn/ui components, use `npx shadcn@latest add` rather than hand-writing them.
- Check `node_modules/next/dist/docs/` when unsure about Next.js 16 APIs.
