"""Add user-created challenges and badge system

Revision ID: fe758f65a55d
Revises: 32a1c68093c3
Create Date: 2025-11-11 07:23:31.813374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe758f65a55d'
down_revision = '32a1c68093c3'
branch_labels = None
depends_on = None


def upgrade():
    # Create badge table
    op.create_table(
        'badge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('challenges_required', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('challenges_required', name='uq_badge_challenges_required'),
        sa.UniqueConstraint('name', name='uq_badge_name')
    )

    # Create user_badge table
    op.create_table(
        'user_badge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_id', sa.Integer(), nullable=False),
        sa.Column('date_earned', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['badge_id'], ['badge.id'], name='fk_user_badge_badge_id'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profile.id'], name='fk_user_badge_user_id'),
        sa.PrimaryKeyConstraint('id')
    )

    # Alter challenge table
    with op.batch_alter_table('challenge', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_user_created', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_challenge_user_id',
            'user_profile',
            ['user_id'],
            ['id']
        )


def downgrade():
    # Revert challenge table changes
    with op.batch_alter_table('challenge', schema=None) as batch_op:
        batch_op.drop_constraint('fk_challenge_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('is_user_created')

    # Drop user_badge and badge tables
    op.drop_table('user_badge')
    op.drop_table('badge')
