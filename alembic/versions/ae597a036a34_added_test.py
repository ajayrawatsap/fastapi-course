"""Added test

Revision ID: ae597a036a34
Revises: 53f9a985b949
Create Date: 2023-08-19 12:23:26.407489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae597a036a34'
down_revision: Union[str, None] = '53f9a985b949'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('votes', sa.Column('test', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('votes', 'test')
    # ### end Alembic commands ###