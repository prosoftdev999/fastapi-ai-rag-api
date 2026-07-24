"""change embedding dimension to 384"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dffc14810f56"
down_revision: str | Sequence[str] | None = "9a877a82eb39"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Change pgvector embedding dimension from 1536 to 384."""

    # Existing embeddings become invalid after dimension change.
    op.execute("DELETE FROM document_chunks")

    op.execute(
        """
        ALTER TABLE document_chunks
        ALTER COLUMN embedding
        TYPE vector(384)
        USING NULL
        """
    )


def downgrade() -> None:
    """Restore pgvector embedding dimension back to 1536."""

    op.execute("DELETE FROM document_chunks")

    op.execute(
        """
        ALTER TABLE document_chunks
        ALTER COLUMN embedding
        TYPE vector(1536)
        USING NULL
        """
    )
