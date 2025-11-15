from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import BlockResponse, ChainIntegrityResponse
from ..services import TeamService
from ..security import get_current_active_user
from ..blockchain import blockchain
from ..models import User

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])


@router.get("/chain", response_model=List[BlockResponse])
async def get_blockchain(
    team_id: Optional[int] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get blockchain data"""
    # If team_id is provided, verify user is a member
    if team_id:
        role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this team"
            )

    blocks = blockchain.get_chain(team_id, limit)
    return blocks


@router.get("/verify", response_model=ChainIntegrityResponse)
async def verify_blockchain_integrity(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify the integrity of the blockchain"""
    is_valid = blockchain.verify_chain_integrity()

    chain = blockchain.get_chain(limit=10000)
    total_blocks = len(chain)

    return ChainIntegrityResponse(
        is_valid=is_valid,
        total_blocks=total_blocks,
        message="Blockchain is valid" if is_valid else "Blockchain integrity compromised"
    )


@router.get("/block/{contribution_uuid}", response_model=BlockResponse)
async def get_block_by_contribution(
    contribution_uuid: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific block by contribution UUID"""
    from ..models import Contribution

    # Get contribution to check permissions
    contribution = db.query(Contribution).filter(
        Contribution.uuid == contribution_uuid
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

    block = blockchain.get_block_by_contribution(contribution_uuid)

    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )

    return block
