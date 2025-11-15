# ContriBook - Quick Start Guide

Get ContriBook up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- OR: Python 3.11+, Node.js 18+, PostgreSQL

## Option 1: Docker (Fastest) ⚡

1. **Clone & Setup**
```bash
git clone <your-repo-url>
cd ContriBook
./setup.sh
```

2. **Start Everything**
```bash
docker-compose up -d
```

3. **Access the App**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

That's it! The app is running.

## Option 2: Manual Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env - add your SECRET_KEY and ENCRYPTION_KEY
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## First Steps in the App

### 1. Create Your Account
- Go to http://localhost:5173
- Click "Register"
- Fill in username, email, password
- Click "Register"

### 2. Create or Join a Team
**To create a team:**
- Click "Create Team" button
- Enter team name and description
- You'll get an invite code - share it with teammates!

**To join a team:**
- Click "Join Team" button
- Enter the invite code from your instructor
- You're now part of the team!

### 3. Submit Your First Contribution
- Click on your team
- Click "Submit Contribution"
- Choose type: Git, Document, Image, Meeting, Mental, or Other
- Add title and description
- (Optional) Upload a file or add a link
- Rate your impact (1-5)
- Submit!

### 4. Verify Teammates
- Browse the team feed
- Review contributions
- Click "Verify" on good contributions
- Earn reputation by contributing and getting verified!

### 5. Check the Leaderboard
- Click "Leaderboard" tab in your team
- See rankings based on reputation scores
- Track your progress!

## Understanding Reputation Scores

Your score is calculated as:
```
Score = (Verified by 2+ teammates × 3)
      + (Verified by instructor × 5)
      + (Submitted × 1)
      + (Flagged × -2)
```

**Tips to boost your score:**
- Submit quality contributions regularly
- Get your work verified by teammates
- Seek instructor/manager verification
- Avoid submitting low-effort content

## Contribution Types Explained

- **Git**: Link to GitHub/GitLab commits
- **Document**: Google Docs, written reports
- **Image**: Handwritten notes, diagrams (upload photos)
- **Meeting**: Meeting notes, transcripts
- **Mental**: Ideas, planning, strategy discussions
- **Other**: Anything else that doesn't fit above

## For Instructors/Team Leads

### Managing Your Team
- You're automatically an "instructor" when you create a team
- Share the invite code with your team members
- Your verifications carry extra weight (+5 points)

### End of Project
1. Click "Freeze Team" to lock contributions
2. Export team data (includes blockchain + all files)
3. Team members can download individual reports

## Troubleshooting

### Can't connect to backend?
- Make sure backend is running on port 8000
- Check `VITE_API_URL` in frontend/.env

### Database errors?
- Ensure PostgreSQL is running
- Check DATABASE_URL in backend/.env

### Login not working?
- Clear browser storage
- Check SECRET_KEY is set in backend/.env

### File upload fails?
- Check file size (max 50MB by default)
- Verify allowed file types in backend/.env

## Common Commands

### Docker
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend
```

### Backend
```bash
# Run server
uvicorn app.main:app --reload

# Run tests
pytest
```

### Frontend
```bash
# Dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables Explained

### Backend (.env)
- `SECRET_KEY`: JWT signing key (generate randomly)
- `ENCRYPTION_KEY`: File encryption key (use Fernet.generate_key())
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: True for development, False for production

### Frontend (.env)
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000/api)

## Generate Keys

```bash
# SECRET_KEY (JWT)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Need Help?

- Check the full README.md for detailed documentation
- View API docs at http://localhost:8000/docs
- Open an issue on GitHub

## Next Steps

1. Invite your team members
2. Set contribution guidelines
3. Start tracking work!
4. Review and verify regularly
5. Export data at project end

Happy contributing! 🚀
