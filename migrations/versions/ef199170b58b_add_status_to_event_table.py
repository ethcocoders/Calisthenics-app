"""Add status to event table

Revision ID: ef199170b58b
Revises: ef7305a9a187
Create Date: 2025-11-09 22:55:59.706648
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ef199170b58b'
down_revision = 'ef7305a9a187'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('status', sa.String(length=50), nullable=False, server_default='pending')
        )


def downgrade():
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('status')
