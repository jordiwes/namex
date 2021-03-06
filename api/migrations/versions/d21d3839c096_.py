"""empty message

Revision ID: d21d3839c096
Revises: 0c6b29c57638
Create Date: 2020-01-08 12:54:10.048577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd21d3839c096'
down_revision = '0c6b29c57638'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('word_classification',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('word_classification', sa.String(length=4), nullable=False),
    sa.Column('word', sa.String(length=1024), nullable=False),
    sa.Column('last_name_used', sa.String(length=1024), nullable=True),
    sa.Column('last_prep_name', sa.String(length=1024), nullable=True),
    sa.Column('frequency', sa.BIGINT(), nullable=True),
    sa.Column('approved_by', sa.Integer(), nullable=True),
    sa.Column('approved_dt', sa.DateTime(timezone=True), nullable=True),
    sa.Column('start_dt', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_dt', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_updated_by', sa.Integer(), nullable=True),
    sa.Column('last_update_dt', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['last_updated_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_word_classification_word'), 'word_classification', ['word'], unique=False)
    op.create_index(op.f('ix_word_classification_word_classification'), 'word_classification', ['word_classification'], unique=False)
   # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_word_classification_word_classification'), table_name='word_classification')
    op.drop_index(op.f('ix_word_classification_word'), table_name='word_classification')
    op.drop_table('word_classification')
    # ### end Alembic commands ###
