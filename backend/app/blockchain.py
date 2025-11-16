import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from .config import settings


class Block:
    """Represents a block in the blockchain"""

    def __init__(
        self,
        block_id: int,
        timestamp: str,
        contribution_id: str,
        contributor_id: int,
        contribution_type: str,
        file_hash: Optional[str],
        metadata: Dict[str, Any],
        previous_hash: str,
        verification_count: int = 0,
        reputation_score: float = 0.0
    ):
        self.block_id = block_id
        self.timestamp = timestamp
        self.contribution_id = contribution_id
        self.contributor_id = contributor_id
        self.contribution_type = contribution_type
        self.file_hash = file_hash
        self.metadata = metadata
        self.previous_hash = previous_hash
        self.verification_count = verification_count
        self.reputation_score = reputation_score
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of block data"""
        block_data = {
            "block_id": self.block_id,
            "timestamp": self.timestamp,
            "contribution_id": self.contribution_id,
            "contributor_id": self.contributor_id,
            "contribution_type": self.contribution_type,
            "file_hash": self.file_hash,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "verification_count": self.verification_count,
            "reputation_score": self.reputation_score
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            "block_id": self.block_id,
            "timestamp": self.timestamp,
            "contribution_id": self.contribution_id,
            "contributor_id": self.contributor_id,
            "contribution_type": self.contribution_type,
            "file_hash": self.file_hash,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "verification_count": self.verification_count,
            "reputation_score": self.reputation_score,
            "hash": self.hash
        }


class Blockchain:
    """Simplified blockchain implementation using SQLite"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_chain(self, team_id: int):
        """Initialize the blockchain database for a specific team"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                contribution_id TEXT NOT NULL,
                contributor_id INTEGER NOT NULL,
                contribution_type TEXT NOT NULL,
                file_hash TEXT,
                metadata TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                verification_count INTEGER DEFAULT 0,
                reputation_score REAL DEFAULT 0.0,
                hash TEXT NOT NULL,
                team_id INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chain_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()

        # Create genesis block if chain is empty
        cursor.execute("SELECT COUNT(*) FROM blocks WHERE team_id = ?", (team_id,))
        if cursor.fetchone()[0] == 0:
            self._create_genesis_block(cursor, team_id)
            conn.commit()

        conn.close()

    def _create_genesis_block(self, cursor, team_id: int):
        """Create the first block in the chain for a specific team"""
        genesis_block = Block(
            block_id=0,
            timestamp=datetime.utcnow().isoformat(),
            contribution_id="genesis",
            contributor_id=0,
            contribution_type="genesis",
            file_hash=None,
            metadata={"message": f"ContriBook Genesis Block for team {team_id}"},
            previous_hash="0" * 64,
            verification_count=0,
            reputation_score=0.0
        )

        cursor.execute("""
            INSERT INTO blocks (
                block_id, timestamp, contribution_id, contributor_id,
                contribution_type, file_hash, metadata, previous_hash,
                verification_count, reputation_score, hash, team_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            genesis_block.block_id,
            genesis_block.timestamp,
            genesis_block.contribution_id,
            genesis_block.contributor_id,
            genesis_block.contribution_type,
            genesis_block.file_hash,
            json.dumps(genesis_block.metadata),
            genesis_block.previous_hash,
            genesis_block.verification_count,
            genesis_block.reputation_score,
            genesis_block.hash,
            team_id  # Use the provided team_id for genesis
        ))

    def add_block(
        self,
        contribution_id: str,
        contributor_id: int,
        contribution_type: str,
        team_id: int,
        file_hash: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Block:
        """Add a new block to the chain"""
        if self.is_frozen():
            raise ValueError("Blockchain is frozen and cannot accept new blocks")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get the last block for this team
        cursor.execute("SELECT hash FROM blocks WHERE team_id = ? ORDER BY block_id DESC LIMIT 1", (team_id,))
        result = cursor.fetchone()
        previous_hash = result[0] if result else "0" * 64 # Fallback for first block after genesis

        # Get next block ID for this team
        cursor.execute("SELECT MAX(block_id) FROM blocks WHERE team_id = ?", (team_id,))
        last_id = cursor.fetchone()[0]
        new_block_id = (last_id or 0) + 1

        # Create new block
        new_block = Block(
            block_id=new_block_id,
            timestamp=datetime.utcnow().isoformat(),
            contribution_id=contribution_id,
            contributor_id=contributor_id,
            contribution_type=contribution_type,
            file_hash=file_hash,
            metadata=metadata or {},
            previous_hash=previous_hash,
            verification_count=0,
            reputation_score=0.0
        )

        # Insert into database
        cursor.execute("""
            INSERT INTO blocks (
                block_id, timestamp, contribution_id, contributor_id,
                contribution_type, file_hash, metadata, previous_hash,
                verification_count, reputation_score, hash, team_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_block.block_id,
            new_block.timestamp,
            new_block.contribution_id,
            new_block.contributor_id,
            new_block.contribution_type,
            new_block.file_hash,
            json.dumps(new_block.metadata),
            new_block.previous_hash,
            new_block.verification_count,
            new_block.reputation_score,
            new_block.hash,
            team_id
        ))

        conn.commit()
        conn.close()

        return new_block

    def update_block_verification(
        self,
        contribution_id: str,
        verification_count: int,
        reputation_score: float
    ):
        """Update verification count and reputation score for a block"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if block exists first
        cursor.execute("""
            SELECT block_id FROM blocks WHERE contribution_id = ?
        """, (contribution_id,))
        
        if not cursor.fetchone():
            # Block doesn't exist, nothing to update
            conn.close()
            return

        cursor.execute("""
            UPDATE blocks
            SET verification_count = ?, reputation_score = ?
            WHERE contribution_id = ?
        """, (verification_count, reputation_score, contribution_id))

        conn.commit()
        conn.close()

    def get_block_by_contribution(self, contribution_id: str) -> Optional[Dict[str, Any]]:
        """Get a block by contribution ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM blocks WHERE contribution_id = ?
        """, (contribution_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "block_id": row[0],
                "timestamp": row[1],
                "contribution_id": row[2],
                "contributor_id": row[3],
                "contribution_type": row[4],
                "file_hash": row[5],
                "metadata": json.loads(row[6]),
                "previous_hash": row[7],
                "verification_count": row[8],
                "reputation_score": row[9],
                "hash": row[10],
                "team_id": row[11]
            }
        return None

    def get_chain(self, team_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get blocks from the chain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if team_id:
            # Fetch blocks for the specific team, plus the global genesis block (block_id = 0, team_id = 0)
            cursor.execute("""
                SELECT * FROM blocks
                WHERE team_id = ? OR (block_id = 0 AND team_id = 0)
                ORDER BY block_id DESC
                LIMIT ?
            """, (team_id, limit))
        else:
            # This case should ideally not be hit if we're always passing team_id.
            # If it is, it might imply a global chain view, which we're moving away from.
            # For now, it will return all blocks across all teams in this specific db_path.
            cursor.execute("""
                SELECT * FROM blocks
                ORDER BY block_id DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        blocks = []
        for row in rows:
            blocks.append({
                "block_id": row[0],
                "timestamp": row[1],
                "contribution_id": row[2],
                "contributor_id": row[3],
                "contribution_type": row[4],
                "file_hash": row[5],
                "metadata": json.loads(row[6]),
                "previous_hash": row[7],
                "verification_count": row[8],
                "reputation_score": row[9],
                "hash": row[10],
                "team_id": row[11]
            })

        return blocks

    def verify_chain_integrity(self, team_id: int) -> bool:
        """Verify the integrity of the blockchain for a specific team"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM blocks WHERE team_id = ? ORDER BY block_id ASC", (team_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return True # An empty chain or a chain with only genesis block is considered valid

        # Special handling for genesis block if it's the first in the team's sequence
        # Assuming block_id 0 is the genesis for the *entire* system, and team's blocks start from 1
        # If a team has its own genesis, block_id=0, then we start checking from block_id=1
        start_index = 0
        if rows[0][0] == 0: # If the first block is the global genesis block
            # We don't verify the global genesis block's previous hash against a team block.
            # We start verification from the first actual team block.
            if len(rows) > 1:
                start_index = 1
            else:
                return True # Only global genesis present, considered valid

        for i in range(start_index, len(rows)):
            current_row = rows[i]
            previous_row = rows[i - 1]

            # Check if previous hash matches
            if current_row[7] != previous_row[10]:  # previous_hash != previous block's hash
                return False

            # Recalculate hash to verify
            block = Block(
                block_id=current_row[0],
                timestamp=current_row[1],
                contribution_id=current_row[2],
                contributor_id=current_row[3],
                contribution_type=current_row[4],
                file_hash=current_row[5],
                metadata=json.loads(current_row[6]),
                previous_hash=current_row[7],
                verification_count=current_row[8],
                reputation_score=current_row[9]
            )

            if block.hash != current_row[10]:
                return False

        return True

    def freeze_chain(self):
        """Freeze the blockchain (prevent new blocks)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO chain_metadata (key, value)
            VALUES ('frozen', 'true')
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO chain_metadata (key, value)
            VALUES ('frozen_at', ?)
        """, (datetime.utcnow().isoformat(),))

        conn.commit()
        conn.close()

    def unfreeze_chain(self):
        """Unfreeze the blockchain (allow new blocks)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO chain_metadata (key, value)
            VALUES ('frozen', 'false')
        """)

        cursor.execute("""
            DELETE FROM chain_metadata WHERE key = 'frozen_at'
        """)

        conn.commit()
        conn.close()

    def is_frozen(self) -> bool:
        """Check if blockchain is frozen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT value FROM chain_metadata WHERE key = 'frozen'
        """)

        result = cursor.fetchone()
        conn.close()

        return result and result[0] == 'true'

# Removed global blockchain instance
