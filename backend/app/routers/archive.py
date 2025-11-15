from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import zipfile
import os
import json
from datetime import datetime

from ..database import get_db
from ..services import TeamService
from ..security import get_current_active_user
from ..models import User, Team, UserRole, ProjectStatus
from ..config import settings
from ..utils import ensure_directory
from ..blockchain import blockchain

router = APIRouter(prefix="/archive", tags=["Archive"])


@router.post("/teams/{team_id}/export")
async def export_team_data(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export team data and contributions (instructor/manager only)"""
    # Check if user is instructor/manager
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if role not in [UserRole.INSTRUCTOR, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors/managers can export team data"
        )

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Create archive directory
    archive_dir = os.path.join(settings.ARCHIVE_PATH, f"team_{team_id}")
    ensure_directory(archive_dir)

    archive_filename = f"team_{team_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
    archive_path = os.path.join(settings.ARCHIVE_PATH, archive_filename)

    # Create ZIP file
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Export team metadata
        team_data = {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "status": team.status.value,
            "created_at": team.created_at.isoformat(),
            "frozen_at": team.frozen_at.isoformat() if team.frozen_at else None,
            "exported_at": datetime.utcnow().isoformat()
        }
        zipf.writestr("team_info.json", json.dumps(team_data, indent=2))

        # Export blockchain data
        chain_data = blockchain.get_chain(team_id, limit=10000)
        zipf.writestr("blockchain.json", json.dumps(chain_data, indent=2))

        # Export contributions metadata
        from ..models import Contribution
        contributions = db.query(Contribution).filter(
            Contribution.team_id == team_id
        ).all()

        contributions_data = []
        for contrib in contributions:
            contributions_data.append({
                "id": contrib.id,
                "uuid": contrib.uuid,
                "title": contrib.title,
                "description": contrib.description,
                "type": contrib.contribution_type.value,
                "contributor_id": contrib.contributor_id,
                "contributor_username": contrib.contributor.username,
                "file_hash": contrib.file_hash,
                "external_link": contrib.external_link,
                "reputation_score": contrib.reputation_score,
                "created_at": contrib.created_at.isoformat()
            })

        zipf.writestr("contributions.json", json.dumps(contributions_data, indent=2))

        # Copy encrypted files
        storage_dir = os.path.join(settings.ENCRYPTED_STORAGE_PATH, f"team_{team_id}")
        if os.path.exists(storage_dir):
            for root, dirs, files in os.walk(storage_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join("files", file)
                    zipf.write(file_path, arcname)

    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=archive_filename
    )


@router.get("/teams/{team_id}/my-report")
async def get_my_contribution_report(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get individual contribution report for a user in a team"""
    from ..models import Contribution
    from ..services import ReputationService

    # Check if user is a member
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Get user's contributions
    contributions = db.query(Contribution).filter(
        Contribution.team_id == team_id,
        Contribution.contributor_id == current_user.id
    ).all()

    # Get reputation
    reputation = ReputationService.get_user_reputation(db, current_user.id, team_id)

    # Create report
    report = {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "email": current_user.email
        },
        "team": {
            "id": team.id,
            "name": team.name
        },
        "reputation": {
            "total_score": reputation.total_score,
            "total_contributions": reputation.total_contributions,
            "verified_contributions": reputation.verified_contributions,
            "instructor_verified": reputation.instructor_verified,
            "flagged_contributions": reputation.flagged_contributions
        },
        "contributions": [
            {
                "title": c.title,
                "type": c.contribution_type.value,
                "description": c.description,
                "score": c.reputation_score,
                "verification_count": len(c.verifications),
                "created_at": c.created_at.isoformat()
            }
            for c in contributions
        ],
        "generated_at": datetime.utcnow().isoformat()
    }

    return report
