from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import ContributionCreate, ContributionResponse, UserInTeam
from ..services import ContributionService, TeamService
from ..security import get_current_active_user
from ..models import User, ContributionType, Contribution

router = APIRouter(prefix="/contributions", tags=["Contributions"])


@router.post("/", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    contribution_type: ContributionType = Form(...),
    team_id: int = Form(...),
    external_link: Optional[str] = Form(None),
    self_assessed_impact: int = Form(3),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new contribution"""
    # Check if user is a member of the team
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    # Create contribution data
    contribution_data = ContributionCreate(
        title=title,
        description=description,
        contribution_type=contribution_type,
        team_id=team_id,
        external_link=external_link,
        self_assessed_impact=self_assessed_impact
    )

    try:
        contribution = await ContributionService.create_contribution(
            db, contribution_data, current_user, file
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Build response with contributor info
    response = ContributionResponse.from_orm(contribution)
    response.contributor = UserInTeam(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=role
    )
    response.verification_count = 0
    response.flag_count = 0
    response.verified_by_current_user = False
    response.flagged_by_current_user = False

    return response


@router.get("/team/{team_id}", response_model=List[ContributionResponse])
async def get_team_contributions(
    team_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all contributions for a team"""
    from ..models import Verification, Flag

    # Check if user is a member
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    contributions = ContributionService.get_team_contributions(db, team_id, skip, limit)

    response = []
    for contrib in contributions:
        # Get contributor info and role
        contributor_role = TeamService.get_user_role_in_team(db, contrib.contributor_id, team_id)

        contrib_resp = ContributionResponse.from_orm(contrib)
        contrib_resp.contributor = UserInTeam(
            id=contrib.contributor.id,
            username=contrib.contributor.username,
            full_name=contrib.contributor.full_name,
            role=contributor_role
        )

        # Count verifications and flags
        contrib_resp.verification_count = len(contrib.verifications)
        contrib_resp.flag_count = len(contrib.flags)

        # Check if current user verified/flagged
        contrib_resp.verified_by_current_user = any(
            v.verifier_id == current_user.id for v in contrib.verifications
        )
        contrib_resp.flagged_by_current_user = any(
            f.flagger_id == current_user.id for f in contrib.flags
        )

        response.append(contrib_resp)

    return response


@router.get("/my", response_model=List[ContributionResponse])
async def get_my_contributions(
    team_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's contributions"""
    contributions = ContributionService.get_user_contributions(
        db, current_user.id, team_id
    )

    response = []
    for contrib in contributions:
        # Get role in team
        role = TeamService.get_user_role_in_team(db, current_user.id, contrib.team_id)

        contrib_resp = ContributionResponse.from_orm(contrib)
        contrib_resp.contributor = UserInTeam(
            id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name,
            role=role
        )

        contrib_resp.verification_count = len(contrib.verifications)
        contrib_resp.flag_count = len(contrib.flags)
        contrib_resp.verified_by_current_user = False  # Own contribution
        contrib_resp.flagged_by_current_user = False

        response.append(contrib_resp)

    return response


@router.get("/{contribution_id}", response_model=ContributionResponse)
async def get_contribution(
    contribution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific contribution"""
    contribution = db.query(Contribution).filter(Contribution.id == contribution_id).first()

    if not contribution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contribution not found"
        )

    # Check if user is a member of the team
    role = TeamService.get_user_role_in_team(db, current_user.id, contribution.team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    # Get contributor role
    contributor_role = TeamService.get_user_role_in_team(
        db, contribution.contributor_id, contribution.team_id
    )

    response = ContributionResponse.from_orm(contribution)
    response.contributor = UserInTeam(
        id=contribution.contributor.id,
        username=contribution.contributor.username,
        full_name=contribution.contributor.full_name,
        role=contributor_role
    )

    response.verification_count = len(contribution.verifications)
    response.flag_count = len(contribution.flags)
    response.verified_by_current_user = any(
        v.verifier_id == current_user.id for v in contribution.verifications
    )
    response.flagged_by_current_user = any(
        f.flagger_id == current_user.id for f in contribution.flags
    )

    return response
