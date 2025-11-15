import hashlib
import uuid
import os
from typing import Optional
from pathlib import Path
from .config import settings


def calculate_file_hash(file_data: bytes) -> str:
    """Calculate SHA-256 hash of file data"""
    return hashlib.sha256(file_data).hexdigest()


def generate_uuid() -> str:
    """Generate a unique UUID"""
    return str(uuid.uuid4())


def ensure_directory(path: str):
    """Ensure a directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file_type(filename: str) -> bool:
    """Check if file type is allowed"""
    ext = get_file_extension(filename)
    return ext in settings.allowed_file_types_list


def get_storage_path(team_id: int, contribution_uuid: str, filename: str) -> str:
    """Get the storage path for a file"""
    ensure_directory(settings.ENCRYPTED_STORAGE_PATH)
    team_dir = os.path.join(settings.ENCRYPTED_STORAGE_PATH, f"team_{team_id}")
    ensure_directory(team_dir)
    ext = get_file_extension(filename)
    return os.path.join(team_dir, f"{contribution_uuid}{ext}")


def calculate_reputation_score(
    submitted_count: int,
    verified_count: int,
    instructor_verified_count: int,
    flagged_count: int
) -> float:
    """
    Calculate reputation score based on contributions
    Formula: (verified_2+ * 3) + (instructor_verified * 5) + (submitted * 1) + (flagged * -2)
    """
    score = 0.0

    # Verified by 2+ teammates
    score += verified_count * 3

    # Verified by instructor/manager
    score += instructor_verified_count * 5

    # Base submission bonus
    score += submitted_count * 1

    # Penalty for flagged contributions
    score += flagged_count * -2

    return max(0.0, score)  # Ensure score doesn't go negative
