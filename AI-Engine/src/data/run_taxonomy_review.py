import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data.taxonomy import MappingStatus
from src.data.taxonomy_review import TaxonomyReviewEngine, ReviewDecision, ReviewDecisionAction
from src.data.taxonomy_validator import TaxonomyValidator

def main():
    parser = argparse.ArgumentParser(description="Dravya AI Taxonomy Human Review CLI")
    parser.add_argument("--version", type=str, default="v1", help="Taxonomy version (default: v1)")
    parser.add_argument("--summary", action="store_true", help="Print human-readable review summary")
    parser.add_argument("--validate", action="store_true", help="Run full taxonomy system validation")
    
    parser.add_argument("--approve", type=str, default=None, help="Mapping ID to approve")
    parser.add_argument("--reject", type=str, default=None, help="Mapping ID to reject")
    parser.add_argument("--needs-review", type=str, default=None, help="Mapping ID to mark as needs review")
    
    parser.add_argument("--reviewer", type=str, default=None, help="Reviewer ID (required for decisions)")
    parser.add_argument("--approved-plant", type=str, default=None, help="Approved canonical plant ID (for --approve)")
    parser.add_argument("--reason", type=str, default=None, help="Review decision reason / evidence (required)")

    args = parser.parse_args()

    engine = TaxonomyReviewEngine(version=args.version)
    engine.load_state()

    # Handle decision flags if provided
    if args.approve or args.reject or args.needs_review:
        if not args.reviewer:
            print("[ERROR] --reviewer is required when applying a review decision.")
            sys.exit(1)
        if not args.reason:
            print("[ERROR] --reason is required when applying a review decision.")
            sys.exit(1)

        mapping_id = args.approve or args.reject or args.needs_review
        if mapping_id not in engine.mappings:
            print(f"[ERROR] Mapping ID '{mapping_id}' not found in review state.")
            sys.exit(1)

        prev_status = engine.mappings[mapping_id].mapping_status
        cand_id = engine.mappings[mapping_id].candidate_canonical_plant_id

        if args.approve:
            act = ReviewDecisionAction.APPROVE
            app_id = args.approved_plant or cand_id
        elif args.reject:
            act = ReviewDecisionAction.REJECT
            app_id = None
        else:
            act = ReviewDecisionAction.NEEDS_REVIEW
            app_id = None

        decision = ReviewDecision(
            mapping_id=mapping_id,
            taxonomy_version=args.version,
            reviewer_id=args.reviewer,
            decision=act,
            previous_status=prev_status,
            candidate_canonical_plant_id=cand_id,
            approved_canonical_plant_id=app_id,
            review_reason=args.reason,
            evidence=args.reason
        )

        try:
            updated_m = engine.apply_decision(decision)
            print(f"[SUCCESS] Applied decision '{act.value}' to mapping '{mapping_id}'. Status: {updated_m.mapping_status.value}")
        except Exception as e:
            print(f"[ERROR] Failed to apply decision: {e}")
            sys.exit(1)

    artifacts = engine.export_artifacts()
    val_report = TaxonomyValidator.validate_full_system(list(engine.plants.values()), list(engine.mappings.values()))

    if args.summary or not (args.approve or args.reject or args.needs_review):
        summary_str = engine.format_terminal_summary(val_report)
        print("\n" + summary_str)
        print(f"\nGenerated Review Artifacts:")
        print(f" - Latest Review State JSON: {artifacts['review_json']}")
        print(f" - Append-Only History JSON: {artifacts['history_json']}")
        print(f" - Validation Report JSON:  {artifacts['validation_json']}")

    if args.validate and not val_report["is_valid"]:
        print("\n[ERROR] System Validation Failed!")
        for err in val_report["errors"]:
            print(f" - {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
