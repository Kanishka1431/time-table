"""
Conflict reporter: generates structured conflict reports from scheduling results.
"""
from typing import List, Dict, Any
from app.engine.models import ConflictItem


def generate_conflict_report(
    schedule_id: int,
    conflicts: List[ConflictItem],
) -> Dict[str, Any]:
    """
    Generate a structured conflict report from a list of conflicts.
    Groups conflicts by type for easier display.
    """
    teacher_clashes = []
    section_clashes = []
    unsatisfied_frequencies = []
    overloaded_teachers = []
    unavailable_slots = []

    for conflict in conflicts:
        entry = {
            "description": conflict.description,
            **conflict.details,
        }
        if conflict.conflict_type == "teacher_clash":
            teacher_clashes.append(entry)
        elif conflict.conflict_type == "section_clash":
            section_clashes.append(entry)
        elif conflict.conflict_type == "frequency":
            unsatisfied_frequencies.append(entry)
        elif conflict.conflict_type == "overload":
            overloaded_teachers.append(entry)
        elif conflict.conflict_type == "no_slot":
            unavailable_slots.append(entry)
        else:
            unavailable_slots.append(entry)

    total = len(conflicts)

    return {
        "schedule_id": schedule_id,
        "has_conflicts": total > 0,
        "total_conflicts": total,
        "teacher_clashes": teacher_clashes,
        "section_clashes": section_clashes,
        "unsatisfied_frequencies": unsatisfied_frequencies,
        "overloaded_teachers": overloaded_teachers,
        "unavailable_slots": unavailable_slots,
    }
