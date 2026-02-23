# AI Copywriter - Copy.ai Alternative

Free AI-powered copywriting tool. Generate marketing copy, ad text, product descriptions, email subject lines, and social media posts instantly.

🌐 **Live Demo**: https://ai-copywriter.demo.densematrix.ai

## Features

- 📣 **Marketing Copy** - Headlines, taglines, marketing messages
- 🛍️ **Product Descriptions** - E-commerce product descriptions
- 📱 **Ad Copy** - Facebook, Google, LinkedIn ads
- 📧 **Email Subject Lines** - High-converting email subjects
- 📲 **Social Media** - Instagram, Twitter, LinkedIn posts
- 📝 **Blog Intros** - Engaging blog introductions

## Tech Stack

- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI
- **AI**: LLM Proxy (GPT-4o-mini)
- **Payment**: Creem MoR
- **Deploy**: Docker + Nginx

## Development

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker

### Setup

```bash
# Clone
git clone https://github.com/densematrix-labs/ai-copywriter.git
cd ai-copywriter

# Backend
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your keys
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
pytest --cov=app

# Frontend tests
cd frontend
npm run test
```

### Docker

```bash
docker-compose up -d
```

## Pricing

| Pack | Generations | Price |
|------|-------------|-------|
| Starter | 10 | $4.99 |
| Pro | 50 | $14.99 |
| Business | 200 | $39.99 |

## License

Proprietary - DenseMatrix
