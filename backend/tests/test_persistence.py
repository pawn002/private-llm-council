"""
Tests for the persistence layer.
"""

import pytest
from pathlib import Path
import secrets

from src.persistence import (
    encrypt_data,
    decrypt_data,
    derive_key,
    secure_delete,
    DeliberationSerializer,
    DeliberationStore,
    PersistenceError,
    DecryptionError,
    SecureDeletionError,
    SALT_SIZE,
    NONCE_SIZE,
)
from src.council import (
    Deliberation,
    Perspective,
    Critique,
    Synthesis,
    Disagreement,
    MinorityReport,
    ConfidenceScore,
)


class TestKeyDerivation:
    """Tests for key derivation."""

    def test_derive_key_produces_32_bytes(self):
        """Test that key derivation produces correct length."""
        salt = secrets.token_bytes(SALT_SIZE)
        key = derive_key("test passphrase", salt)
        assert len(key) == 32

    def test_same_passphrase_same_salt_same_key(self):
        """Test deterministic key derivation."""
        salt = secrets.token_bytes(SALT_SIZE)
        key1 = derive_key("test passphrase", salt)
        key2 = derive_key("test passphrase", salt)
        assert key1 == key2

    def test_different_passphrase_different_key(self):
        """Test different passphrases produce different keys."""
        salt = secrets.token_bytes(SALT_SIZE)
        key1 = derive_key("passphrase1", salt)
        key2 = derive_key("passphrase2", salt)
        assert key1 != key2

    def test_different_salt_different_key(self):
        """Test different salts produce different keys."""
        salt1 = secrets.token_bytes(SALT_SIZE)
        salt2 = secrets.token_bytes(SALT_SIZE)
        key1 = derive_key("test passphrase", salt1)
        key2 = derive_key("test passphrase", salt2)
        assert key1 != key2


class TestEncryption:
    """Tests for encryption/decryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test that data survives encryption/decryption roundtrip."""
        original = b"This is sensitive deliberation data"
        passphrase = "my secret passphrase"

        encrypted = encrypt_data(original, passphrase)
        decrypted = decrypt_data(encrypted, passphrase)

        assert decrypted == original

    def test_encrypted_data_is_different(self):
        """Test that encrypted data differs from original."""
        original = b"This is sensitive deliberation data"
        passphrase = "my secret passphrase"

        encrypted = encrypt_data(original, passphrase)

        assert encrypted != original
        assert len(encrypted) > len(original)  # Overhead from salt, nonce, tag

    def test_wrong_passphrase_fails(self):
        """Test that wrong passphrase fails to decrypt."""
        original = b"This is sensitive deliberation data"

        encrypted = encrypt_data(original, "correct passphrase")

        with pytest.raises(DecryptionError):
            decrypt_data(encrypted, "wrong passphrase")

    def test_corrupted_data_fails(self):
        """Test that corrupted data fails to decrypt."""
        original = b"This is sensitive deliberation data"
        passphrase = "my secret passphrase"

        encrypted = encrypt_data(original, passphrase)

        # Corrupt the ciphertext
        corrupted = encrypted[:-10] + b"corrupted!"

        with pytest.raises(DecryptionError):
            decrypt_data(corrupted, passphrase)

    def test_too_short_data_fails(self):
        """Test that data that's too short fails."""
        with pytest.raises(DecryptionError):
            decrypt_data(b"too short", "passphrase")

    def test_unicode_passphrase(self):
        """Test that unicode passphrases work."""
        original = b"Test data"
        passphrase = "пароль 密码 🔐"

        encrypted = encrypt_data(original, passphrase)
        decrypted = decrypt_data(encrypted, passphrase)

        assert decrypted == original

    def test_empty_data(self):
        """Test that empty data can be encrypted/decrypted."""
        original = b""
        passphrase = "passphrase"

        encrypted = encrypt_data(original, passphrase)
        decrypted = decrypt_data(encrypted, passphrase)

        assert decrypted == original

    def test_large_data(self):
        """Test that large data can be encrypted/decrypted."""
        original = secrets.token_bytes(1024 * 1024)  # 1 MB
        passphrase = "passphrase"

        encrypted = encrypt_data(original, passphrase)
        decrypted = decrypt_data(encrypted, passphrase)

        assert decrypted == original


class TestSecureDelete:
    """Tests for secure deletion."""

    def test_secure_delete_removes_file(self, tmp_path: Path):
        """Test that secure delete removes the file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("sensitive data")

        assert test_file.exists()

        secure_delete(test_file)

        assert not test_file.exists()

    def test_secure_delete_nonexistent_file(self, tmp_path: Path):
        """Test that secure delete handles nonexistent files."""
        test_file = tmp_path / "nonexistent.txt"

        # Should not raise
        secure_delete(test_file)

    def test_secure_delete_with_passes(self, tmp_path: Path):
        """Test secure delete with multiple passes."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("sensitive data")

        secure_delete(test_file, passes=5)

        assert not test_file.exists()


class TestDeliberationSerializer:
    """Tests for deliberation serialization."""

    @pytest.fixture
    def sample_deliberation(self) -> Deliberation:
        """Create a sample deliberation."""
        return Deliberation(
            id="test-id-123",
            question="What is the meaning of life?",
            perspectives=[
                Perspective(
                    member_id="phi",
                    model="llama3.2:8b",
                    character="Western analytical",
                    content="Life's meaning is subjective.",
                ),
            ],
            critiques=[
                Critique(
                    reviewer_id="psi",
                    rankings=["phi"],
                    comments={"phi": "Good perspective"},
                ),
            ],
            synthesis=Synthesis(
                content="The council has considered...",
                consensus_points=["Life has meaning"],
                divisions=["What that meaning is"],
                unique_insights=["Subjectivity is key"],
                confidence=ConfidenceScore(
                    overall=0.7,
                    consensus_strength=0.6,
                    dissent_strength=0.4,
                    reasoning="Moderate consensus",
                ),
            ),
            disagreements=[
                Disagreement(
                    topic="Meaning source",
                    positions={"phi": "Individual", "psi": "Collective"},
                    description="Fundamental disagreement on source",
                ),
            ],
            minority_reports=[
                MinorityReport(
                    member_id="omega",
                    position="Meaning is irrelevant",
                    rationale="Focus on experience instead",
                ),
            ],
            failed_members=[],
            timestamp=Deliberation.empty("").timestamp,
            session_id="session-123",
        )

    def test_to_dict(self, sample_deliberation: Deliberation):
        """Test serialization to dict."""
        data = DeliberationSerializer.to_dict(sample_deliberation)

        assert data["id"] == "test-id-123"
        assert data["question"] == "What is the meaning of life?"
        assert len(data["perspectives"]) == 1
        assert data["perspectives"][0]["member_id"] == "phi"
        assert data["synthesis"]["confidence"]["overall"] == 0.7

    def test_from_dict(self, sample_deliberation: Deliberation):
        """Test deserialization from dict."""
        data = DeliberationSerializer.to_dict(sample_deliberation)
        restored = DeliberationSerializer.from_dict(data)

        assert restored.id == sample_deliberation.id
        assert restored.question == sample_deliberation.question
        assert len(restored.perspectives) == len(sample_deliberation.perspectives)
        assert restored.synthesis.confidence.overall == 0.7

    def test_roundtrip(self, sample_deliberation: Deliberation):
        """Test serialization roundtrip preserves data."""
        data = DeliberationSerializer.to_dict(sample_deliberation)
        restored = DeliberationSerializer.from_dict(data)

        # Re-serialize and compare
        data2 = DeliberationSerializer.to_dict(restored)

        assert data["id"] == data2["id"]
        assert data["question"] == data2["question"]
        assert data["synthesis"]["content"] == data2["synthesis"]["content"]


class TestDeliberationStore:
    """Tests for the deliberation store."""

    @pytest.fixture
    def store(self, tmp_path: Path) -> DeliberationStore:
        """Create a test store."""
        return DeliberationStore(tmp_path / "deliberations")

    @pytest.fixture
    def sample_deliberation(self) -> Deliberation:
        """Create a sample deliberation."""
        return Deliberation.empty("Test question?")

    def test_save_creates_file(
        self, store: DeliberationStore, sample_deliberation: Deliberation
    ):
        """Test that save creates an encrypted file."""
        path = store.save(sample_deliberation, "passphrase")

        assert path.exists()
        assert path.suffix == ".enc"

    def test_save_load_roundtrip(
        self, store: DeliberationStore, sample_deliberation: Deliberation
    ):
        """Test that save/load preserves data."""
        store.save(sample_deliberation, "passphrase")
        loaded = store.load(sample_deliberation.id, "passphrase")

        assert loaded.id == sample_deliberation.id
        assert loaded.question == sample_deliberation.question

    def test_load_wrong_passphrase(
        self, store: DeliberationStore, sample_deliberation: Deliberation
    ):
        """Test that wrong passphrase fails."""
        store.save(sample_deliberation, "correct")

        with pytest.raises(DecryptionError):
            store.load(sample_deliberation.id, "wrong")

    def test_load_nonexistent(self, store: DeliberationStore):
        """Test loading nonexistent deliberation."""
        with pytest.raises(PersistenceError):
            store.load("nonexistent-id", "passphrase")

    def test_forget(
        self, store: DeliberationStore, sample_deliberation: Deliberation
    ):
        """Test secure deletion."""
        store.save(sample_deliberation, "passphrase")
        assert store.exists(sample_deliberation.id)

        store.forget(sample_deliberation.id)
        assert not store.exists(sample_deliberation.id)

    def test_list_ids(
        self, store: DeliberationStore
    ):
        """Test listing deliberation IDs."""
        # Save a few deliberations
        for i in range(3):
            d = Deliberation.empty(f"Question {i}")
            store.save(d, "passphrase")

        ids = store.list_ids()
        assert len(ids) == 3

    def test_exists(
        self, store: DeliberationStore, sample_deliberation: Deliberation
    ):
        """Test existence check."""
        assert not store.exists(sample_deliberation.id)

        store.save(sample_deliberation, "passphrase")
        assert store.exists(sample_deliberation.id)

    def test_path_traversal_prevention(self, store: DeliberationStore):
        """Test that path traversal is prevented."""
        # Attempt path traversal
        malicious_id = "../../../etc/passwd"
        path = store._get_path(malicious_id)

        # Should sanitize the ID
        assert ".." not in str(path)
        assert path.parent == store.storage_dir
