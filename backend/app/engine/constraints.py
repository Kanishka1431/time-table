"""
Hard constraint validators for the scheduling engine.
Each function checks one specific constraint and returns True if the constraint is satisfied.
"""
from typing import Dict, Tuple, Set, Optional
from app.engine.models import SlotAssignment, TeacherLoad


# Type alias for the assignment grid: (class_section_id, day_index, period) -> SlotAssignment
AssignmentGrid = Dict[Tuple[int, int, int], SlotAssignment]

# Type alias for teacher schedule: teacher_id -> set of (day_index, period) tuples
TeacherSchedule = Dict[int, Set[Tuple[int, int]]]


def check_teacher_clash(
    teacher_id: int,
    day_index: int,
    period: int,
    teacher_schedule: TeacherSchedule
) -> bool:
    """
    Check if a teacher is already assigned to another section at this time.
    Returns True if NO clash (constraint satisfied).
    """
    if teacher_id not in teacher_schedule:
        return True
    return (day_index, period) not in teacher_schedule[teacher_id]


def check_section_clash(
    class_section_id: int,
    day_index: int,
    period: int,
    assignment_grid: AssignmentGrid
) -> bool:
    """
    Check if this section already has a subject assigned at this time.
    Returns True if NO clash (constraint satisfied).
    """
    return (class_section_id, day_index, period) not in assignment_grid


def check_teacher_daily_limit(
    teacher_id: int,
    day_index: int,
    teacher_loads: Dict[int, TeacherLoad],
    max_per_day: int
) -> bool:
    """
    Check if teacher has not exceeded their daily period limit.
    Returns True if limit NOT exceeded.
    """
    if teacher_id not in teacher_loads:
        return True
    return teacher_loads[teacher_id].can_teach_on_day(day_index, max_per_day)


def check_teacher_weekly_limit(
    teacher_id: int,
    teacher_loads: Dict[int, TeacherLoad],
    max_per_week: int
) -> bool:
    """
    Check if teacher has not exceeded their weekly period limit.
    Returns True if limit NOT exceeded.
    """
    if teacher_id not in teacher_loads:
        return True
    return teacher_loads[teacher_id].can_teach_this_week(max_per_week)


def check_subject_daily_limit(
    class_section_id: int,
    subject_id: int,
    day_index: int,
    assignment_grid: AssignmentGrid,
    max_per_day: int = 2
) -> bool:
    """
    Soft constraint: Limit same subject to max_per_day periods on a single day.
    Returns True if limit NOT exceeded.
    """
    count = 0
    for (cs_id, d, p), assignment in assignment_grid.items():
        if cs_id == class_section_id and d == day_index and assignment.subject_id == subject_id:
            count += 1
    return count < max_per_day


def validate_slot(
    teacher_id: int,
    class_section_id: int,
    day_index: int,
    period: int,
    subject_id: int,
    assignment_grid: AssignmentGrid,
    teacher_schedule: TeacherSchedule,
    teacher_loads: Dict[int, TeacherLoad],
    max_per_day: int,
    max_per_week: int,
) -> Tuple[bool, Optional[str]]:
    """
    Validate ALL hard constraints for a potential slot assignment.
    Returns (is_valid, violation_reason).
    """
    if not check_teacher_clash(teacher_id, day_index, period, teacher_schedule):
        return False, f"Teacher clash: teacher {teacher_id} already busy at day {day_index}, period {period}"

    if not check_section_clash(class_section_id, day_index, period, assignment_grid):
        return False, f"Section clash: class {class_section_id} already has a subject at day {day_index}, period {period}"

    if not check_teacher_daily_limit(teacher_id, day_index, teacher_loads, max_per_day):
        return False, f"Teacher {teacher_id} exceeds daily limit of {max_per_day} on day {day_index}"

    if not check_teacher_weekly_limit(teacher_id, teacher_loads, max_per_week):
        return False, f"Teacher {teacher_id} exceeds weekly limit of {max_per_week}"

    # Soft: try not to assign same subject more than twice per day per section
    if not check_subject_daily_limit(class_section_id, subject_id, day_index, assignment_grid, max_per_day=2):
        return False, f"Subject {subject_id} already appears twice on day {day_index} for class {class_section_id}"

    return True, None
