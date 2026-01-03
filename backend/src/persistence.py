"""
Persistence layer for The Sovereign Council.

Implements encrypted storage for deliberations. Your data is encrypted
with keys you control - we cannot read your saved deliberations.

Philosophy: If it's worth saving, it's worth encrypting.
"""

import json
import os
import secrets
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .council import Deliberation, Perspective, Critique, Synthesis, ConfidenceScore


# Constants
SALT_SIZE = 16  # 128 bits
NONCE_SIZE = 12  # 96 bits for AES-GCM
KEY_SIZE = 32  # 256 bits
ITERATIONS = 600_000  # OWASP 2023 recommendation for PBKDF2-SHA256


class PersistenceError(Exception):
    """Error during persistence operations."""
    pass


class DecryptionError(PersistenceError):
    """Failed to decrypt - wrong key or corrupted data."""
    pass


class SecureDeletionError(PersistenceError):
    """Failed to securely delete data."""
    pass


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """
    Derive an encryption key from a user passphrase.

    Uses PBKDF2 with SHA-256, following OWASP 2023 recommendations.

    Args:
        passphrase: User-provided passphrase
        salt: Random salt (must be stored with encrypted data)

    Returns:
        32-byte key suitable for AES-256
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_data(data: bytes, passphrase: str) -> bytes:
    """
    Encrypt data using AES-256-GCM with a passphrase-derived key.

    The output format is: salt (16 bytes) || nonce (12 bytes) || ciphertext

    Args:
        data: Raw bytes to encrypt
        passphrase: User-provided passphrase

    Returns:
        Encrypted data with salt and nonce prepended
    """
    # Generate random salt and nonce
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)

    # Derive key from passphrase
    key = derive_key(passphrase, salt)

    # Encrypt using AES-GCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    # Return salt || nonce || ciphertext
    return salt + nonce + ciphertext


def decrypt_data(encrypted: bytes, passphrase: str) -> bytes:
    """
    Decrypt data encrypted with encrypt_data.

    Args:
        encrypted: Encrypted data (salt || nonce || ciphertext)
        passphrase: User-provided passphrase

    Returns:
        Decrypted data

    Raises:
        DecryptionError: If decryption fails (wrong passphrase or corrupted)
    """
    if len(encrypted) < SALT_SIZE + NONCE_SIZE + 16:  # 16 = min GCM tag
        raise DecryptionError("Encrypted data too short")

    # Extract salt, nonce, and ciphertext
    salt = encrypted[:SALT_SIZE]
    nonce = encrypted[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
    ciphertext = encrypted[SALT_SIZE + NONCE_SIZE :]

    # Derive key from passphrase
    key = derive_key(passphrase, salt)

    # Decrypt
    try:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise DecryptionError(
            "Decryption failed. Wrong passphrase or corrupted data."
        ) from e


def secure_delete(path: Path, passes: int = 3) -> None:
    """
    Securely delete a file by overwriting before removal.

    Args:
        path: Path to file to delete
        passes: Number of overwrite passes (default 3)

    Raises:
        SecureDeletionError: If secure deletion fails
    """
    if not path.exists():
        return

    try:
        file_size = path.stat().st_size

        # Overwrite with random data multiple times
        for _ in range(passes):
            with open(path, "wb") as f:
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())

        # Final overwrite with zeros
        with open(path, "wb") as f:
            f.write(b"\x00" * file_size)
            f.flush()
            os.fsync(f.fileno())

        # Remove the file
        path.unlink()

    except Exception as e:
        raise SecureDeletionError(f"Failed to securely delete {path}: {e}") from e


class DeliberationSerializer:
    """Serializes and deserializes Deliberation objects."""

    @staticmethod
    def _serialize_perspectives(deliberation: Deliberation) -> list[dict[str, Any]]:
        """Serialize perspectives list."""
        return [
            {
                "member_id": p.member_id,
                "model": p.model,
                "character": p.character,
                "content": p.content,
                "timestamp": p.timestamp.isoformat(),
            }
            for p in deliberation.perspectives
        ]

    @staticmethod
    def _serialize_synthesis(deliberation: Deliberation) -> dict[str, Any]:
        """Serialize synthesis with confidence."""
        confidence = None
        if deliberation.synthesis.confidence:
            confidence = {
                "overall": deliberation.synthesis.confidence.overall,
                "consensus_strength": deliberation.synthesis.confidence.consensus_strength,
                "dissent_strength": deliberation.synthesis.confidence.dissent_strength,
                "reasoning": deliberation.synthesis.confidence.reasoning,
            }
        return {
            "content": deliberation.synthesis.content,
            "consensus_points": deliberation.synthesis.consensus_points,
            "divisions": deliberation.synthesis.divisions,
            "unique_insights": deliberation.synthesis.unique_insights,
            "confidence": confidence,
        }

    @staticmethod
    def _serialize_disagreements(
        deliberation: Deliberation, include_extended: bool = False
    ) -> list[dict[str, Any]]:
        """Serialize disagreements list.

        Args:
            deliberation: The deliberation to serialize
            include_extended: If True, includes severity and implications fields
        """
        disagreements = []
        for d in deliberation.disagreements:
            disagreement_dict: dict[str, Any] = {
                "topic": d.topic,
                "description": d.description,
                "positions": d.positions,
            }
            if include_extended:
                if hasattr(d, "severity") and d.severity is not None:
                    disagreement_dict["severity"] = (
                        d.severity.value if hasattr(d.severity, "value") else str(d.severity)
                    )
                if hasattr(d, "implications") and d.implications is not None:
                    disagreement_dict["implications"] = d.implications
            disagreements.append(disagreement_dict)
        return disagreements

    @staticmethod
    def _serialize_minority_reports(deliberation: Deliberation) -> list[dict[str, Any]]:
        """Serialize minority reports list."""
        return [
            {
                "member_id": mr.member_id,
                "position": mr.position,
                "rationale": mr.rationale,
            }
            for mr in deliberation.minority_reports
        ]

    @staticmethod
    def to_api_response(deliberation: Deliberation) -> dict[str, Any]:
        """
        Serialize deliberation for API responses.

        This format is used by all API endpoints (POST /deliberate,
        SSE /deliberate/stream, POST /deliberations/load).
        """
        return {
            "id": deliberation.id,
            "question": deliberation.question,
            "synthesis": DeliberationSerializer._serialize_synthesis(deliberation),
            "confidence": None,  # Deprecated - confidence now inside synthesis
            "perspectives": DeliberationSerializer._serialize_perspectives(deliberation),
            "disagreements": DeliberationSerializer._serialize_disagreements(
                deliberation, include_extended=True
            ),
            "minority_reports": DeliberationSerializer._serialize_minority_reports(deliberation),
            "timestamp": deliberation.timestamp.isoformat(),
            "session_id": deliberation.session_id,
        }

    @staticmethod
    def to_dict(deliberation: Deliberation) -> dict[str, Any]:
        """
        Convert a Deliberation to a serializable dictionary for storage.

        This format includes critiques and is used for encrypted persistence.
        """
        base = DeliberationSerializer.to_api_response(deliberation)
        # Remove deprecated field not needed in storage
        del base["confidence"]
        # Add critiques for storage (not needed in API responses)
        base["critiques"] = [
            {
                "reviewer_id": c.reviewer_id,
                "rankings": c.rankings,
                "comments": c.comments,
            }
            for c in deliberation.critiques
        ]
        return base

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Deliberation:
        """Reconstruct a Deliberation from a dictionary."""
        from .council import Disagreement, MinorityReport

        # Parse perspectives
        perspectives = [
            Perspective(
                member_id=p["member_id"],
                model=p["model"],
                character=p["character"],
                content=p["content"],
                timestamp=datetime.fromisoformat(p["timestamp"]),
            )
            for p in data["perspectives"]
        ]

        # Parse critiques
        critiques = [
            Critique(
                reviewer_id=c["reviewer_id"],
                rankings=c["rankings"],
                comments=c["comments"],
            )
            for c in data["critiques"]
        ]

        # Parse synthesis
        synth_data = data["synthesis"]
        confidence = None
        if synth_data.get("confidence"):
            conf_data = synth_data["confidence"]
            confidence = ConfidenceScore(
                overall=conf_data["overall"],
                consensus_strength=conf_data["consensus_strength"],
                dissent_strength=conf_data["dissent_strength"],
                reasoning=conf_data["reasoning"],
            )

        synthesis = Synthesis(
            content=synth_data["content"],
            consensus_points=synth_data["consensus_points"],
            divisions=synth_data["divisions"],
            unique_insights=synth_data["unique_insights"],
            confidence=confidence,
        )

        # Parse disagreements
        disagreements = [
            Disagreement(
                topic=d["topic"],
                positions=d["positions"],
                description=d["description"],
            )
            for d in data["disagreements"]
        ]

        # Parse minority reports
        minority_reports = [
            MinorityReport(
                member_id=mr["member_id"],
                position=mr["position"],
                rationale=mr["rationale"],
            )
            for mr in data["minority_reports"]
        ]

        return Deliberation(
            id=data["id"],
            question=data["question"],
            perspectives=perspectives,
            critiques=critiques,
            synthesis=synthesis,
            disagreements=disagreements,
            minority_reports=minority_reports,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"],
        )


class DeliberationStore:
    """
    Encrypted storage for deliberations.

    All saved deliberations are encrypted. We cannot read your data.
    You control the key. If you lose it, your data is gone forever.
    This is a feature, not a bug.
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize the store.

        Args:
            storage_dir: Directory to store encrypted deliberations
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, deliberation_id: str) -> Path:
        """Get the storage path for a deliberation."""
        # Sanitize ID to prevent path traversal
        safe_id = "".join(c for c in deliberation_id if c.isalnum() or c == "-")
        return self.storage_dir / f"{safe_id}.enc"

    def save(self, deliberation: Deliberation, passphrase: str) -> Path:
        """
        Save an encrypted deliberation.

        Args:
            deliberation: The deliberation to save
            passphrase: User-provided encryption passphrase

        Returns:
            Path to the saved file

        Raises:
            PersistenceError: If save fails
        """
        try:
            # Serialize to JSON
            data = DeliberationSerializer.to_dict(deliberation)
            json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")

            # Encrypt
            encrypted = encrypt_data(json_bytes, passphrase)

            # Write to file
            path = self._get_path(deliberation.id)
            with open(path, "wb") as f:
                f.write(encrypted)
                f.flush()
                os.fsync(f.fileno())

            return path

        except Exception as e:
            raise PersistenceError(f"Failed to save deliberation: {e}") from e

    def load(self, deliberation_id: str, passphrase: str) -> Deliberation:
        """
        Load and decrypt a deliberation.

        Args:
            deliberation_id: ID of the deliberation to load
            passphrase: User-provided decryption passphrase

        Returns:
            Decrypted Deliberation

        Raises:
            PersistenceError: If load fails
            DecryptionError: If decryption fails
        """
        path = self._get_path(deliberation_id)

        if not path.exists():
            raise PersistenceError(f"Deliberation not found: {deliberation_id}")

        try:
            # Read encrypted data
            with open(path, "rb") as f:
                encrypted = f.read()

            # Decrypt
            json_bytes = decrypt_data(encrypted, passphrase)

            # Deserialize
            data = json.loads(json_bytes.decode("utf-8"))
            return DeliberationSerializer.from_dict(data)

        except DecryptionError:
            raise
        except Exception as e:
            raise PersistenceError(f"Failed to load deliberation: {e}") from e

    def forget(self, deliberation_id: str, passes: int = 3) -> None:
        """
        Securely delete a deliberation.

        The right to be forgotten, implemented literally.

        Args:
            deliberation_id: ID of the deliberation to delete
            passes: Number of overwrite passes (default 3)

        Raises:
            SecureDeletionError: If secure deletion fails
        """
        path = self._get_path(deliberation_id)
        secure_delete(path, passes)

    def list_ids(self) -> list[str]:
        """
        List all saved deliberation IDs.

        Note: This only returns IDs, not content. Content requires passphrase.

        Returns:
            List of deliberation IDs
        """
        ids = []
        for path in self.storage_dir.glob("*.enc"):
            ids.append(path.stem)
        return ids

    def exists(self, deliberation_id: str) -> bool:
        """Check if a deliberation exists."""
        return self._get_path(deliberation_id).exists()
