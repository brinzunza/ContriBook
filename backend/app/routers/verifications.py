from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import VerificationCreate, VerificationResponse, FlagCreate, FlagResponse, UserInTeam
from ..services import VerificationService, FlagService, TeamService
from ..security import get_current_active_user
from ..models import User, Contribution

router = APIRouter(prefix="/verifications", tags=["Verifications & Flags"])


@router.post("/verify", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def verify_contribution(
    verification_data: VerificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify a contribution"""
    # Get contribution to check team membership
    contribution = db.query(Contribution).filter(
        Contribution.id == verification_data.contribution_id
    ).first()

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

    try:
        verification = VerificationService.verify_contribution(
            db, verification_data, current_user, contribution.team_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Build response
    response = VerificationResponse.from_orm(verification)
    response.verifier = UserInTeam(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=role
    )

    return response


@router.post("/flag", response_model=FlagResponse, status_code=status.HTTP_201_CREATED)
async def flag_contribution(
    flag_data: FlagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Flag a contribution as low-effort"""
    # Get contribution to check team membership
    contribution = db.query(Contribution).filter(
        Contribution.id == flag_data.contribution_id
    ).first()

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

    try:
        flag = FlagService.flag_contribution(
            db, flag_data, current_user, contribution.team_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Build response
    response = FlagResponse.from_orm(flag)
    response.flagger = UserInTeam(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=role
    )

    return response


@router.get("/contribution/{contribution_id}/verifications", response_model=List[VerificationResponse])
async def get_contribution_verifications(
    contribution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all verifications for a contribution"""
    from ..models import Verification

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

    verifications = db.query(Verification).filter(
        Verification.contribution_id == contribution_id
    ).all()

    response = []
    for verification in verifications:
        verifier_role = TeamService.get_user_role_in_team(
            db, verification.verifier_id, contribution.team_id
        )

        verif_resp = VerificationResponse.from_orm(verification)
        verif_resp.verifier = UserInTeam(
            id=verification.verifier.id,
            username=verification.verifier.username,
            full_name=verification.verifier.full_name,
            role=verifier_role
        )
        response.append(verif_resp)

    return response
