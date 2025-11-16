from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import TeamCreate, TeamResponse, TeamJoin, UserInTeam
from ..services import TeamService
from ..security import get_current_active_user
from ..models import User, Team, team_members

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new team"""
    try:
        team = TeamService.create_team(db, team_data, current_user)

        # Add member count
        response = TeamResponse.from_orm(team)
        response.member_count = 1

        return response
    except Exception as e:
        # Rollback any partial changes
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create team: {str(e)}"
        )


@router.post("/join", response_model=TeamResponse)
async def join_team(
    join_data: TeamJoin,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a team using invite code"""
    try:
        team = TeamService.join_team(db, join_data.invite_code, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    response = TeamResponse.from_orm(team)
    response.member_count = len(team.members)

    return response


@router.get("/", response_model=List[TeamResponse])
async def get_my_teams(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all teams the current user is a member of, optionally filtered by status"""
    from ..models import ProjectStatus

    teams = TeamService.get_user_teams(db, current_user)

    # Filter by status if provided
    if status:
        try:
            status_enum = ProjectStatus(status.lower())
            teams = [team for team in teams if team.status == status_enum]
        except ValueError:
            # Invalid status, return empty list
            teams = []

    response = []
    for team in teams:
        team_resp = TeamResponse.from_orm(team)
        team_resp.member_count = len(team.members)
        response.append(team_resp)

    return response


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get team details"""
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

    response = TeamResponse.from_orm(team)
    response.member_count = len(team.members)

    return response


@router.get("/{team_id}/members", response_model=List[UserInTeam])
async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all members of a team"""
    # Check if user is a member
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    members_with_roles = TeamService.get_team_members(db, team_id)

    return [
        UserInTeam(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=role
        )
        for user, role in members_with_roles
    ]


@router.post("/{team_id}/freeze", status_code=status.HTTP_200_OK)
async def freeze_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Freeze a team (team creator only)"""
    # Get team
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Check if user is the team creator
    if team.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the team creator can freeze/archive teams"
        )

    try:
        TeamService.freeze_team(db, team_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    return {"message": "Team frozen successfully"}


@router.post("/{team_id}/unfreeze", status_code=status.HTTP_200_OK)
async def unfreeze_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfreeze a team (team creator only)"""
    # Get team
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Check if user is the team creator
    if team.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the team creator can unfreeze teams"
        )

    try:
        TeamService.unfreeze_team(db, team_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {"message": "Team unfrozen successfully"}
