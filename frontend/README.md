# Frontend

Next.js (App Router, TypeScript, Tailwind CSS) frontend for the fashion e-commerce platform.

See the [root README](../README.md) for full setup instructions.

## Structure

- `app/` — routes, layouts, pages
- `components/` — shared UI components
- `lib/` — helpers such as the API client (`lib/api.ts`)
- `types/` — shared TypeScript types
- `styles/` — global CSS (`styles/globals.css`, imported by `app/layout.tsx`)

## Environment

- `NEXT_PUBLIC_API_URL` — base URL of the backend API (see `.env.example`)

## Development

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Scripts

- `npm run dev` — start the development server
- `npm run build` — build for production
- `npm start` — run the production build
- `npm run lint` — run ESLint
