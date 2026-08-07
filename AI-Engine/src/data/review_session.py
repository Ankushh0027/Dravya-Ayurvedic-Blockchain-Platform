import os
import json
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.data.taxonomy_review import atomic_json_write

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

@dataclass
class TaxonomyReviewSession:
    session_id: str
    reviewer_id: str
    taxonomy_version: str = "v1"
    session_status: SessionStatus = SessionStatus.ACTIVE
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reviewed_mapping_ids: List[str] = field(default_factory=list)
    skipped_mapping_ids: List[str] = field(default_factory=list)
    approved_mapping_ids: List[str] = field(default_factory=list)
    rejected_mapping_ids: List[str] = field(default_factory=list)
    needs_review_mapping_ids: List[str] = field(default_factory=list)
    current_mapping_id: Optional[str] = None
    current_candidate_group_id: Optional[str] = None
    dataset_filter: Optional[str] = None
    status_filter: Optional[str] = None
    candidate_group_filter: Optional[str] = None
    limit_filter: Optional[int] = None
    progress_snapshot: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["session_status"] = self.session_status.value if isinstance(self.session_status, SessionStatus) else str(self.session_status)
        return d

class ReviewSessionManager:
    """
    Manager for human taxonomy review sessions with crash safety, atomic JSON writes,
    reviewer isolation, and resume capabilities.
    """

    def __init__(self, version: str = "v1", reports_dir: str = r"C:\Dravya-AI-Engine\reports\dataset_analysis"):
        self.version = version
        self.reports_dir = Path(reports_dir)
        self.sessions: Dict[str, TaxonomyReviewSession] = {}
        self.load_sessions()

    def get_session_file_path(self) -> Path:
        return self.reports_dir / f"review_sessions_{self.version}.json"

    def load_sessions(self) -> Dict[str, TaxonomyReviewSession]:
        session_file = self.get_session_file_path()
        self.sessions = {}
        if not session_file.exists():
            return self.sessions

        with open(session_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                raise ValueError(f"Malformed review session artifact '{session_file}': JSON parse error: {e}")

        if not isinstance(data, dict) or "sessions" not in data:
            raise ValueError(f"Malformed review session file structure in '{session_file}'.")

        raw_sessions = data.get("sessions", {})
        if not isinstance(raw_sessions, dict):
            raise ValueError(f"Malformed 'sessions' mapping in '{session_file}'.")

        for s_id, s_dict in raw_sessions.items():
            if not isinstance(s_dict, dict) or "reviewer_id" not in s_dict or "session_status" not in s_dict:
                raise ValueError(f"Malformed review session entry for session_id '{s_id}'.")
            try:
                s_dict["session_status"] = SessionStatus(s_dict["session_status"])
            except Exception as e:
                raise ValueError(f"Invalid session_status enum in session '{s_id}': {e}")
            self.sessions[s_id] = TaxonomyReviewSession(**s_dict)

        return self.sessions

    def create_session(
        self,
        session_id: str,
        reviewer_id: str,
        dataset_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        candidate_group_filter: Optional[str] = None,
        limit_filter: Optional[int] = None
    ) -> TaxonomyReviewSession:
        if not session_id or not str(session_id).strip():
            raise ValueError("session_id must be a non-empty string.")
        if not reviewer_id or not str(reviewer_id).strip():
            raise ValueError("reviewer_id must be a non-empty string.")

        if session_id in self.sessions:
            existing = self.sessions[session_id]
            if existing.reviewer_id != reviewer_id:
                raise ValueError(f"Session '{session_id}' belongs to reviewer '{existing.reviewer_id}', not '{reviewer_id}'.")
            if existing.session_status in (SessionStatus.COMPLETED, SessionStatus.ABANDONED):
                raise ValueError(f"Session '{session_id}' is already {existing.session_status.value} and cannot be recreated.")
            return existing

        now = datetime.now(timezone.utc).isoformat()
        session = TaxonomyReviewSession(
            session_id=session_id,
            reviewer_id=reviewer_id,
            taxonomy_version=self.version,
            session_status=SessionStatus.ACTIVE,
            started_at=now,
            last_updated_at=now,
            dataset_filter=dataset_filter,
            status_filter=status_filter,
            candidate_group_filter=candidate_group_filter,
            limit_filter=limit_filter
        )
        self.sessions[session_id] = session
        self.save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[TaxonomyReviewSession]:
        return self.sessions.get(session_id)

    def resume_session(self, session_id: str, reviewer_id: str) -> TaxonomyReviewSession:
        if session_id not in self.sessions:
            raise KeyError(f"Session '{session_id}' not found.")

        session = self.sessions[session_id]

        if session.reviewer_id != reviewer_id:
            raise ValueError(f"Reviewer isolation error: Session '{session_id}' belongs to '{session.reviewer_id}', but access requested by '{reviewer_id}'.")

        if session.taxonomy_version != self.version:
            raise ValueError(f"Taxonomy version mismatch: Session '{session_id}' has version '{session.taxonomy_version}', but manager version is '{self.version}'.")

        if session.session_status == SessionStatus.COMPLETED:
            raise ValueError(f"Session '{session_id}' is COMPLETED and cannot be resumed.")

        if session.session_status == SessionStatus.ABANDONED:
            raise ValueError(f"Session '{session_id}' is ABANDONED and cannot be resumed.")

        session.session_status = SessionStatus.ACTIVE
        session.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.save_sessions()
        return session

    def pause_session(self, session_id: str) -> TaxonomyReviewSession:
        if session_id not in self.sessions:
            raise KeyError(f"Session '{session_id}' not found.")
        session = self.sessions[session_id]
        session.session_status = SessionStatus.PAUSED
        session.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.save_sessions()
        return session

    def abandon_session(self, session_id: str) -> TaxonomyReviewSession:
        if session_id not in self.sessions:
            raise KeyError(f"Session '{session_id}' not found.")
        session = self.sessions[session_id]
        session.session_status = SessionStatus.ABANDONED
        session.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.save_sessions()
        return session

    def record_decision(self, session_id: str, mapping_id: str, action_str: str):
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        if mapping_id not in session.reviewed_mapping_ids:
            session.reviewed_mapping_ids.append(mapping_id)

        if action_str == "APPROVE":
            if mapping_id not in session.approved_mapping_ids:
                session.approved_mapping_ids.append(mapping_id)
        elif action_str == "REJECT":
            if mapping_id not in session.rejected_mapping_ids:
                session.rejected_mapping_ids.append(mapping_id)
        elif action_str == "NEEDS_REVIEW":
            if mapping_id not in session.needs_review_mapping_ids:
                session.needs_review_mapping_ids.append(mapping_id)

        session.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.save_sessions()

    def record_skip(self, session_id: str, mapping_id: str):
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        if mapping_id not in session.skipped_mapping_ids:
            session.skipped_mapping_ids.append(mapping_id)
        session.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.save_sessions()

    def update_navigation(self, session_id: str, current_mapping_id: Optional[str], current_group_id: Optional[str]):
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        session.current_mapping_id = current_mapping_id
        session.current_candidate_group_id = current_group_id
        session.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.save_sessions()

    def mark_completed(self, session_id: str):
        if session_id not in self.sessions:
            return
        session = self.sessions[session_id]
        session.session_status = SessionStatus.COMPLETED
        session.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.save_sessions()

    def save_sessions(self) -> Path:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        session_file = self.get_session_file_path()
        data = {
            "taxonomy_version": self.version,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_sessions": len(self.sessions),
            "sessions": {s_id: s.to_dict() for s_id, s in self.sessions.items()}
        }
        atomic_json_write(session_file, data)
        return session_file

    def get_summary_metrics(self) -> Dict[str, Any]:
        active_cnt = sum(1 for s in self.sessions.values() if s.session_status == SessionStatus.ACTIVE)
        paused_cnt = sum(1 for s in self.sessions.values() if s.session_status == SessionStatus.PAUSED)
        completed_cnt = sum(1 for s in self.sessions.values() if s.session_status == SessionStatus.COMPLETED)
        abandoned_cnt = sum(1 for s in self.sessions.values() if s.session_status == SessionStatus.ABANDONED)

        by_reviewer: Dict[str, Dict[str, int]] = {}
        for s in self.sessions.values():
            rev = s.reviewer_id
            by_reviewer.setdefault(rev, {"total_sessions": 0, "reviewed_mappings": 0, "approved": 0, "rejected": 0, "needs_review": 0, "skipped": 0})
            by_reviewer[rev]["total_sessions"] += 1
            by_reviewer[rev]["reviewed_mappings"] += len(s.reviewed_mapping_ids)
            by_reviewer[rev]["approved"] += len(s.approved_mapping_ids)
            by_reviewer[rev]["rejected"] += len(s.rejected_mapping_ids)
            by_reviewer[rev]["needs_review"] += len(s.needs_review_mapping_ids)
            by_reviewer[rev]["skipped"] += len(s.skipped_mapping_ids)

        return {
            "active_sessions": active_cnt,
            "paused_sessions": paused_cnt,
            "completed_sessions": completed_cnt,
            "abandoned_sessions": abandoned_cnt,
            "progress_by_reviewer": by_reviewer
        }
