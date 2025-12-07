# DocWiz Frontend

Next.js frontend for the DocWiz surgical visualization and cost estimation platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env.local
```

3. Start the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Development

### Code Formatting
```bash
npm run format
npm run format:check
```

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npm run type-check
```

### Testing
```bash
npm run test
npm run test:coverage
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   ├── lib/                 # Utility functions
│   ├── hooks/               # Custom React hooks
│   ├── store/               # Zustand stores
│   ├── types/               # TypeScript types
│   └── styles/              # Global styles
├── public/                  # Static assets
└── package.json             # npm configuration
```

## Design System

DocWiz follows a "surgically effective" design philosophy:
- Clean, minimalist interfaces
- Surgical blue color palette
- Precise, purposeful layouts
- WCAG AAA accessibility compliance
