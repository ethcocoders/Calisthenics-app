"""Add level to user_profile

Revision ID: 32f5db99994c
Revises: 9aec3e085548
Create Date: 2025-11-11 06:45:55.716784

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '32f5db99994c'
down_revision = '9aec3e085548'
branch_labels = None
depends_on = None


def upgrade():
    # Drop table if exists (skip if not present)
    conn = op.get_bind()
    if conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_challenge'")).fetchone():
        op.drop_table('user_challenge')

    with op.batch_alter_table('user_profile', schema=None) as batch_op:
        batch_op.add_column(sa.Column('level', sa.Integer(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('experience_points', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    with op.batch_alter_table('user_profile', schema=None) as batch_op:
        batch_op.drop_column('experience_points')
        batch_op.drop_column('level')

    # Recreate table
    op.create_table(
        'user_challenge',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.Column('challenge_id', sa.INTEGER(), nullable=False),
        sa.Column('status', sa.VARCHAR(length=50), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenge.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user_profile.id']),
        sa.PrimaryKeyConstraint('id')
    )
