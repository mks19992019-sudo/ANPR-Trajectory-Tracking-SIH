"""Initial PostgreSQL/PostGIS ANPR schema."""
from alembic import op
from backend.app.database import Base
import backend.app.models.entities  # register metadata
revision = "019aea4f36af"
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    Base.metadata.create_all(bind=op.get_bind())
def downgrade():
    Base.metadata.drop_all(bind=op.get_bind())
