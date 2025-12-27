"""Initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2025-12-22 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create organisms table
    op.create_table('organisms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('genus', sa.String(), nullable=False),
        sa.Column('species', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create strains table
    op.create_table('strains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strain_name', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('organism_id', sa.Integer(), sa.ForeignKey('organisms.id'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create analyses table
    op.create_table('analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_type', sa.String(), nullable=False),
        sa.Column('results', sa.JSON(), nullable=False),
        sa.Column('file_url', sa.String(1024), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('strain_id', sa.Integer(), sa.ForeignKey('strains.id'), nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('analyses')
    op.drop_table('users')
    op.drop_table('strains')
    op.drop_table('organisms')