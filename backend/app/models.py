from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base


class UserRole(str, enum.Enum):
    MEMBER = "member"
    INSTRUCTOR = "instructor"
    MANAGER = "manager"


class ContributionType(str, enum.Enum):
    GIT = "git"
    DOCUMENT = "document"
    IMAGE = "image"
    MEETING = "meeting"
    MENTAL = "mental"
    OTHER = "other"


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    ARCHIVED = "archived"


# Association table for team members
team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role', SQLEnum(UserRole), default=UserRole.MEMBER),
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teams = relationship("Team", secondary=team_members, back_populates="members")
    contributions = relationship("Contribution", back_populates="contributor", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="verifier", cascade="all, delete-orphan")
    flags = relationship("Flag", back_populates="flagger", cascade="all, delete-orphan")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    invite_code = Column(String, unique=True, index=True, nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    frozen_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    members = relationship("User", secondary=team_members, back_populates="teams")
    contributions = relationship("Contribution", back_populates="team", cascade="all, delete-orphan")


class Contribution(Base):
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    contribution_type = Column(SQLEnum(ContributionType), nullable=False)

    # File/Link data
    file_path = Column(String, nullable=True)  # encrypted file path
    file_hash = Column(String, nullable=True)  # SHA-256 hash
    external_link = Column(String, nullable=True)  # Git/Docs link

    # Impact and scoring
    self_assessed_impact = Column(Integer, default=3)  # 1-5 scale
    reputation_score = Column(Float, default=0.0)

    # Blockchain reference
    block_id = Column(Integer, nullable=True)
    block_hash = Column(String, nullable=True)

    # Relationships
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    contributor_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    team = relationship("Team", back_populates="contributions")
    contributor = relationship("User", back_populates="contributions")
    verifications = relationship("Verification", back_populates="contribution", cascade="all, delete-orphan")
    flags = relationship("Flag", back_populates="contribution", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    contribution_id = Column(Integer, ForeignKey('contributions.id', ondelete='CASCADE'), nullable=False)
    verifier_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    verifier_role = Column(SQLEnum(UserRole), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    contribution = relationship("Contribution", back_populates="verifications")
    verifier = relationship("User", back_populates="verifications")


class Flag(Base):
    __tablename__ = "flags"

    id = Column(Integer, primary_key=True, index=True)
    contribution_id = Column(Integer, ForeignKey('contributions.id', ondelete='CASCADE'), nullable=False)
    flagger_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    contribution = relationship("Contribution", back_populates="flags")
    flagger = relationship("User", back_populates="flags")
