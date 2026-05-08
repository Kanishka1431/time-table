"""
Greedy Constraint-Based Timetable Scheduler

Algorithm:
1. Build scheduling context from database data
2. Sort subjects by scheduling difficulty (higher frequency = harder)
3. For each class-section, assign subjects to slots greedily
4. Validate all hard constraints at each step
5. If conflicts remain (frequency shortfall), auto-add teachers and retry
6. Students get ZERO free periods — every slot is a subject
7. Return fully valid timetable or conflict report
"""
import random
import copy
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

from app.engine.models import (
    TeacherInfo, SubjectInfo, ClassSectionInfo, TeacherMappingInfo,
    SlotAssignment, TeacherLoad, ConflictItem, GenerationResult
)
from app.engine.constraints import (
    AssignmentGrid, TeacherSchedule, validate_slot
)
from app.config import NUM_DAYS, PERIODS_PER_DAY


class GreedyScheduler:
    """
    Greedy constraint-based timetable scheduler.
    Assigns subjects to time slots while respecting all hard constraints.
    Auto-adds teachers when constraints cannot be satisfied with existing staff.
    Students get zero free periods.
    """

    def __init__(
        self,
        teachers: List[TeacherInfo],
        subjects: List[SubjectInfo],
        class_sections: List[ClassSectionInfo],
        mappings: List[TeacherMappingInfo],
    ):
        self.original_teachers = list(teachers)
        self.original_mappings = list(mappings)
        self.subjects = {s.id: s for s in subjects}
        self.class_sections = {cs.id: cs for cs in class_sections}

        # Will be rebuilt on each attempt
        self.teachers: Dict[int, TeacherInfo] = {}
        self.mappings: List[TeacherMappingInfo] = []
        self.assignment_grid: AssignmentGrid = {}
        self.teacher_schedule: TeacherSchedule = defaultdict(set)
        self.teacher_loads: Dict[int, TeacherLoad] = {}
        self.conflicts: List[ConflictItem] = []

        # Auto-teacher tracking
        self.auto_teachers_added: List[dict] = []
        self._next_auto_id = -1  # Negative IDs for auto-created teachers

        # Build lookup structures
        self.subject_teacher_map: Dict[Tuple[int, int], List[int]] = defaultdict(list)

    def _rebuild_state(self):
        """Rebuild all teachers, mappings, and lookup structures from originals + auto-added."""
        all_teachers = list(self.original_teachers)
        all_mappings = list(self.original_mappings)

        # Add auto-teachers
        for at in self.auto_teachers_added:
            all_teachers.append(at["teacher_info"])
            all_mappings.extend(at["mappings"])

        self.teachers = {t.id: t for t in all_teachers}
        self.mappings = all_mappings
        self._build_mapping_index()

    def _reset(self):
        """Reset scheduling state for a new attempt."""
        self._rebuild_state()
        self.assignment_grid = {}
        self.teacher_schedule = defaultdict(set)
        self.teacher_loads = {t.id: TeacherLoad(teacher_id=t.id) for t in self.teachers.values()}
        self.conflicts = []

    def _build_mapping_index(self):
        """Build efficient lookup: (subject_id, class_number) -> list of teacher_ids."""
        self.subject_teacher_map = defaultdict(list)
        for m in self.mappings:
            for cls_num in range(m.class_range_start, m.class_range_end + 1):
                if m.teacher_id not in self.subject_teacher_map[(m.subject_id, cls_num)]:
                    self.subject_teacher_map[(m.subject_id, cls_num)].append(m.teacher_id)

    def _get_subjects_for_class(self, class_section: ClassSectionInfo) -> List[Tuple[SubjectInfo, int]]:
        """Get list of (subject, weekly_frequency) for a class section."""
        result = []
        for subj in self.subjects.values():
            if subj.class_group == class_section.class_group:
                result.append((subj, subj.weekly_frequency))
        random.shuffle(result)
        result.sort(key=lambda x: (
            -x[1],
            len(self.subject_teacher_map.get((x[0].id, class_section.class_number), []))
        ))
        return result

    def _find_available_teachers(
        self,
        subject_id: int,
        class_number: int,
        day_index: int,
        period: int,
    ) -> List[int]:
        """Find teachers who can teach this subject for this class at this time."""
        key = (subject_id, class_number)
        candidate_teachers = self.subject_teacher_map.get(key, [])

        available = []
        for tid in candidate_teachers:
            teacher = self.teachers[tid]
            from app.engine.constraints import check_teacher_clash, check_teacher_daily_limit, check_teacher_weekly_limit
            if (check_teacher_clash(tid, day_index, period, self.teacher_schedule) and
                check_teacher_daily_limit(tid, day_index, self.teacher_loads, teacher.max_periods_per_day) and
                check_teacher_weekly_limit(tid, self.teacher_loads, teacher.max_periods_per_week)):
                available.append(tid)

        return available

    def _get_free_slots(self, class_section_id: int) -> List[Tuple[int, int]]:
        """Get all unassigned (day, period) slots for a class section."""
        free = []
        for day in range(NUM_DAYS):
            for period in range(1, PERIODS_PER_DAY + 1):
                if (class_section_id, day, period) not in self.assignment_grid:
                    free.append((day, period))
        return free

    def _assign_slot(
        self,
        class_section_id: int,
        day_index: int,
        period: int,
        subject_id: int,
        teacher_id: int,
    ):
        """Record a slot assignment and update all tracking structures."""
        assignment = SlotAssignment(
            class_section_id=class_section_id,
            day_index=day_index,
            period=period,
            subject_id=subject_id,
            teacher_id=teacher_id,
            slot_type="class",
        )
        self.assignment_grid[(class_section_id, day_index, period)] = assignment
        self.teacher_schedule[teacher_id].add((day_index, period))
        self.teacher_loads[teacher_id].add_period(day_index)

    def _count_subject_on_day(
        self, class_section_id: int, subject_id: int, day_index: int
    ) -> int:
        """Count how many times a subject appears on a specific day for a class."""
        count = 0
        for period in range(1, PERIODS_PER_DAY + 1):
            key = (class_section_id, day_index, period)
            if key in self.assignment_grid and self.assignment_grid[key].subject_id == subject_id:
                count += 1
        return count

    def _count_total_on_day(self, class_section_id: int, day_index: int) -> int:
        """Count total assigned (non-free) slots on a day for a class."""
        count = 0
        for period in range(1, PERIODS_PER_DAY + 1):
            key = (class_section_id, day_index, period)
            if key in self.assignment_grid and self.assignment_grid[key].slot_type == "class":
                count += 1
        return count

    def _get_day_distribution_score(
        self, class_section_id: int, subject_id: int, day_index: int
    ) -> tuple:
        """
        Score a day for subject distribution. Lower = better.
        First priority: spread this subject across different days.
        Second priority: prefer days with fewer total assignments (balance load).
        """
        subject_count = self._count_subject_on_day(class_section_id, subject_id, day_index)
        total_count = self._count_total_on_day(class_section_id, day_index)
        return (subject_count, total_count)

    def _diagnose_conflicts(self) -> List[dict]:
        """
        Analyze current conflicts to determine which subject/class-range combos
        need more teacher capacity.
        Returns list of dicts: {subject_id, subject_name, class_group, class_numbers, shortfall}
        """
        bottlenecks = defaultdict(lambda: {"shortfall": 0, "class_numbers": set()})

        for conflict in self.conflicts:
            if conflict.conflict_type == "frequency":
                details = conflict.details
                subj_id = details.get("subject_id")
                cls_num = details.get("class_number")
                remaining = details.get("remaining", 0)
                subj = self.subjects.get(subj_id)
                if subj:
                    key = (subj_id, subj.class_group)
                    bottlenecks[key]["subject_id"] = subj_id
                    bottlenecks[key]["subject_name"] = subj.name
                    bottlenecks[key]["class_group"] = subj.class_group
                    bottlenecks[key]["shortfall"] += remaining
                    bottlenecks[key]["class_numbers"].add(cls_num)

        result = []
        for key, info in bottlenecks.items():
            info["class_numbers"] = sorted(info["class_numbers"])
            result.append(info)
        # Sort by shortfall descending — fix worst bottlenecks first
        result.sort(key=lambda x: -x["shortfall"])
        return result

    def _add_auto_teacher(self, subject_id: int, subject_name: str, class_group: str, class_numbers: List[int]):
        """
        Create a virtual teacher for the given subject and class range.
        Uses negative IDs to distinguish from real DB teachers.
        """
        teacher_id = self._next_auto_id
        self._next_auto_id -= 1

        # Determine class range
        range_start = min(class_numbers)
        range_end = max(class_numbers)

        group_label = "P" if class_group == "primary" else "H"
        auto_num = len(self.auto_teachers_added) + 1
        teacher_name = f"Auto-Teacher ({subject_name}-{group_label}) #{auto_num}"

        teacher_info = TeacherInfo(
            id=teacher_id,
            name=teacher_name,
            max_periods_per_day=6,
            max_periods_per_week=32,
        )

        mapping = TeacherMappingInfo(
            teacher_id=teacher_id,
            subject_id=subject_id,
            class_range_start=range_start,
            class_range_end=range_end,
        )

        auto_entry = {
            "teacher_info": teacher_info,
            "mappings": [mapping],
            "teacher_id": teacher_id,
            "teacher_name": teacher_name,
            "subject_id": subject_id,
            "subject_name": subject_name,
            "class_group": class_group,
            "class_range_start": range_start,
            "class_range_end": range_end,
        }
        self.auto_teachers_added.append(auto_entry)

    def _run_one_attempt(self) -> Tuple[int, int]:
        """
        Run one scheduling attempt.
        Returns (total_assigned, total_needed).
        """
        self._reset()
        total_assigned = 0
        total_needed = 0

        class_sections_list = list(self.class_sections.items())
        random.shuffle(class_sections_list)

        for cs_id, cs in class_sections_list:
            subjects_for_class = self._get_subjects_for_class(cs)
            total_needed += sum(freq for _, freq in subjects_for_class)
            remaining: Dict[int, int] = {subj.id: freq for subj, freq in subjects_for_class}

            # Multiple passes to try to assign all subjects
            for pass_num in range(4):
                if all(v <= 0 for v in remaining.values()):
                    break
                remaining_items = [(sid, rem) for sid, rem in remaining.items() if rem > 0]
                random.shuffle(remaining_items)
                remaining_items.sort(key=lambda x: -x[1])

                for subject_id, slots_needed in remaining_items:
                    if slots_needed <= 0:
                        continue
                    free_slots = self._get_free_slots(cs_id)
                    if not free_slots:
                        break
                    random.shuffle(free_slots)
                    free_slots.sort(key=lambda slot: (
                        self._get_day_distribution_score(cs_id, subject_id, slot[0]),
                        slot[0], slot[1]
                    ))

                    assigned_count = 0
                    for day_index, period in free_slots:
                        if assigned_count >= slots_needed:
                            break
                        available_teachers = self._find_available_teachers(
                            subject_id, cs.class_number, day_index, period
                        )
                        if not available_teachers:
                            continue
                        if self._count_subject_on_day(cs_id, subject_id, day_index) >= 2:
                            continue
                        available_teachers.sort(key=lambda tid: self.teacher_loads[tid].weekly_count)
                        self._assign_slot(cs_id, day_index, period, subject_id, available_teachers[0])
                        assigned_count += 1
                        total_assigned += 1
                    remaining[subject_id] = slots_needed - assigned_count

            # Record conflicts for unassigned subjects
            for subject_id, rem in remaining.items():
                if rem > 0:
                    subj = self.subjects[subject_id]
                    self.conflicts.append(ConflictItem(
                        conflict_type="frequency",
                        description=f"Could not satisfy frequency for {subj.name} in Class {cs.class_number}-{cs.section}: {rem} slots still needed",
                        details={
                            "class_section_id": cs_id,
                            "subject_id": subject_id,
                            "subject_name": subj.name,
                            "class_number": cs.class_number,
                            "section": cs.section,
                            "remaining": rem,
                        }
                    ))

            # NO free period filling — any unfilled slot stays empty and is a conflict
            unfilled = self._get_free_slots(cs_id)
            if unfilled:
                self.conflicts.append(ConflictItem(
                    conflict_type="no_slot",
                    description=f"Class {cs.class_number}-{cs.section} has {len(unfilled)} unfilled student slots",
                    details={
                        "class_section_id": cs_id,
                        "class_number": cs.class_number,
                        "section": cs.section,
                        "unfilled_count": len(unfilled),
                        "unfilled_slots": unfilled[:10],  # Cap for readability
                    }
                ))

        # Check teacher overload
        for tid, load in self.teacher_loads.items():
            teacher = self.teachers[tid]
            if load.weekly_count > teacher.max_periods_per_week:
                self.conflicts.append(ConflictItem(
                    conflict_type="overload",
                    description=f"Teacher {teacher.name} is overloaded: {load.weekly_count}/{teacher.max_periods_per_week} periods/week",
                    details={
                        "teacher_id": tid,
                        "teacher_name": teacher.name,
                        "weekly_count": load.weekly_count,
                        "max_per_week": teacher.max_periods_per_week,
                    }
                ))
            for day, count in load.daily_counts.items():
                if count > teacher.max_periods_per_day:
                    self.conflicts.append(ConflictItem(
                        conflict_type="overload",
                        description=f"Teacher {teacher.name} overloaded on day {day}: {count}/{teacher.max_periods_per_day} periods",
                        details={
                            "teacher_id": tid,
                            "teacher_name": teacher.name,
                            "day_index": day,
                            "daily_count": count,
                            "max_per_day": teacher.max_periods_per_day,
                        }
                    ))

        return total_assigned, total_needed

    def generate(self) -> GenerationResult:
        """
        Generate a complete timetable.
        Uses randomized restarts + auto-teacher addition to resolve conflicts.
        Students get zero free periods.
        """
        MAX_SCHEDULE_ATTEMPTS = 50       # Randomized restarts per teacher config
        MAX_AUTO_TEACHER_ROUNDS = 20     # Max rounds of adding teachers
        MAX_AUTO_TEACHERS_TOTAL = 50     # Max total auto-teachers to add

        best_result = None
        min_conflicts = float('inf')
        total_global_attempts = 0

        for auto_round in range(MAX_AUTO_TEACHER_ROUNDS + 1):
            # Try multiple random restarts with current teacher set
            for attempt in range(MAX_SCHEDULE_ATTEMPTS):
                total_global_attempts += 1
                total_assigned, total_needed = self._run_one_attempt()

                result = GenerationResult(
                    success=len(self.conflicts) == 0,
                    assignments=list(self.assignment_grid.values()),
                    conflicts=copy.deepcopy(self.conflicts),
                    stats={
                        "total_sections": len(self.class_sections),
                        "total_subjects_assigned": total_assigned,
                        "total_subjects_needed": total_needed,
                        "total_free_periods": 0,  # Always 0 — no free periods for students
                        "total_conflicts": len(self.conflicts),
                        "total_teachers_used": sum(1 for load in self.teacher_loads.values() if load.weekly_count > 0),
                        "total_teachers_available": len(self.teachers),
                        "auto_teachers_added": len(self.auto_teachers_added),
                        "auto_teacher_details": [
                            {"name": at["teacher_name"], "subject": at["subject_name"], "range": f"{at['class_range_start']}-{at['class_range_end']}"}
                            for at in self.auto_teachers_added
                        ],
                        "attempts": total_global_attempts,
                        "auto_rounds": auto_round,
                    }
                )

                if result.success:
                    return result

                if len(self.conflicts) < min_conflicts:
                    min_conflicts = len(self.conflicts)
                    best_result = result

            # If we've exhausted restarts and still have conflicts, diagnose and add teachers
            if len(self.auto_teachers_added) >= MAX_AUTO_TEACHERS_TOTAL:
                break  # Safety limit

            bottlenecks = self._diagnose_conflicts()
            if not bottlenecks:
                break  # No frequency-type conflicts to fix

            # Add one auto-teacher for the worst bottleneck
            worst = bottlenecks[0]
            self._add_auto_teacher(
                subject_id=worst["subject_id"],
                subject_name=worst["subject_name"],
                class_group=worst["class_group"],
                class_numbers=worst["class_numbers"],
            )

        return best_result