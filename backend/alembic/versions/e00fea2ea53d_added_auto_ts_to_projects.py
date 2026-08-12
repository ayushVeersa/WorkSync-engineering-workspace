"""added auto ts to projects

Revision ID: e00fea2ea53d
Revises: 8792e85a25b2
Create Date: 2026-08-11 10:41:36.595171

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e00fea2ea53d"
down_revision: Union[str, Sequence[str], None] = "8792e85a25b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    with op.batch_alter_table("projects") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            existing_nullable=False,
        )

        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table("projects") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            server_default=None,
            existing_nullable=False,
        )

        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=None,
            existing_nullable=False,
        )
