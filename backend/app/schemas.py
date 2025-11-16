from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from .models import UserRole, ContributionType, ProjectStatus

if TYPE_CHECKING:
    from typing import ForwardRef


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInTeam(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    role: UserRole
    reputation: Optional["ReputationBreakdown"] = None

    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# Team schemas
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int
    invite_code: str
    status: ProjectStatus
    created_by: int
    created_at: datetime
    frozen_at: Optional[datetime] = None
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TeamJoin(BaseModel):
    invite_code: str


# Contribution schemas
class ContributionBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    contribution_type: ContributionType
    external_link: Optional[str] = None
    self_assessed_impact: int = Field(default=3, ge=1, le=5)


class ContributionCreate(ContributionBase):
    team_id: int


class ContributionResponse(ContributionBase):
    id: int
    uuid: str
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    reputation_score: float
    block_id: Optional[int] = None
    block_hash: Optional[str] = None
    team_id: int
    contributor_id: int
    contributor: UserInTeam
    verification_count: int = 0
    flag_count: int = 0
    verified_by_current_user: bool = False
    flagged_by_current_user: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Verification schemas
class VerificationCreate(BaseModel):
    contribution_id: int
    comment: Optional[str] = None


class VerificationResponse(BaseModel):
    id: int
    contribution_id: int
    verifier_id: int
    verifier: UserInTeam
    verifier_role: UserRole
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Flag schemas
class FlagCreate(BaseModel):
    contribution_id: int
    reason: Optional[str] = None


class FlagResponse(BaseModel):
    id: int
    contribution_id: int
    flagger_id: int
    flagger: UserInTeam
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Reputation schemas
class ReputationBreakdown(BaseModel):
    total_contributions: int
    verified_contributions: int
    instructor_verified: int
    flagged_contributions: int
    total_score: float

# Update forward references after ReputationBreakdown is defined
UserInTeam.model_rebuild()


class UserReputation(BaseModel):
    user: UserInTeam
    reputation: ReputationBreakdown


class TeamLeaderboard(BaseModel):
    team_id: int
    team_name: str
    rankings: List[UserReputation]


# Blockchain schemas
class BlockResponse(BaseModel):
    block_id: int
    timestamp: str
    contribution_id: str
    contributor_id: int
    contribution_type: str
    file_hash: Optional[str]
    metadata: dict
    previous_hash: str
    verification_count: int
    reputation_score: float
    hash: str
    team_id: int


class ChainIntegrityResponse(BaseModel):
    is_valid: bool
    total_blocks: int
    message: str


# File upload response
class FileUploadResponse(BaseModel):
    file_id: str
    file_hash: str
    file_path: str
    size_bytes: int
