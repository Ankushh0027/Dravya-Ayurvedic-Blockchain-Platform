import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.abspath(r"C:\Dravya-AI-Engine"))

from src.data.taxonomy import MappingStatus
from src.data.taxonomy_review import ReviewDecision, ReviewDecisionAction
from src.data.taxonomy_review_queue import TaxonomyReviewQueue, ReviewQueueItem
from src.data.botanical_review import BotanicalReviewAnalyzer, RecommendationAction, BotanicalReviewGroup
from src.data.review_session import ReviewSessionManager, SessionStatus, TaxonomyReviewSession

def print_queue_item(item: ReviewQueueItem, recommendation_info: Optional[Dict[str, Any]] = None):
    print("============================================================")
    print("HUMAN BOTANICAL TAXONOMY REVIEW ITEM")
    print("============================================================")
    print(f"1.  Mapping ID:                  {item.mapping_id}")
    print(f"2.  Source Dataset:              {item.source_dataset}")
    print(f"3.  Original Class Name:         {item.original_class_name}")
    print(f"4.  Normalized Name:             {item.normalized_name}")
    print(f"5.  Candidate Canonical Plant ID:{item.candidate_canonical_plant_id or 'None'}")
    print(f"6.  Canonical Plant Name:        {item.candidate_canonical_name or 'None'}")

    sci_name = recommendation_info.get("scientific_name") if recommendation_info else None
    print(f"7.  Scientific Name:             {sci_name or 'None'}")
    print(f"8.  Health Condition:            {item.health_condition}")
    print(f"9.  Confidence Level:            {item.confidence}")
    print(f"10. Match Reason:                {item.match_reason}")
    print(f"11. Existing Evidence:           {item.evidence or 'None'}")

    if recommendation_info:
        print(f"12. Botanical Recommendation:    {recommendation_info.get('recommendation', 'None')}")
        print(f"13. Recommendation Reason:       {recommendation_info.get('reason', 'None')}")
        rel_classes = recommendation_info.get("related_classes", [])
        print(f"14. Related Source Classes:      {', '.join(rel_classes) if rel_classes else 'None'}")
    else:
        print("12. Botanical Recommendation:    None")
        print("13. Recommendation Reason:       None")
        print("14. Related Source Classes:      None")

    print(f"15. Current Review Status:       {item.current_mapping_status}")
    print("------------------------------------------------------------")
    print("⚠️  BOTANICAL RECOMMENDATION != HUMAN APPROVAL")
    print("    Recommendations are non-binding review aids only.")
    print("============================================================")

def print_candidate_group(group: BotanicalReviewGroup):
    print("============================================================")
    print(f"CANDIDATE CANONICAL PLANT GROUP: {group.canonical_plant_id}")
    print("============================================================")
    print(f"Canonical Plant Name:     {group.candidate_canonical_name}")
    print(f"Scientific Name:          {group.scientific_name or 'None'}")
    print(f"Aliases:                  {', '.join(group.aliases) if group.aliases else 'None'}")
    print("------------------------------------------------------------")
    print(f"Source Datasets:          {', '.join(group.source_datasets)}")
    print(f"Original Class Names:     {', '.join(group.original_class_names)}")
    print(f"Normalized Names:         {', '.join(group.normalized_names)}")
    print(f"Health Conditions:        {', '.join(group.health_conditions)}")
    print(f"Confidence Levels:        {', '.join(group.confidence_levels)}")
    print(f"Botanical Recommendation: {group.review_recommendation}")
    print(f"Recommendation Reason:    {group.recommendation_reason}")
    print("------------------------------------------------------------")
    print("Source Mappings in Group:")
    for idx, m in enumerate(group.source_mappings, 1):
        print(f"  [{idx}] Mapping ID: {m.get('mapping_id')} | Dataset: {m.get('source_dataset')} | Class: '{m.get('original_class_name')}' | Health: {m.get('health_condition')} | Status: {m.get('mapping_status')}")
    print("------------------------------------------------------------")
    print("⚠️  BOTANICAL RECOMMENDATION != HUMAN APPROVAL")
    print("============================================================")

def print_session_summary(session: TaxonomyReviewSession, queue: TaxonomyReviewQueue):
    print("============================================================")
    print("DRAVYA AI HUMAN REVIEW SESSION SUMMARY")
    print("============================================================")
    print(f"Session ID:                   {session.session_id}")
    print(f"Reviewer ID:                  {session.reviewer_id}")
    print(f"Taxonomy Version:             {session.taxonomy_version}")
    print(f"Session Status:               {session.session_status.value if isinstance(session.session_status, SessionStatus) else session.session_status}")
    print(f"Started At:                   {session.started_at}")
    print(f"Last Updated At:              {session.last_updated_at}")
    print("------------------------------------------------------------")
    print("Session Scope & Filters:")
    print(f"Candidate Group Filter:       {session.candidate_group_filter or 'None'}")
    print(f"Dataset Filter:               {session.dataset_filter or 'None'}")
    print(f"Status Filter:                {session.status_filter or 'None'}")
    print(f"Limit Filter:                 {session.limit_filter or 'None'}")
    print("------------------------------------------------------------")
    print("Session Actions Summary:")
    print(f"Reviewed Mappings Count:      {len(session.reviewed_mapping_ids)}")
    print(f"  - Approved:                 {len(session.approved_mapping_ids)}")
    print(f"  - Rejected:                 {len(session.rejected_mapping_ids)}")
    print(f"  - Needs Review:             {len(session.needs_review_mapping_ids)}")
    print(f"Skipped Mappings Count:       {len(session.skipped_mapping_ids)}")
    print("------------------------------------------------------------")
    print("Navigation State:")
    print(f"Current Mapping ID:           {session.current_mapping_id or 'None'}")
    print(f"Current Candidate Group ID:   {session.current_candidate_group_id or 'None'}")
    print("============================================================")

def prompt_approval_confirmation(
    mapping_id: str,
    source_dataset: str,
    original_class_name: str,
    candidate_plant_id: str,
    canonical_name: str,
    scientific_name: str,
    health_condition: str,
    reviewer_id: str,
    evidence: str,
    input_func=input
) -> bool:
    print("\n============================================================")
    print("APPROVAL PREVIEW & EXPLICIT CONFIRMATION")
    print("============================================================")
    print(f"Mapping ID:                   {mapping_id}")
    print(f"Source Dataset:               {source_dataset}")
    print(f"Original Class Name:          {original_class_name}")
    print(f"Candidate Canonical Plant ID: {candidate_plant_id}")
    print(f"Canonical Name:               {canonical_name}")
    print(f"Scientific Name:              {scientific_name}")
    print(f"Health Condition:             {health_condition}")
    print(f"Reviewer ID:                  {reviewer_id}")
    print(f"Review Evidence / Reason:     {evidence}")
    print("============================================================")
    
    response = input_func("CONFIRM APPROVE? [y/N]: ").strip()
    return response.lower() in ("y", "yes")

def run_interactive_review(
    queue: TaxonomyReviewQueue,
    session_mgr: Optional[ReviewSessionManager] = None,
    session_id: Optional[str] = None,
    reviewer_id: Optional[str] = None,
    resume_flag: bool = False,
    dataset_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    mapping_id_filter: Optional[str] = None,
    candidate_group_filter: Optional[str] = None,
    limit: Optional[int] = 10,
    reviewer_default: str = "botanist_expert",
    input_func=input
):
    session: Optional[TaxonomyReviewSession] = None
    if session_id and reviewer_id and session_mgr:
        if resume_flag:
            session = session_mgr.resume_session(session_id, reviewer_id)
            dataset_filter = dataset_filter or session.dataset_filter
            status_filter = status_filter or session.status_filter
            candidate_group_filter = candidate_group_filter or session.candidate_group_filter
            limit = limit or session.limit_filter
        else:
            session = session_mgr.create_session(
                session_id=session_id,
                reviewer_id=reviewer_id,
                dataset_filter=dataset_filter,
                status_filter=status_filter,
                candidate_group_filter=candidate_group_filter,
                limit_filter=limit
            )

    items = queue.get_all()

    if candidate_group_filter:
        items = [i for i in items if (i.candidate_canonical_plant_id or "UNMAPPED").lower() == candidate_group_filter.lower()]
    elif mapping_id_filter:
        items = [i for i in items if i.mapping_id.lower() == mapping_id_filter.lower()]
    elif status_filter:
        items = [i for i in items if i.current_mapping_status.lower() == status_filter.lower()]
    else:
        items = queue.get_pending()

    if dataset_filter:
        items = [i for i in items if i.source_dataset.lower() == dataset_filter.lower()]

    if not items:
        print("\n[INFO] No taxonomy review items match the specified filters.")
        if session:
            session_mgr.mark_completed(session.session_id)
        return

    # If resuming a session, skip already reviewed mappings within scope
    if session and session.reviewed_mapping_ids:
        items = [i for i in items if i.mapping_id not in session.reviewed_mapping_ids]

    if not items:
        print("\n[INFO] All items in this session scope have already been reviewed.")
        if session:
            session_mgr.mark_completed(session.session_id)
        return

    if limit and limit > 0:
        items = items[:limit]

    analyzer = BotanicalReviewAnalyzer(version=queue.version, reports_dir=str(queue.reports_dir))
    botanical_groups = {g.canonical_plant_id: g for g in analyzer.analyze()}

    print(f"\nStarting interactive taxonomy review session ({len(items)} items in batch limit={limit or 'all'}).\n")

    for idx, item in enumerate(items, 1):
        if session:
            session_mgr.update_navigation(session.session_id, current_mapping_id=item.mapping_id, current_group_id=item.candidate_canonical_plant_id)

        print(f"\n[Item {idx} / {len(items)}]")

        rec_info = None
        if item.candidate_canonical_plant_id and item.candidate_canonical_plant_id in botanical_groups:
            g = botanical_groups[item.candidate_canonical_plant_id]
            rec_info = {
                "scientific_name": g.scientific_name,
                "recommendation": g.review_recommendation,
                "reason": g.recommendation_reason,
                "related_classes": [c for c in g.original_class_names if c != item.original_class_name]
            }

        print_queue_item(item, recommendation_info=rec_info)

        while True:
            choice = input_func("\nAction -> [A]pprove, [R]eject, [N]eeds_review, [S]kip, [P]ause, [Q]uit/Exit: ").strip().upper()

            if choice == "A":
                rev_user = reviewer_id or reviewer_default
                reviewer = input_func(f"Reviewer ID [{rev_user}]: ").strip() or rev_user
                approved_plant = input_func(f"Canonical Plant ID [{item.candidate_canonical_plant_id}]: ").strip() or item.candidate_canonical_plant_id
                reason = input_func("Approval reason / evidence: ").strip()

                if not reason:
                    print("[ERROR] Approval reason / evidence is required!")
                    continue
                if not approved_plant:
                    print("[ERROR] Canonical plant ID is required!")
                    continue

                sci_name = rec_info.get("scientific_name", "None") if rec_info else "None"
                confirmed = prompt_approval_confirmation(
                    mapping_id=item.mapping_id,
                    source_dataset=item.source_dataset,
                    original_class_name=item.original_class_name,
                    candidate_plant_id=approved_plant,
                    canonical_name=item.candidate_canonical_name or "Unknown",
                    scientific_name=sci_name,
                    health_condition=item.health_condition,
                    reviewer_id=reviewer,
                    evidence=reason,
                    input_func=input_func
                )

                if not confirmed:
                    print("[CANCELLED] Approval cancelled. Mapping status remains unchanged.")
                    continue

                decision = ReviewDecision(
                    mapping_id=item.mapping_id,
                    taxonomy_version=queue.version,
                    reviewer_id=reviewer,
                    decision=ReviewDecisionAction.APPROVE,
                    previous_status=MappingStatus(item.current_mapping_status),
                    candidate_canonical_plant_id=item.candidate_canonical_plant_id,
                    approved_canonical_plant_id=approved_plant,
                    review_reason=reason,
                    evidence=reason
                )

                try:
                    queue.engine.apply_decision(decision)
                    queue.engine.export_artifacts()
                    queue.export_progress_report()
                    analyzer.generate_report()
                    queue.reload()
                    if session:
                        session_mgr.record_decision(session.session_id, item.mapping_id, "APPROVE")
                    print(f"[SUCCESS] Approved mapping '{item.mapping_id}' as '{approved_plant}'")
                    break
                except Exception as e:
                    print(f"[ERROR] Approval failed: {e}")

            elif choice == "R":
                rev_user = reviewer_id or reviewer_default
                reviewer = input_func(f"Reviewer ID [{rev_user}]: ").strip() or rev_user
                reason = input_func("Rejection reason / evidence: ").strip()

                if not reason:
                    print("[ERROR] Rejection reason / evidence is required!")
                    continue

                decision = ReviewDecision(
                    mapping_id=item.mapping_id,
                    taxonomy_version=queue.version,
                    reviewer_id=reviewer,
                    decision=ReviewDecisionAction.REJECT,
                    previous_status=MappingStatus(item.current_mapping_status),
                    candidate_canonical_plant_id=item.candidate_canonical_plant_id,
                    review_reason=reason,
                    evidence=reason
                )

                try:
                    queue.engine.apply_decision(decision)
                    queue.engine.export_artifacts()
                    queue.export_progress_report()
                    analyzer.generate_report()
                    queue.reload()
                    if session:
                        session_mgr.record_decision(session.session_id, item.mapping_id, "REJECT")
                    print(f"[SUCCESS] Rejected mapping '{item.mapping_id}'")
                    break
                except Exception as e:
                    print(f"[ERROR] Rejection failed: {e}")

            elif choice == "N":
                rev_user = reviewer_id or reviewer_default
                reviewer = input_func(f"Reviewer ID [{rev_user}]: ").strip() or rev_user
                reason = input_func("Needs-review reason / evidence: ").strip()

                if not reason:
                    print("[ERROR] Needs-review reason / evidence is required!")
                    continue

                decision = ReviewDecision(
                    mapping_id=item.mapping_id,
                    taxonomy_version=queue.version,
                    reviewer_id=reviewer,
                    decision=ReviewDecisionAction.NEEDS_REVIEW,
                    previous_status=MappingStatus(item.current_mapping_status),
                    candidate_canonical_plant_id=item.candidate_canonical_plant_id,
                    review_reason=reason,
                    evidence=reason
                )

                try:
                    queue.engine.apply_decision(decision)
                    queue.engine.export_artifacts()
                    queue.export_progress_report()
                    analyzer.generate_report()
                    queue.reload()
                    if session:
                        session_mgr.record_decision(session.session_id, item.mapping_id, "NEEDS_REVIEW")
                    print(f"[SUCCESS] Marked mapping '{item.mapping_id}' as NEEDS_REVIEW")
                    break
                except Exception as e:
                    print(f"[ERROR] Decision failed: {e}")

            elif choice == "S":
                if session:
                    session_mgr.record_skip(session.session_id, item.mapping_id)
                print(f"[SKIP] Skipped mapping '{item.mapping_id}' (No state change made).")
                break

            elif choice in ("P", "PAUSE"):
                if session:
                    session_mgr.pause_session(session.session_id)
                    print(f"\n[PAUSED] Session '{session.session_id}' safely paused.")
                return

            elif choice in ("Q", "EXIT"):
                if session:
                    session_mgr.pause_session(session.session_id)
                    print(f"\n[QUIT] Exiting interactive taxonomy review. Session '{session.session_id}' paused.")
                else:
                    print("\n[QUIT] Exiting interactive taxonomy review.")
                return
            else:
                print("[ERROR] Invalid choice. Please select A, R, N, S, P, or Q.")

def main():
    parser = argparse.ArgumentParser(description="Dravya AI Production Taxonomy Review Queue CLI")
    parser.add_argument("--version", type=str, default="v1", help="Taxonomy version (default: v1)")
    parser.add_argument("--summary", action="store_true", help="Display taxonomy review progress summary")
    parser.add_argument("--next", action="store_true", help="Show next pending review item")
    parser.add_argument("--pending", action="store_true", help="List all pending review items")
    parser.add_argument("--groups", action="store_true", help="List candidate plant groups")
    parser.add_argument("--candidate-group", type=str, default=None, help="Filter/review by candidate canonical plant ID (e.g. PLANT-SARACA-ASOCA-4B8F7A)")
    parser.add_argument("--dataset", type=str, default=None, help="Filter review queue by source dataset ID (e.g. CIMPd, Hugging_Face, Kaggle)")
    parser.add_argument("--status", type=str, default=None, help="Filter review queue by mapping status (e.g. UNREVIEWED, NEEDS_REVIEW, APPROVED, REJECTED)")
    parser.add_argument("--mapping-id", type=str, default=None, help="Filter review queue by specific mapping ID (e.g. map_v1_00001)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of items output in pending/interactive review mode (e.g. 10)")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive human review mode")
    parser.add_argument("--session-id", type=str, default=None, help="Review session ID (e.g. session_v1_001)")
    parser.add_argument("--reviewer-id", type=str, default=None, help="Reviewer ID (e.g. reviewer_001)")
    parser.add_argument("--resume", action="store_true", help="Resume an existing review session")
    parser.add_argument("--pause", action="store_true", help="Pause an active review session")
    parser.add_argument("--abandon", action="store_true", help="Abandon an active or paused review session")
    parser.add_argument("--session-summary", action="store_true", help="Display review session summary")
    parser.add_argument("--completion-readiness", action="store_true", help="Display human review completion & dataset generation readiness report")

    args = parser.parse_args()

    queue = TaxonomyReviewQueue(version=args.version)
    session_mgr = ReviewSessionManager(version=args.version, reports_dir=str(queue.reports_dir))
    report_path = queue.export_progress_report()

    # Generate Botanical Review Report
    analyzer = BotanicalReviewAnalyzer(version=args.version, reports_dir=str(queue.reports_dir))
    botanical_report_path = analyzer.generate_report()
    botanical_groups = analyzer.analyze()
    groups_by_id = {g.canonical_plant_id: g for g in botanical_groups}

    if args.completion_readiness:
        from src.data.review_completion import HumanReviewCompletionAnalyzer
        comp_analyzer = HumanReviewCompletionAnalyzer(version=args.version, reports_dir=str(queue.reports_dir))
        comp_report = comp_analyzer.analyze_completion_readiness()
        print("\n" + comp_analyzer.format_terminal_summary(comp_report))
        print(f"\nGenerated Completion Readiness Report JSON: {queue.reports_dir / f'human_review_completion_readiness_{args.version}.json'}")
        return

    if args.pause and args.session_id:
        sess = session_mgr.pause_session(args.session_id)
        print(f"\n[SUCCESS] Session '{args.session_id}' marked as PAUSED.")
        print_session_summary(sess, queue)
        return

    if args.abandon and args.session_id:
        sess = session_mgr.abandon_session(args.session_id)
        print(f"\n[SUCCESS] Session '{args.session_id}' marked as ABANDONED.")
        print_session_summary(sess, queue)
        return

    if args.session_summary:
        if args.session_id:
            sess = session_mgr.get_session(args.session_id)
            if sess:
                print_session_summary(sess, queue)
            else:
                print(f"[ERROR] Session '{args.session_id}' not found.")
        else:
            print("\n============================================================")
            print("DRAVYA AI REVIEW SESSIONS OVERVIEW")
            print("============================================================")
            metrics = session_mgr.get_summary_metrics()
            print(f"Total Active Sessions:     {metrics['active_sessions']}")
            print(f"Total Paused Sessions:     {metrics['paused_sessions']}")
            print(f"Total Completed Sessions:  {metrics['completed_sessions']}")
            print(f"Total Abandoned Sessions:  {metrics['abandoned_sessions']}")
            print("============================================================")
        return

    if args.summary or (not args.next and not args.pending and not args.dataset and not args.status and not args.mapping_id and not args.candidate_group and not args.groups and not args.interactive):
        print("\n" + queue.format_terminal_progress())
        print(f"\nGenerated Review Progress JSON: {report_path}")
        print(f"Generated Botanical Review Report JSON: {botanical_report_path}")

    if args.groups:
        print(f"\n[CANDIDATE PLANT GROUPS COUNT: {len(botanical_groups)}]")
        for g in (botanical_groups[:args.limit] if args.limit else botanical_groups):
            print(f" - [{g.canonical_plant_id}] {g.candidate_canonical_name} ({g.scientific_name or 'No sci name'}) | Sources: {len(g.source_mappings)} mappings | Rec: {g.review_recommendation}")

    if args.candidate_group and not args.interactive:
        g = groups_by_id.get(args.candidate_group)
        if g:
            print_candidate_group(g)
        else:
            print(f"\n[ERROR] Candidate plant group '{args.candidate_group}' not found.")

    if args.next:
        nxt = queue.get_next()
        if nxt:
            print("\n[NEXT PENDING TAXONOMY REVIEW ITEM]")
            rec_info = None
            if nxt.candidate_canonical_plant_id and nxt.candidate_canonical_plant_id in groups_by_id:
                grp = groups_by_id[nxt.candidate_canonical_plant_id]
                rec_info = {
                    "scientific_name": grp.scientific_name,
                    "recommendation": grp.review_recommendation,
                    "reason": grp.recommendation_reason,
                    "related_classes": [c for c in grp.original_class_names if c != nxt.original_class_name]
                }
            print_queue_item(nxt, recommendation_info=rec_info)
        else:
            print("\n[INFO] No pending review items found in queue.")

    if args.mapping_id and not args.interactive:
        m_item = queue.get_by_mapping_id(args.mapping_id)
        if m_item:
            print(f"\n[TAXONOMY REVIEW ITEM: {args.mapping_id}]")
            rec_info = None
            if m_item.candidate_canonical_plant_id and m_item.candidate_canonical_plant_id in groups_by_id:
                grp = groups_by_id[m_item.candidate_canonical_plant_id]
                rec_info = {
                    "scientific_name": grp.scientific_name,
                    "recommendation": grp.review_recommendation,
                    "reason": grp.recommendation_reason,
                    "related_classes": [c for c in grp.original_class_names if c != m_item.original_class_name]
                }
            print_queue_item(m_item, recommendation_info=rec_info)
        else:
            print(f"\n[ERROR] Mapping ID '{args.mapping_id}' not found.")

    if args.pending and not args.interactive:
        pending = queue.get_pending()
        if args.dataset:
            pending = [item for item in pending if item.source_dataset.lower() == args.dataset.lower()]
        if args.status:
            pending = [item for item in pending if item.current_mapping_status.lower() == args.status.lower()]
        if args.limit and args.limit > 0:
            pending = pending[:args.limit]
        print(f"\n[PENDING REVIEW ITEMS COUNT: {len(pending)} (limit={args.limit or 'none'})]")
        for item in pending:
            print(f" - [{item.source_dataset}] {item.mapping_id} | Class: '{item.original_class_name}' | Candidate: '{item.candidate_canonical_plant_id}' ({item.confidence})")

    if args.interactive:
        run_interactive_review(
            queue,
            session_mgr=session_mgr,
            session_id=args.session_id,
            reviewer_id=args.reviewer_id,
            resume_flag=args.resume,
            dataset_filter=args.dataset,
            status_filter=args.status,
            mapping_id_filter=args.mapping_id,
            candidate_group_filter=args.candidate_group,
            limit=args.limit or 10
        )

if __name__ == "__main__":
    main()
