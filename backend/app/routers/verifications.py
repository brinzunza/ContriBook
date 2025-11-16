from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db
from ..schemas import VerificationCreate, VerificationResponse, FlagCreate, FlagResponse, UserInTeam
from ..services import VerificationService, FlagService, TeamService
from ..security import get_current_active_user
from ..models import User, Contribution, Verification, Flag

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
        
        # Reload verification with relationships to ensure verifier is loaded
        verification = db.query(Verification).options(
            joinedload(Verification.verifier)
        ).filter(Verification.id == verification.id).first()
        
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve verification after creation"
            )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the full error for debugging
        import logging
        logging.error(f"Error verifying contribution: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify contribution: {str(e)}"
        )

    # Build response - get verifier info from the relationship
    try:
        verifier_user = verification.verifier
        verifier_info = UserInTeam(
            id=verifier_user.id,
            username=verifier_user.username,
            full_name=verifier_user.full_name,
            role=role
        )
        
        # Create response with all data
        response = VerificationResponse(
            id=verification.id,
            contribution_id=verification.contribution_id,
            verifier_id=verification.verifier_id,
            verifier=verifier_info,
            verifier_role=verification.verifier_role,
            comment=verification.comment,
            created_at=verification.created_at
        )

        return response
    except Exception as e:
        # If response building fails, log but still return success
        # The verification was already saved to the database
        import logging
        logging.error(f"Error building verification response: {str(e)}", exc_info=True)
        # Return a minimal response
        return VerificationResponse(
            id=verification.id,
            contribution_id=verification.contribution_id,
            verifier_id=verification.verifier_id,
            verifier=UserInTeam(
                id=current_user.id,
                username=current_user.username,
                full_name=current_user.full_name,
                role=role
            ),
            verifier_role=verification.verifier_role,
            comment=verification.comment,
            created_at=verification.created_at
        )


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

    # Build response - get flagger info from the relationship
    flagger_user = flag.flagger
    flagger_info = UserInTeam(
        id=flagger_user.id,
        username=flagger_user.username,
        full_name=flagger_user.full_name,
        role=role
    )
    
    # Create response with all data
    response = FlagResponse(
        id=flag.id,
        contribution_id=flag.contribution_id,
        flagger_id=flag.flagger_id,
        flagger=flagger_info,
        reason=flag.reason,
        created_at=flag.created_at
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
