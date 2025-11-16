from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple
from fastapi import UploadFile
import aiofiles
import os
import uuid

from .models import User, Team, Contribution, Verification, Flag, UserRole, team_members, ProjectStatus
from .schemas import (
    UserCreate, TeamCreate, ContributionCreate, VerificationCreate, FlagCreate,
    ReputationBreakdown, UserReputation
)
from .security import get_password_hash, generate_invite_code, encrypt_file
from .utils import (
    generate_uuid, calculate_file_hash, get_storage_path,
    is_allowed_file_type, calculate_reputation_score, ensure_directory
)
from .blockchain import Blockchain # Import the Blockchain class
from .config import settings


class UserService:
    """Service for user operations"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()


class TeamService:
    """Service for team operations"""

    @staticmethod
    def create_team(db: Session, team_data: TeamCreate, creator: User) -> Team:
        """Create a new team"""
        try:
            invite_code = generate_invite_code()
            
            # Generate a unique blockchain database file path for the team
            blockchain_filename = f"team_blockchain_{uuid.uuid4().hex}.db"
            blockchain_dir = os.path.join(settings.BLOCKCHAIN_STORAGE_PATH, str(creator.id))
            ensure_directory(blockchain_dir) # Ensure the directory exists
            blockchain_db_path = os.path.join(blockchain_dir, blockchain_filename)

            db_team = Team(
                name=team_data.name,
                description=team_data.description,
                invite_code=invite_code,
                created_by=creator.id,
                blockchain_db_path=blockchain_db_path,
                status=ProjectStatus.ACTIVE # Ensure new teams are active
            )
            db.add(db_team)
            db.flush()

            # Initialize the new blockchain for the team
            try:
                team_blockchain = Blockchain(db_path=blockchain_db_path)
                team_blockchain.init_chain(team_id=db_team.id) # This will create the genesis block
            except Exception as e:
                # If blockchain initialization fails, rollback and re-raise
                db.rollback()
                raise ValueError(f"Failed to initialize blockchain: {str(e)}")

            # Add creator as instructor
            stmt = team_members.insert().values(
                team_id=db_team.id,
                user_id=creator.id,
                role=UserRole.INSTRUCTOR
            )
            db.execute(stmt)

            db.commit()
            db.refresh(db_team)
            return db_team
        except Exception as e:
            db.rollback()
            raise

    @staticmethod
    def join_team(db: Session, invite_code: str, user: User) -> Team:
        """Join a team using invite code"""
        team = db.query(Team).filter(Team.invite_code == invite_code).first()
        if not team:
            raise ValueError("Invalid invite code")

        # Check if already a member
        existing = db.query(team_members).filter(
            and_(
                team_members.c.team_id == team.id,
                team_members.c.user_id == user.id
            )
        ).first()

        if existing:
            raise ValueError("Already a member of this team")

        # Add as member
        stmt = team_members.insert().values(
            team_id=team.id,
            user_id=user.id,
            role=UserRole.MEMBER
        )
        db.execute(stmt)
        db.commit()

        return team

    @staticmethod
    def get_user_teams(db: Session, user: User) -> List[Team]:
        """Get all teams user is a member of"""
        return user.teams

    @staticmethod
    def get_team_members(db: Session, team_id: int) -> List[Tuple[User, UserRole]]:
        """Get all members of a team with their roles"""
        results = db.query(User, team_members.c.role).join(
            team_members, User.id == team_members.c.user_id
        ).filter(team_members.c.team_id == team_id).all()

        return [(user, role) for user, role in results]

    @staticmethod
    def get_user_role_in_team(db: Session, user_id: int, team_id: int) -> Optional[UserRole]:
        """Get user's role in a specific team"""
        result = db.query(team_members.c.role).filter(
            and_(
                team_members.c.user_id == user_id,
                team_members.c.team_id == team_id
            )
        ).first()

        return result[0] if result else None

    @staticmethod
    def freeze_team(db: Session, team_id: int):
        """Freeze a team (lock blockchain and prevent new contributions)"""
        from datetime import datetime
        from .models import ProjectStatus

        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        team.status = ProjectStatus.FROZEN
        team.frozen_at = datetime.utcnow()
        db.commit()

        if not team.blockchain_db_path:
            raise ValueError("Team blockchain not initialized")

        team_blockchain = Blockchain(db_path=team.blockchain_db_path)
        team_blockchain.freeze_chain()

    @staticmethod
    def unfreeze_team(db: Session, team_id: int):
        """Unfreeze a team (allow new contributions)"""
        from datetime import datetime
        from .models import ProjectStatus

        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")
        
        if team.status == ProjectStatus.ACTIVE:
            raise ValueError("Team is already active and not frozen")

        team.status = ProjectStatus.ACTIVE
        team.frozen_at = None  # Clear frozen_at timestamp
        db.commit()

        # Unfreeze blockchain
        if not team.blockchain_db_path:
            raise ValueError("Team blockchain not initialized")

        team_blockchain = Blockchain(db_path=team.blockchain_db_path)
        team_blockchain.unfreeze_chain()


class ContributionService:
    """Service for contribution operations"""

    @staticmethod
    async def create_contribution(
        db: Session,
        contribution_data: ContributionCreate,
        contributor: User,
        file: Optional[UploadFile] = None
    ) -> Contribution:
        """Create a new contribution"""
        
        team = db.query(Team).filter(Team.id == contribution_data.team_id).first()
        if not team:
            raise ValueError("Team not found.")

        if not team.blockchain_db_path:
            # Initialize blockchain for existing teams that don't have one
            blockchain_filename = f"team_blockchain_{uuid.uuid4().hex}.db"
            blockchain_dir = os.path.join(settings.BLOCKCHAIN_STORAGE_PATH, str(team.created_by))
            ensure_directory(blockchain_dir)
            blockchain_db_path = os.path.join(blockchain_dir, blockchain_filename)
            team.blockchain_db_path = blockchain_db_path
            db.commit()
            
            # Initialize the blockchain
            team_blockchain = Blockchain(db_path=blockchain_db_path)
            team_blockchain.init_chain(team_id=team.id)

        if team.status == ProjectStatus.FROZEN:
            raise ValueError("Team blockchain is frozen and cannot accept new contributions.")

        contribution_uuid = generate_uuid()
        file_path = None
        file_hash = None

        # Handle file upload if present
        if file:
            if not is_allowed_file_type(file.filename):
                raise ValueError(f"File type not allowed: {file.filename}")

            # Read file data
            file_data = await file.read()

            # Calculate hash
            file_hash = calculate_file_hash(file_data)

            # Encrypt and save
            encrypted_data = encrypt_file(file_data)
            file_path = get_storage_path(
                contribution_data.team_id,
                contribution_uuid,
                file.filename
            )

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(encrypted_data)

        # Create contribution record
        db_contribution = Contribution(
            uuid=contribution_uuid,
            title=contribution_data.title,
            description=contribution_data.description,
            contribution_type=contribution_data.contribution_type,
            external_link=contribution_data.external_link,
            self_assessed_impact=contribution_data.self_assessed_impact,
            file_path=file_path,
            file_hash=file_hash,
            team_id=contribution_data.team_id,
            contributor_id=contributor.id,
            reputation_score=1.0  # Initial score for submission
        )

        db.add(db_contribution)
        db.flush()

        # Add to blockchain
        team_blockchain = Blockchain(db_path=team.blockchain_db_path)
        block = team_blockchain.add_block(
            contribution_id=contribution_uuid,
            contributor_id=contributor.id,
            contribution_type=contribution_data.contribution_type.value,
            team_id=contribution_data.team_id,
            file_hash=file_hash,
            metadata={
                "title": contribution_data.title,
                "self_assessed_impact": contribution_data.self_assessed_impact,
                "has_file": file_path is not None,
                "has_link": contribution_data.external_link is not None
            }
        )

        # Update contribution with block info
        db_contribution.block_id = block.block_id
        db_contribution.block_hash = block.hash

        db.commit()
        db.refresh(db_contribution)

        return db_contribution

    @staticmethod
    def get_team_contributions(
        db: Session,
        team_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Contribution]:
        """Get all contributions for a team"""
        return db.query(Contribution).filter(
            Contribution.team_id == team_id
        ).order_by(Contribution.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_contributions(
        db: Session,
        user_id: int,
        team_id: Optional[int] = None
    ) -> List[Contribution]:
        """Get all contributions by a user"""
        query = db.query(Contribution).filter(Contribution.contributor_id == user_id)

        if team_id:
            query = query.filter(Contribution.team_id == team_id)

        return query.order_by(Contribution.created_at.desc()).all()


class VerificationService:
    """Service for verification operations"""

    @staticmethod
    def verify_contribution(
        db: Session,
        verification_data: VerificationCreate,
        verifier: User,
        team_id: int
    ) -> Verification:
        """Verify a contribution"""
        # Get contribution
        contribution = db.query(Contribution).filter(
            and_(
                Contribution.id == verification_data.contribution_id,
                Contribution.team_id == team_id
            )
        ).first()

        if not contribution:
            raise ValueError("Contribution not found")

        # Prevent self-verification
        if contribution.contributor_id == verifier.id:
            raise ValueError("Cannot verify your own contribution")

        # Check if already verified
        existing = db.query(Verification).filter(
            and_(
                Verification.contribution_id == contribution.id,
                Verification.verifier_id == verifier.id
            )
        ).first()

        if existing:
            raise ValueError("Already verified this contribution")

        # Get verifier's role
        verifier_role = TeamService.get_user_role_in_team(db, verifier.id, team_id)

        # Create verification
        db_verification = Verification(
            contribution_id=contribution.id,
            verifier_id=verifier.id,
            verifier_role=verifier_role,
            comment=verification_data.comment
        )

        db.add(db_verification)
        db.flush()

        # Recalculate reputation score
        ReputationService.update_contribution_score(db, contribution.id)

        db.commit()
        db.refresh(db_verification)
        
        # Eagerly load the verifier relationship
        db_verification.verifier  # This will trigger lazy loading if needed

        return db_verification


class FlagService:
    """Service for flagging operations"""

    @staticmethod
    def flag_contribution(
        db: Session,
        flag_data: FlagCreate,
        flagger: User,
        team_id: int
    ) -> Flag:
        """Flag a contribution as low-effort"""
        # Get contribution
        contribution = db.query(Contribution).filter(
            and_(
                Contribution.id == flag_data.contribution_id,
                Contribution.team_id == team_id
            )
        ).first()

        if not contribution:
            raise ValueError("Contribution not found")

        # Check if already flagged
        existing = db.query(Flag).filter(
            and_(
                Flag.contribution_id == contribution.id,
                Flag.flagger_id == flagger.id
            )
        ).first()

        if existing:
            raise ValueError("Already flagged this contribution")

        # Create flag
        db_flag = Flag(
            contribution_id=contribution.id,
            flagger_id=flagger.id,
            reason=flag_data.reason
        )

        db.add(db_flag)
        db.flush()

        # Recalculate reputation score
        ReputationService.update_contribution_score(db, contribution.id)

        db.commit()
        db.refresh(db_flag)

        return db_flag


class ReputationService:
    """Service for reputation calculations"""

    @staticmethod
    def update_contribution_score(db: Session, contribution_id: int):
        """Update reputation score for a contribution"""
        contribution = db.query(Contribution).filter(Contribution.id == contribution_id).first()

        if not contribution:
            return
        
        team = db.query(Team).filter(Team.id == contribution.team_id).first()
        if not team:
            raise ValueError("Team not found.")
        
        if not team.blockchain_db_path:
            # If team doesn't have blockchain, skip blockchain update
            return

        # Count verifications
        total_verifications = db.query(func.count(Verification.id)).filter(
            Verification.contribution_id == contribution_id
        ).scalar()

        # Count instructor/manager verifications
        instructor_verifications = db.query(func.count(Verification.id)).filter(
            and_(
                Verification.contribution_id == contribution_id,
                Verification.verifier_role.in_([UserRole.INSTRUCTOR, UserRole.MANAGER])
            )
        ).scalar()

        # Count flags
        flag_count = db.query(func.count(Flag.id)).filter(
            Flag.contribution_id == contribution_id
        ).scalar()

        # Calculate score
        verified_count = max(0, total_verifications - instructor_verifications)
        score = calculate_reputation_score(
            submitted_count=1,  # This contribution
            verified_count=verified_count if verified_count >= 2 else 0,
            instructor_verified_count=instructor_verifications,
            flagged_count=flag_count
        )

        # Update contribution
        contribution.reputation_score = score
        db.commit()

        # Update blockchain (non-critical - don't fail if this errors)
        try:
            if contribution.uuid:  # Only update if contribution has a UUID
                team_blockchain = Blockchain(db_path=team.blockchain_db_path)
                team_blockchain.update_block_verification(
                    contribution_id=contribution.uuid,
                    verification_count=total_verifications,
                    reputation_score=score
                )
        except Exception as e:
            # Log error but don't fail the verification
            # The reputation score has already been updated in the database
            import logging
            logging.warning(f"Failed to update blockchain for contribution {contribution_id}: {str(e)}")

    @staticmethod
    def get_user_reputation(db: Session, user_id: int, team_id: int) -> ReputationBreakdown:
        """Get reputation breakdown for a user in a team"""
        contributions = db.query(Contribution).filter(
            and_(
                Contribution.contributor_id == user_id,
                Contribution.team_id == team_id
            )
        ).all()

        total_contributions = len(contributions)
        verified_contributions = 0
        instructor_verified = 0
        flagged_contributions = 0
        total_score = 0.0

        for contrib in contributions:
            total_score += contrib.reputation_score

            # Count verifications
            verifications = db.query(Verification).filter(
                Verification.contribution_id == contrib.id
            ).all()

            if len(verifications) >= 2:
                verified_contributions += 1

            instructor_count = sum(
                1 for v in verifications
                if v.verifier_role in [UserRole.INSTRUCTOR, UserRole.MANAGER]
            )
            if instructor_count > 0:
                instructor_verified += 1

            # Count flags
            flag_count = db.query(func.count(Flag.id)).filter(
                Flag.contribution_id == contrib.id
            ).scalar()

            if flag_count >= 2:
                flagged_contributions += 1

        return ReputationBreakdown(
            total_contributions=total_contributions,
            verified_contributions=verified_contributions,
            instructor_verified=instructor_verified,
            flagged_contributions=flagged_contributions,
            total_score=total_score
        )

    @staticmethod
    def get_team_leaderboard(db: Session, team_id: int) -> List[UserReputation]:
        """Get leaderboard for a team"""
        members_with_roles = TeamService.get_team_members(db, team_id)

        leaderboard = []
        for user, role in members_with_roles:
            reputation = ReputationService.get_user_reputation(db, user.id, team_id)
            leaderboard.append(UserReputation(
                user={
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": role
                },
                reputation=reputation
            ))

        # Sort by total score
        leaderboard.sort(key=lambda x: x.reputation.total_score, reverse=True)

        return leaderboard
