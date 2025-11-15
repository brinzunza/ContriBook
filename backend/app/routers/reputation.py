from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import TeamLeaderboard, UserReputation, UserInTeam
from ..services import ReputationService, TeamService
from ..security import get_current_active_user
from ..models import User

router = APIRouter(prefix="/reputation", tags=["Reputation"])


@router.get("/team/{team_id}/leaderboard", response_model=TeamLeaderboard)
async def get_team_leaderboard(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get leaderboard for a team"""
    from ..models import Team

    # Check if user is a member of the team
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

    rankings = ReputationService.get_team_leaderboard(db, team_id)

    return TeamLeaderboard(
        team_id=team_id,
        team_name=team.name,
        rankings=rankings
    )


@router.get("/my/{team_id}")
async def get_my_reputation(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's reputation in a team"""
    # Check if user is a member of the team
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    reputation = ReputationService.get_user_reputation(db, current_user.id, team_id)

    return UserReputation(
        user=UserInTeam(
            id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name,
            role=role
        ),
        reputation=reputation
    )
