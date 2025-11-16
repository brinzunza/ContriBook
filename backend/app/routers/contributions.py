from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import ContributionCreate, ContributionResponse, UserInTeam
from ..services import ContributionService, TeamService
from ..security import get_current_active_user
from ..models import User, ContributionType, Contribution, Team

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
    contributor_data = UserInTeam(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=role
    )

    response = ContributionResponse(
        id=contribution.id,
        uuid=contribution.uuid,
        title=contribution.title,
        description=contribution.description,
        contribution_type=contribution.contribution_type,
        external_link=contribution.external_link,
        self_assessed_impact=contribution.self_assessed_impact,
        file_path=contribution.file_path,
        file_hash=contribution.file_hash,
        reputation_score=contribution.reputation_score,
        block_id=contribution.block_id,
        block_hash=contribution.block_hash,
        team_id=contribution.team_id,
        contributor_id=contribution.contributor_id,
        contributor=contributor_data,
        verification_count=0,
        flag_count=0,
        verified_by_current_user=False,
        flagged_by_current_user=False,
        created_at=contribution.created_at,
        updated_at=contribution.updated_at
    )

    return response


@router.get("/team/{team_id}", response_model=List[ContributionResponse])
async def get_team_contributions(
    team_id: int,
    skip: int = 0,
    limit: int = 50,
    contributor_id: Optional[int] = None,
    contribution_type: Optional[ContributionType] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all contributions for a team with filtering, sorting, and search"""
    from ..models import Verification, Flag

    # Check if user is a member
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    contributions = ContributionService.get_team_contributions(
        db, team_id, skip, limit, contributor_id, contribution_type, search, sort_by, sort_order
    )

    response = []
    for contrib in contributions:
        # Get contributor info and role
        contributor_role = TeamService.get_user_role_in_team(db, contrib.contributor_id, team_id)

        contributor_data = UserInTeam(
            id=contrib.contributor.id,
            username=contrib.contributor.username,
            full_name=contrib.contributor.full_name,
            role=contributor_role
        )

        # Count verifications and flags
        verification_count = len(contrib.verifications)
        flag_count = len(contrib.flags)

        # Check if current user verified/flagged
        verified_by_current_user = any(
            v.verifier_id == current_user.id for v in contrib.verifications
        )
        flagged_by_current_user = any(
            f.flagger_id == current_user.id for f in contrib.flags
        )

        contrib_resp = ContributionResponse(
            id=contrib.id,
            uuid=contrib.uuid,
            title=contrib.title,
            description=contrib.description,
            contribution_type=contrib.contribution_type,
            external_link=contrib.external_link,
            self_assessed_impact=contrib.self_assessed_impact,
            file_path=contrib.file_path,
            file_hash=contrib.file_hash,
            reputation_score=contrib.reputation_score,
            block_id=contrib.block_id,
            block_hash=contrib.block_hash,
            team_id=contrib.team_id,
            contributor_id=contrib.contributor_id,
            contributor=contributor_data,
            verification_count=verification_count,
            flag_count=flag_count,
            verified_by_current_user=verified_by_current_user,
            flagged_by_current_user=flagged_by_current_user,
            created_at=contrib.created_at,
            updated_at=contrib.updated_at
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

        contributor_data = UserInTeam(
            id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name,
            role=role
        )

        contrib_resp = ContributionResponse(
            id=contrib.id,
            uuid=contrib.uuid,
            title=contrib.title,
            description=contrib.description,
            contribution_type=contrib.contribution_type,
            external_link=contrib.external_link,
            self_assessed_impact=contrib.self_assessed_impact,
            file_path=contrib.file_path,
            file_hash=contrib.file_hash,
            reputation_score=contrib.reputation_score,
            block_id=contrib.block_id,
            block_hash=contrib.block_hash,
            team_id=contrib.team_id,
            contributor_id=contrib.contributor_id,
            contributor=contributor_data,
            verification_count=len(contrib.verifications),
            flag_count=len(contrib.flags),
            verified_by_current_user=False,  # Own contribution
            flagged_by_current_user=False,
            created_at=contrib.created_at,
            updated_at=contrib.updated_at
        )

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

    contributor_data = UserInTeam(
        id=contribution.contributor.id,
        username=contribution.contributor.username,
        full_name=contribution.contributor.full_name,
        role=contributor_role
    )

    response = ContributionResponse(
        id=contribution.id,
        uuid=contribution.uuid,
        title=contribution.title,
        description=contribution.description,
        contribution_type=contribution.contribution_type,
        external_link=contribution.external_link,
        self_assessed_impact=contribution.self_assessed_impact,
        file_path=contribution.file_path,
        file_hash=contribution.file_hash,
        reputation_score=contribution.reputation_score,
        block_id=contribution.block_id,
        block_hash=contribution.block_hash,
        team_id=contribution.team_id,
        contributor_id=contribution.contributor_id,
        contributor=contributor_data,
        verification_count=len(contribution.verifications),
        flag_count=len(contribution.flags),
        verified_by_current_user=any(
            v.verifier_id == current_user.id for v in contribution.verifications
        ),
        flagged_by_current_user=any(
            f.flagger_id == current_user.id for f in contribution.flags
        ),
        created_at=contribution.created_at,
        updated_at=contribution.updated_at
    )

    return response
