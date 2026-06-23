"""add run step progress table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PIPELINE_STEPS = (
    "search_planner",
    "scraper",
    "extractor",
    "validator",
    "classifier",
    "nvidia_rag",
    "recommendation",
    "briefing",
)


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS run_steps (
            run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
            step_key TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            started_at TEXT,
            completed_at TEXT,
            error_message TEXT,
            PRIMARY KEY (run_id, step_key)
        )
    """)
    for step in PIPELINE_STEPS:
        op.execute(
            f"""
            INSERT OR IGNORE INTO run_steps (run_id, step_key, status)
            SELECT id, '{step}',
                   CASE WHEN status = 'completed' THEN 'completed'
                        WHEN status = 'failed' THEN 'failed'
                        ELSE 'pending'
                   END
            FROM runs
            """
        )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS run_steps")