from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from radar.database.connection import get_connection


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS startups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sector TEXT,
                product TEXT,
                description TEXT,
                founders TEXT DEFAULT '[]',
                customers TEXT DEFAULT '[]',
                funding TEXT,
                cited_technologies TEXT DEFAULT '[]',
                ai_usage_summary TEXT,
                classification_label TEXT,
                classification_confidence REAL,
                classification_rationale TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                startup_id TEXT REFERENCES startups(id),
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS source_documents (
                id TEXT PRIMARY KEY,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                url TEXT NOT NULL,
                domain TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT,
                text TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                collection_method TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence_claims (
                id TEXT PRIMARY KEY,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                source_document_id TEXT NOT NULL REFERENCES source_documents(id),
                text TEXT NOT NULL,
                claim_type TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 0.0
            );

            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                has_minimum_evidence INTEGER NOT NULL DEFAULT 0,
                source_quality TEXT NOT NULL DEFAULT 'weak',
                supporting_evidence_ids TEXT DEFAULT '[]',
                conflicts TEXT DEFAULT '[]',
                caveats TEXT DEFAULT '[]',
                requires_human_review INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                run_id INTEGER NOT NULL REFERENCES runs(id),
                technology TEXT NOT NULL,
                target_gap TEXT NOT NULL,
                technical_justification TEXT NOT NULL,
                business_justification TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'medium',
                implementation_complexity TEXT NOT NULL DEFAULT 'medium',
                suggested_next_action TEXT NOT NULL,
                startup_evidence_ids TEXT DEFAULT '[]',
                nvidia_knowledge_ids TEXT DEFAULT '[]'
            );
        """)


def save_run(query: str, startup_id: str | None = None) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO runs (query, startup_id) VALUES (?, ?)",
            (query, startup_id),
        )
        return cur.lastrowid or 0


def update_run_status(run_id: int, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE runs SET status = ?, completed_at = datetime('now') WHERE id = ?",
            (status, run_id),
        )


def save_startup(data: dict[str, Any]) -> str:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM startups WHERE name = ?", (data["name"],)
        ).fetchone()
        if existing:
            stmt = """
                UPDATE startups SET
                    sector=?, product=?, description=?, founders=?, customers=?,
                    funding=?, cited_technologies=?, ai_usage_summary=?,
                    classification_label=?, classification_confidence=?,
                    classification_rationale=?, updated_at=datetime('now')
                WHERE id=?
            """
            conn.execute(
                stmt,
                (
                    data.get("sector"),
                    data.get("product"),
                    data.get("description"),
                    json.dumps(data.get("founders", [])),
                    json.dumps(data.get("customers", [])),
                    data.get("funding"),
                    json.dumps(data.get("cited_technologies", [])),
                    data.get("ai_usage_summary"),
                    data.get("classification_label"),
                    data.get("classification_confidence"),
                    data.get("classification_rationale"),
                    existing["id"],
                ),
            )
            return existing["id"]
        stmt = """
            INSERT INTO startups
                (id, name, sector, product, description, founders, customers,
                 funding, cited_technologies, ai_usage_summary,
                 classification_label, classification_confidence, classification_rationale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn.execute(
            stmt,
            (
                data.get("id"),
                data["name"],
                data.get("sector"),
                data.get("product"),
                data.get("description"),
                json.dumps(data.get("founders", [])),
                json.dumps(data.get("customers", [])),
                data.get("funding"),
                json.dumps(data.get("cited_technologies", [])),
                data.get("ai_usage_summary"),
                data.get("classification_label"),
                data.get("classification_confidence"),
                data.get("classification_rationale"),
            ),
        )
        return data["id"]


def save_source_document(run_id: int, data: dict[str, Any]) -> str:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO source_documents
               (id, run_id, url, domain, source_type, title, text, retrieved_at, collection_method)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["id"],
                run_id,
                str(data["url"]),
                data["domain"],
                data["source_type"],
                data.get("title"),
                data["text"],
                data["retrieved_at"].isoformat()
                if isinstance(data["retrieved_at"], datetime)
                else data["retrieved_at"],
                data["collection_method"],
            ),
        )
    return data["id"]


def save_evidence_claim(run_id: int, data: dict[str, Any]) -> str:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO evidence_claims
               (id, run_id, source_document_id, text, claim_type, confidence)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data["id"],
                run_id,
                data["source_document_id"],
                data["text"],
                data["claim_type"],
                data["confidence"],
            ),
        )
    return data["id"]


def save_validation(run_id: int, data: dict[str, Any]) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO validations
               (run_id, has_minimum_evidence, source_quality, supporting_evidence_ids, conflicts, caveats, requires_human_review)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                1 if data.get("has_minimum_evidence") else 0,
                data.get("source_quality", "weak"),
                json.dumps(data.get("supporting_evidence_ids", [])),
                json.dumps(data.get("conflicts", [])),
                json.dumps(data.get("caveats", [])),
                1 if data.get("requires_human_review") else 0,
            ),
        )
        return cur.lastrowid or 0


def save_recommendation(run_id: int, data: dict[str, Any]) -> str:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO recommendations
               (id, run_id, technology, target_gap, technical_justification,
                business_justification, priority, implementation_complexity,
                suggested_next_action, startup_evidence_ids, nvidia_knowledge_ids)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["id"],
                run_id,
                data["technology"],
                data.get("target_gap", ""),
                data.get("technical_justification", ""),
                data.get("business_justification", ""),
                data.get("priority", "medium"),
                data.get("implementation_complexity", "medium"),
                data.get("suggested_next_action", ""),
                json.dumps(data.get("startup_evidence_ids", [])),
                json.dumps(data.get("nvidia_knowledge_ids", [])),
            ),
        )
    return data["id"]


def get_all_source_documents() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                sd.*,
                COUNT(ec.id) AS claim_count,
                AVG(ec.confidence) AS average_claim_confidence
            FROM source_documents sd
            LEFT JOIN evidence_claims ec ON ec.source_document_id = sd.id
            GROUP BY sd.id
            ORDER BY sd.retrieved_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def get_run_source_documents(run_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                sd.*,
                COUNT(ec.id) AS claim_count,
                AVG(ec.confidence) AS average_claim_confidence
            FROM source_documents sd
            LEFT JOIN evidence_claims ec ON ec.source_document_id = sd.id
            WHERE sd.run_id = ?
            GROUP BY sd.id
            ORDER BY sd.retrieved_at DESC
            """,
            (run_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_run_evidence_claims(run_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM evidence_claims
            WHERE run_id = ?
            ORDER BY confidence DESC, id ASC
            """,
            (run_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_runs() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, query, startup_id, status, created_at, completed_at FROM runs ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_run_by_id(run_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return dict(row) if row else None


def get_run_recommendations(run_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM recommendations WHERE run_id = ? ORDER BY priority",
            (run_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_startups() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM startups ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_startup_by_id(startup_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM startups WHERE id = ?", (startup_id,)
        ).fetchone()
        return dict(row) if row else None
