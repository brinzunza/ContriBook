from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import BlockResponse, ChainIntegrityResponse
from ..services import TeamService
from ..security import get_current_active_user
from ..blockchain import Blockchain
from ..models import User, Team

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])


@router.get("/chain", response_model=List[BlockResponse])
async def get_blockchain(
    team_id: Optional[int] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get blockchain data"""
    # team_id is required now since each team has its own blockchain
    if not team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="team_id is required"
        )
    
    # Verify user is a member
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    # Get team to access blockchain_db_path
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if not team.blockchain_db_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Team blockchain not initialized"
        )

    team_blockchain = Blockchain(db_path=team.blockchain_db_path)
    blocks = team_blockchain.get_chain(team_id=team_id, limit=limit)
    return blocks


@router.get("/verify", response_model=ChainIntegrityResponse)
async def verify_blockchain_integrity(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify the integrity of the blockchain for a specific team"""
    # Verify user is a member
    role = TeamService.get_user_role_in_team(db, current_user.id, team_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this team"
        )

    # Get team to access blockchain_db_path
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    if not team.blockchain_db_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Team blockchain not initialized"
        )

    team_blockchain = Blockchain(db_path=team.blockchain_db_path)
    is_valid = team_blockchain.verify_chain_integrity(team_id=team_id)

    chain = team_blockchain.get_chain(team_id=team_id, limit=10000)
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

    # Get team to access blockchain_db_path
    team = db.query(Team).filter(Team.id == contribution.team_id).first()
    if not team or not team.blockchain_db_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Team blockchain not initialized"
        )

    team_blockchain = Blockchain(db_path=team.blockchain_db_path)
    block = team_blockchain.get_block_by_contribution(contribution_uuid)

    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )

    return block
