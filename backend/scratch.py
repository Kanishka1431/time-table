import re
with open('c:/Users/Kanishka/OneDrive/Desktop/timetable/backend/app/engine/scheduler.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add import copy
if 'import copy' not in code:
    code = code.replace('import random', 'import random\nimport copy')

# Replace _get_subjects_for_class
code = re.sub(
    r'    def _get_subjects_for_class.*?return result',
    '''    def _get_subjects_for_class(self, class_section: ClassSectionInfo) -> List[Tuple[SubjectInfo, int]]:
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
        return result''',
    code,
    flags=re.DOTALL
)

# Replace generate method with randomized version
new_generate = '''    def _reset(self):
        self.assignment_grid = {}
        self.teacher_schedule = defaultdict(set)
        self.teacher_loads = {t.id: TeacherLoad(teacher_id=t.id) for t in self.teachers.values()}
        self.conflicts = []

    def generate(self) -> GenerationResult:
        MAX_ATTEMPTS = 50
        best_result = None
        min_conflicts = float('inf')

        for attempt in range(MAX_ATTEMPTS):
            self._reset()
            total_assigned = 0
            total_needed = 0
            total_free_filled = 0

            class_sections_list = list(self.class_sections.items())
            random.shuffle(class_sections_list)

            for cs_id, cs in class_sections_list:
                subjects_for_class = self._get_subjects_for_class(cs)
                total_needed += sum(freq for _, freq in subjects_for_class)
                remaining: Dict[int, int] = {subj.id: freq for subj, freq in subjects_for_class}

                for pass_num in range(3):
                    if all(v <= 0 for v in remaining.values()): break
                    remaining_items = [(sid, rem) for sid, rem in remaining.items() if rem > 0]
                    random.shuffle(remaining_items)
                    remaining_items.sort(key=lambda x: -x[1])

                    for subject_id, slots_needed in remaining_items:
                        if slots_needed <= 0: continue
                        free_slots = self._get_free_slots(cs_id)
                        if not free_slots: break
                        random.shuffle(free_slots)
                        free_slots.sort(key=lambda slot: (
                            self._get_day_distribution_score(cs_id, subject_id, slot[0]),
                            slot[0], slot[1]
                        ))

                        assigned_count = 0
                        for day_index, period in free_slots:
                            if assigned_count >= slots_needed: break
                            available_teachers = self._find_available_teachers(
                                subject_id, cs.class_number, day_index, period
                            )
                            if not available_teachers: continue
                            if self._count_subject_on_day(cs_id, subject_id, day_index) >= 2: continue
                            available_teachers.sort(key=lambda tid: self.teacher_loads[tid].weekly_count)
                            self._assign_slot(cs_id, day_index, period, subject_id, available_teachers[0])
                            assigned_count += 1
                            total_assigned += 1
                        remaining[subject_id] = slots_needed - assigned_count

                for subject_id, rem in remaining.items():
                    if rem > 0:
                        subj = self.subjects[subject_id]
                        self.conflicts.append(ConflictItem(
                            conflict_type="frequency",
                            description=f"Could not satisfy frequency for {subj.name} in Class {cs.class_number}-{cs.section}: {rem} slots still needed",
                            details={"class_section_id": cs_id, "subject_id": subject_id, "subject_name": subj.name, "class_number": cs.class_number, "section": cs.section, "remaining": rem}
                        ))

                for day_index, period in self._get_free_slots(cs_id):
                    self.assignment_grid[(cs_id, day_index, period)] = SlotAssignment(
                        class_section_id=cs_id, day_index=day_index, period=period,
                        subject_id=None, teacher_id=None, slot_type="free"
                    )
                    total_free_filled += 1

            for tid, load in self.teacher_loads.items():
                teacher = self.teachers[tid]
                if load.weekly_count > teacher.max_periods_per_week:
                    self.conflicts.append(ConflictItem(
                        conflict_type="overload",
                        description=f"Teacher {teacher.name} is overloaded: {load.weekly_count}/{teacher.max_periods_per_week} periods/week",
                        details={"teacher_id": tid, "teacher_name": teacher.name, "weekly_count": load.weekly_count, "max_per_week": teacher.max_periods_per_week}
                    ))
                for day, count in load.daily_counts.items():
                    if count > teacher.max_periods_per_day:
                        self.conflicts.append(ConflictItem(
                            conflict_type="overload",
                            description=f"Teacher {teacher.name} overloaded on day {day}: {count}/{teacher.max_periods_per_day} periods",
                            details={"teacher_id": tid, "teacher_name": teacher.name, "day_index": day, "daily_count": count, "max_per_day": teacher.max_periods_per_day}
                        ))

            result = GenerationResult(
                success=len(self.conflicts) == 0,
                assignments=list(self.assignment_grid.values()),
                conflicts=copy.deepcopy(self.conflicts),
                stats={
                    "total_sections": len(self.class_sections),
                    "total_subjects_assigned": total_assigned,
                    "total_subjects_needed": total_needed,
                    "total_free_periods": total_free_filled,
                    "total_conflicts": len(self.conflicts),
                    "total_teachers_used": sum(1 for load in self.teacher_loads.values() if load.weekly_count > 0),
                    "attempts": attempt + 1
                }
            )

            if result.success:
                return result
            if len(self.conflicts) < min_conflicts:
                min_conflicts = len(self.conflicts)
                best_result = result

        return best_result'''

code = re.sub(
    r'    def generate\(self\) -> GenerationResult:.*',
    new_generate,
    code,
    flags=re.DOTALL
)

with open('c:/Users/Kanishka/OneDrive/Desktop/timetable/backend/app/engine/scheduler.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Done!')
