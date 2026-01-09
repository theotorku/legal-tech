# Contract Analyzer Frontend

Modern, responsive web application for the Contract Analyzer API built with Next.js 16, TypeScript, and Tailwind CSS.

## Features

- 🔐 **Authentication** - Secure login and registration with JWT tokens
- 💳 **Subscription Management** - Plan selection, upgrades, and billing
- 📄 **Contract Analysis** - Upload and analyze contracts with AI
- 📊 **Usage Dashboard** - Real-time usage statistics and limits
- 🔑 **API Key Management** - Generate and manage API keys
- 🎨 **Modern UI** - Beautiful, responsive design with Tailwind CSS
- ⚡ **Fast** - Built with Next.js 16 App Router for optimal performance

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod
- **Payments**: Stripe Elements

## Getting Started

### Prerequisites

- Node.js 20+ and npm
- Backend API running (see main README)

### Installation

1. **Install dependencies**

```bash
npm install
```

2. **Configure environment variables**

Create `.env.local` file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

3. **Run development server**

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── dashboard/           # Protected dashboard pages
│   │   ├── analyze/        # Contract analysis page
│   │   ├── subscription/   # Subscription management
│   │   ├── api-keys/       # API key management
│   │   ├── layout.tsx      # Dashboard layout
│   │   └── page.tsx        # Dashboard home
│   ├── login/              # Login page
│   ├── register/           # Registration page
│   ├── pricing/            # Pricing page
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Landing page
├── lib/                     # Utilities and configurations
│   ├── api-client.ts       # API client with Axios
│   ├── types.ts            # TypeScript types
│   └── store.ts            # Zustand state management
├── public/                  # Static assets
└── package.json

```

## Available Scripts

```bash
# Development
npm run dev          # Start development server

# Production
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
```

## Key Pages

### Public Pages

- **/** - Landing page with features and pricing
- **/login** - User login
- **/register** - User registration
- **/pricing** - Pricing plans

### Protected Pages (Dashboard)

- **/dashboard** - Overview with usage stats
- **/dashboard/analyze** - Upload and analyze contracts
- **/dashboard/subscription** - Manage subscription
- **/dashboard/api-keys** - API key management
- **/dashboard/settings** - User settings

## API Integration

The frontend communicates with the backend API using Axios. All API calls are centralized in `lib/api-client.ts`.

### Authentication

JWT tokens are stored in localStorage and automatically included in API requests via Axios interceptors.

### Example API Call

```typescript
import { contractAPI } from "@/lib/api-client";

// Analyze a contract
const result = await contractAPI.analyze(file);
```

## State Management

Global state is managed with Zustand:

- **Auth Store** - User authentication state
- **Subscription Store** - Subscription and usage data
- **UI Store** - UI state (sidebar, modals, etc.)

### Example Usage

```typescript
import { useAuthStore } from "@/lib/store";

const { user, isAuthenticated, logout } = useAuthStore();
```

## Styling

Tailwind CSS 4 is used for styling with a custom configuration.

### Color Palette

- **Primary**: Blue (600)
- **Success**: Green (600)
- **Warning**: Yellow (600)
- **Error**: Red (600)

## Environment Variables

| Variable                             | Description            | Required |
| ------------------------------------ | ---------------------- | -------- |
| `NEXT_PUBLIC_API_URL`                | Backend API URL        | Yes      |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | No       |

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Docker

```bash
# Build
docker build -t contract-analyzer-frontend .

# Run
docker run -p 3000:3000 contract-analyzer-frontend
```

### Manual

```bash
# Build
npm run build

# Start
npm run start
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

Proprietary - All rights reserved

## Support

For issues or questions, contact support or check the main project documentation.
