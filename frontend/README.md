# Layerpath Sales Agent Frontend

Next.js 14 frontend with TypeScript and Tailwind CSS.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
npm start
```

## Components

- `Chat.tsx` - Main chat interface
- `MessageBubble.tsx` - Message display component
- `AssetPanel.tsx` - Modal panel for displaying assets (video, GIF, pricing)

## Features

- Real-time chat interface
- Session management
- Asset display (video, GIF, pricing cards)
- Responsive design
- Dark mode support

