# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

## Commands

```bash
npm run dev      # Start dev server (http://localhost:3000)
npm run build    # Production build
npm run start    # Start production server
npm run lint     # ESLint (flat config, eslint.config.mjs)
```

## Tech Stack

- **Next.js 16** (App Router) — breaking changes from earlier versions; consult `node_modules/next/dist/docs/` before writing code
- **React 19** with Server Components by default
- **Tailwind CSS v4** via `@tailwindcss/postcss` (no `tailwind.config.js`; configure in CSS)
- **TypeScript** (strict mode)

## Project Structure

```
src/app/              — Root layout + page (App Router)
src/app/(views)/      — Route groups (e.g., system/)
```

- Uses `@/*` path alias mapped to `./src/*`
- Route groups use parenthesized folders: `(views)` does not appear in URL
- Each route group can have its own `layout.tsx` and `globals.css`

## Key Conventions

- Fonts: Geist Sans + Geist Mono loaded via `next/font/google`, exposed as CSS variables
- Styling: Utility-first Tailwind; supports dark mode via `dark:` variant
- ESLint: Flat config with `eslint-config-next` (core-web-vitals + typescript presets)
