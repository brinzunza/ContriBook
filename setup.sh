#!/bin/bash

echo "ContriBook Setup Script"
echo "======================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo ".env file already exists. Skipping setup."
else
    echo "Creating .env file..."
    cp .env.example .env

    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    # Generate ENCRYPTION_KEY
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

    # Update .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
        sed -i '' "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|g" .env
    else
        # Linux
        sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
        sed -i "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|g" .env
    fi

    echo "Generated SECRET_KEY and ENCRYPTION_KEY"
fi

# Copy backend .env
if [ ! -f backend/.env ]; then
    echo "Creating backend/.env..."
    cp backend/.env.example backend/.env

    # Get keys from root .env
    SECRET_KEY=$(grep SECRET_KEY= .env | cut -d'=' -f2)
    ENCRYPTION_KEY=$(grep ENCRYPTION_KEY= .env | cut -d'=' -f2)

    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" backend/.env
        sed -i '' "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|g" backend/.env
    else
        sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" backend/.env
        sed -i "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|g" backend/.env
    fi
fi

# Copy frontend .env
if [ ! -f frontend/.env ]; then
    echo "Creating frontend/.env..."
    cp frontend/.env.example frontend/.env
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review .env files and adjust if needed"
echo "2. Run 'docker-compose up -d' to start the application"
echo "3. Access the app at http://localhost:5173"
echo ""
