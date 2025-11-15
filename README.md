# ContriBook

**Blockchain-Verified Academic & Professional Contribution Tracking**

ContriBook is a lightweight, private, transparent system where every team member's work is logged, verified, and visible to the group — without exposing data publicly.

## Features

- **Contribution Tracking**: Submit various types of contributions (Git commits, documents, meeting notes, etc.)
- **Blockchain Verification**: Immutable ledger using simplified blockchain for tamper-proof logs
- **Peer Verification**: Team members can verify each other's contributions
- **Reputation System**: Automatic scoring based on verified contributions and instructor approvals
- **Team Privacy**: All data is private to team members only
- **Encrypted Storage**: Files are encrypted at rest
- **Export & Archive**: End-of-project archival and individual PDF reports

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (metadata), SQLite (blockchain simulation)
- **Storage**: Local encrypted filesystem
- **Security**: JWT authentication, Fernet encryption

### Frontend
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OR: Python 3.11+, Node.js 20+, PostgreSQL

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ContriBook.git
cd ContriBook
```

2. Generate encryption keys:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your SECRET_KEY and ENCRYPTION_KEY
```

4. Start services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add to .env as ENCRYPTION_KEY
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Set VITE_API_URL if needed
```

3. Run development server:
```bash
npm run dev
```

## Usage

### 1. Register & Login
- Create an account at `/register`
- Login at `/login`

### 2. Create or Join a Team
- **Create Team**: Click "Create Team" from dashboard
- **Join Team**: Use invite code provided by your instructor/team lead

### 3. Submit Contributions
- Navigate to your team
- Click "Submit Contribution"
- Fill in details, upload files, or add links
- Self-assess impact (1-5 scale)

### 4. Verify Contributions
- Browse team feed
- Review teammates' contributions
- Click "Verify" to endorse their work

### 5. View Reputation
- Check leaderboard to see team rankings
- View your individual reputation breakdown
- Export your contribution report

### 6. Archive Project (Instructors Only)
- Freeze the team when project ends
- Export team data including blockchain and encrypted files
- Members can download individual contribution reports

## Reputation Scoring Algorithm

```
Total Score = (Verified by 2+ teammates × 3)
            + (Verified by instructor/manager × 5)
            + (Submitted contributions × 1)
            + (Flagged contributions × -2)
```

## API Documentation

Visit `/docs` when the backend is running for interactive API documentation.

### Key Endpoints

- **Auth**: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- **Teams**: `/api/teams/`, `/api/teams/join`
- **Contributions**: `/api/contributions/`, `/api/contributions/team/{id}`
- **Verification**: `/api/verifications/verify`, `/api/verifications/flag`
- **Reputation**: `/api/reputation/team/{id}/leaderboard`
- **Blockchain**: `/api/blockchain/chain`, `/api/blockchain/verify`
- **Archive**: `/api/archive/teams/{id}/export`

## Project Structure

```
ContriBook/
├── backend/
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── services.py     # Business logic
│   │   ├── blockchain.py   # Blockchain implementation
│   │   ├── security.py     # Auth & encryption
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/          # React pages
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   ├── lib/            # API client
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for password storage
- **File Encryption**: Fernet symmetric encryption for uploaded files
- **Blockchain Integrity**: SHA-256 hashing and chain validation
- **Private Teams**: Row-level security on all queries
- **CORS Protection**: Configured allowed origins

## Development

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Build
```bash
cd frontend
npm run build
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Production Deployment

1. **Generate strong keys**:
   - Use a cryptographically secure SECRET_KEY (32+ characters)
   - Generate ENCRYPTION_KEY using Fernet

2. **Set DEBUG=False** in production

3. **Use production database**: Update DATABASE_URL

4. **Configure CORS**: Set proper CORS_ORIGINS

5. **SSL/TLS**: Use HTTPS in production

6. **Backup**: Regular backups of PostgreSQL and blockchain.db

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.

## Acknowledgments

Built for academic and professional teams to track contributions transparently and fairly.
