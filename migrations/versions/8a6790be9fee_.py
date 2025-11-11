"""Add user-related fields to challenge

Revision ID: 8a6790be9fee
Revises: fe758f65a55d
Create Date: 2025-11-11 10:19:23.996112
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a6790be9fee'
down_revision = 'fe758f65a55d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('challenge', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'is_user_created',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('0')
        ))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_challenge_user_id',
            'user_profile',
            ['user_id'],
            ['id']
        )


def downgrade():
    with op.batch_alter_table('challenge', schema=None) as batch_op:
        batch_op.drop_constraint('fk_challenge_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('is_user_created')
