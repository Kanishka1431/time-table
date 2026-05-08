"""
Seed service: generates sample data for the school timetable system.
Creates classes, sections, subjects, teachers, and teacher-subject mappings.
Teacher counts are scaled to handle 48 periods/week/section with zero free periods.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.teacher import Teacher
from app.models.subject import Subject
from app.models.class_section import ClassSection
from app.models.mapping import TeacherSubjectMapping
from app.models.constraint import Constraint
from app.config import (
    CLASS_RANGE, SECTIONS, PRIMARY_CLASSES, HIGHER_CLASSES,
    PRIMARY_SUBJECTS, HIGHER_SUBJECTS,
    DEFAULT_MAX_PERIODS_PER_DAY, DEFAULT_MAX_PERIODS_PER_WEEK,
)


async def seed_database(db: AsyncSession) -> dict:
    """Seed database with complete school data. Returns summary."""
    summary = {}

    # ──────────────────────────────────────────
    # 1. Create Class Sections (50 total)
    # ──────────────────────────────────────────
    existing = await db.scalar(select(func.count(ClassSection.id)))
    if existing == 0:
        sections_created = 0
        for cls_num in CLASS_RANGE:
            group = "primary" if cls_num in PRIMARY_CLASSES else "higher"
            for sec in SECTIONS:
                db.add(ClassSection(
                    class_number=cls_num,
                    section=sec,
                    class_group=group,
                ))
                sections_created += 1
        await db.flush()
        summary["class_sections"] = sections_created
    else:
        summary["class_sections"] = f"Already exists ({existing})"

    # ──────────────────────────────────────────
    # 2. Create Subjects
    # ──────────────────────────────────────────
    existing = await db.scalar(select(func.count(Subject.id)))
    if existing == 0:
        subjects_created = 0
        for name, freq in PRIMARY_SUBJECTS.items():
            db.add(Subject(
                name=name,
                code=f"PRI_{name.upper()[:3]}",
                class_group="primary",
                weekly_frequency=freq,
            ))
            subjects_created += 1
        for name, freq in HIGHER_SUBJECTS.items():
            db.add(Subject(
                name=name,
                code=f"HIG_{name.upper()[:3]}",
                class_group="higher",
                weekly_frequency=freq,
            ))
            subjects_created += 1
        await db.flush()
        summary["subjects"] = subjects_created
    else:
        summary["subjects"] = f"Already exists ({existing})"

    # ──────────────────────────────────────────
    # 3. Create Teachers (scaled for 48 periods/week)
    # ──────────────────────────────────────────
    existing = await db.scalar(select(func.count(Teacher.id)))
    if existing == 0:
        # Teacher distribution — more teachers per subject to handle higher frequencies
        # Each teacher can do max 32/week across all sections
        # For 5 sections per class and 8 periods/week for English:
        #   5 sections × 8 = 40 periods needed per class-range chunk
        #   Need at least ceil(40/32) = 2 teachers per small range, more for wider ranges
        teacher_defs = [
            # ═══════════════════════════════════════
            # PRIMARY SUBJECTS (Classes 1-5)
            # ═══════════════════════════════════════

            # English (8/week × 5 sections × 5 classes = 200 needed)
            ("English", "primary", [
                ("Mrs. Sharma", 1, 2), ("Mrs. Verma", 1, 2),
                ("Mrs. Gupta", 2, 3), ("Mrs. Joshi", 3, 4),
                ("Mrs. Kapoor", 3, 4), ("Mrs. Batra", 4, 5),
                ("Mrs. Anand", 4, 5), ("Mrs. Tomar", 1, 3),
            ]),

            # Math (8/week × 5 sections × 5 classes = 200 needed)
            ("Math", "primary", [
                ("Mr. Kumar", 1, 2), ("Mr. Singh", 1, 2),
                ("Mr. Rao", 2, 3), ("Mr. Mehta", 3, 4),
                ("Mr. Pillai", 3, 4), ("Mr. Mathur", 4, 5),
                ("Mr. Arjun", 4, 5), ("Mr. Devraj", 1, 3),
            ]),

            # EVS (8/week × 5 sections × 5 classes = 200 needed)
            ("EVS", "primary", [
                ("Mrs. Iyer", 1, 2), ("Mrs. Nair", 1, 2),
                ("Mrs. Das", 2, 3), ("Mrs. Sen", 3, 4),
                ("Mrs. Lakshmi", 3, 4), ("Mrs. Saini", 4, 5),
                ("Mrs. Rathi", 4, 5), ("Mrs. Devi", 1, 3),
            ]),

            # GK (5/week × 5 sections × 5 classes = 125 needed)
            ("GK", "primary", [
                ("Mrs. Bose", 1, 3), ("Mrs. Reddy", 1, 3),
                ("Mrs. Chawla", 3, 5), ("Mrs. Grover", 3, 5),
                ("Mrs. Bajaj", 1, 5),
            ]),

            # Computer (5/week × 5 sections × 5 classes = 125 needed)
            ("Computer", "primary", [
                ("Mr. Tiwari", 1, 3), ("Mr. Saxena", 1, 3),
                ("Mr. Goyal", 3, 5), ("Mr. Jha", 3, 5),
                ("Mr. Suri", 1, 5),
            ]),

            # PT (5/week × 5 sections × 5 classes = 125 needed)
            ("PT", "primary", [
                ("Mr. Yadav", 1, 3), ("Mr. Chauhan", 1, 3),
                ("Mr. Patel_P", 3, 5), ("Mr. Chand", 3, 5),
                ("Mr. Ravi", 1, 5),
            ]),

            # Language (7/week × 5 sections × 5 classes = 175 needed)
            ("Language", "primary", [
                ("Mrs. Khan", 1, 2), ("Mrs. Mishra", 1, 2),
                ("Mrs. Pandey", 2, 3), ("Mrs. Dubey", 3, 4),
                ("Mrs. Neha", 3, 4), ("Mrs. Seema", 4, 5),
                ("Mrs. Priya", 4, 5),
            ]),

            # Art (2/week × 5 sections × 5 classes = 50 needed)
            ("Art", "primary", [
                ("Mrs. Meera_P", 1, 3), ("Mrs. Kala_P", 3, 5),
            ]),

            # ═══════════════════════════════════════
            # HIGHER SUBJECTS (Classes 6-10)
            # ═══════════════════════════════════════

            # English (8/week × 5 sections × 5 classes = 200 needed)
            ("English", "higher", [
                ("Mrs. Sinha", 6, 7), ("Mrs. Chatterjee", 6, 7),
                ("Mrs. Mukherjee", 7, 8), ("Mrs. Banerjee", 8, 9),
                ("Mrs. Ghosh", 8, 9), ("Mrs. Roy", 9, 10),
                ("Mrs. Dutta", 9, 10), ("Mrs. Sarkar", 6, 8),
            ]),

            # Math (8/week × 5 sections × 5 classes = 200 needed)
            ("Math", "higher", [
                ("Mr. Agarwal", 6, 7), ("Mr. Bhat", 6, 7),
                ("Mr. Desai", 7, 8), ("Mr. Jain", 8, 9),
                ("Mr. Chopra", 8, 9), ("Mr. Tandon", 9, 10),
                ("Mr. Kapil", 9, 10), ("Mr. Vyas", 6, 8),
            ]),

            # Science (7/week × 5 sections × 5 classes = 175 needed)
            ("Science", "higher", [
                ("Mrs. Kulkarni", 6, 7), ("Mrs. Patil", 6, 7),
                ("Mr. Hegde", 7, 8), ("Mr. Shetty", 8, 9),
                ("Mrs. Menon", 8, 9), ("Mr. Nambiar", 9, 10),
                ("Mrs. Kamath", 9, 10),
            ]),

            # Social (6/week × 5 sections × 5 classes = 150 needed)
            ("Social", "higher", [
                ("Mr. Rathore", 6, 7), ("Mr. Rajput", 6, 7),
                ("Mrs. Malik", 7, 8), ("Mrs. Sethi", 8, 9),
                ("Mr. Chahal", 8, 9), ("Mrs. Narayan", 9, 10),
                ("Mr. Shukla", 9, 10),
            ]),

            # Computer (5/week × 5 sections × 5 classes = 125 needed)
            ("Computer", "higher", [
                ("Mr. Patel_H", 6, 7), ("Mr. Naidu", 6, 7),
                ("Mr. Venkat", 7, 8), ("Mr. Mohan", 8, 9),
                ("Mr. Ashok", 9, 10),
            ]),

            # PT (5/week × 5 sections × 5 classes = 125 needed)
            ("PT", "higher", [
                ("Mr. Thakur", 6, 8), ("Mr. Rawat", 6, 8),
                ("Mr. Bhatt", 8, 10), ("Mr. Parmar", 8, 10),
            ]),

            # Language (7/week × 5 sections × 5 classes = 175 needed)
            ("Language", "higher", [
                ("Mrs. Kaur", 6, 7), ("Mrs. Gill", 6, 7),
                ("Mrs. Arora", 7, 8), ("Mrs. Dhawan", 8, 9),
                ("Mrs. Randhawa", 8, 9), ("Mrs. Sandhu", 9, 10),
                ("Mrs. Kohli", 9, 10),
            ]),

            # Art (2/week × 5 sections × 5 classes = 50 needed)
            ("Art", "higher", [
                ("Mrs. Meera_H", 6, 8), ("Mrs. Kala_H", 8, 10),
            ]),
        ]

        teachers_created = 0
        mappings_created = 0
        teacher_id_map = {}  # name -> id

        for subject_name, class_group, teachers in teacher_defs:
            # Find the subject
            subj_result = await db.execute(
                select(Subject).where(
                    Subject.name == subject_name,
                    Subject.class_group == class_group
                )
            )
            subject = subj_result.scalar_one_or_none()
            if not subject:
                continue

            for teacher_name, range_start, range_end in teachers:
                # Check if teacher already created (avoid duplicates for PT teachers etc.)
                if teacher_name not in teacher_id_map:
                    display_name = (teacher_name
                        .replace("_P", " (Primary)")
                        .replace("_H", " (Higher)"))
                    teacher = Teacher(
                        name=display_name,
                        email=f"{teacher_name.lower().replace(' ', '').replace('.', '')}@school.edu",
                        max_periods_per_day=DEFAULT_MAX_PERIODS_PER_DAY,
                        max_periods_per_week=DEFAULT_MAX_PERIODS_PER_WEEK,
                    )
                    db.add(teacher)
                    await db.flush()
                    teacher_id_map[teacher_name] = teacher.id
                    teachers_created += 1

                # Create mapping
                db.add(TeacherSubjectMapping(
                    teacher_id=teacher_id_map[teacher_name],
                    subject_id=subject.id,
                    class_range_start=range_start,
                    class_range_end=range_end,
                ))
                mappings_created += 1

        await db.flush()
        summary["teachers"] = teachers_created
        summary["mappings"] = mappings_created
    else:
        summary["teachers"] = f"Already exists ({existing})"

    # ──────────────────────────────────────────
    # 4. Create Default Constraints
    # ──────────────────────────────────────────
    existing = await db.scalar(select(func.count(Constraint.id)))
    if existing == 0:
        default_constraints = [
            Constraint(
                name="No Teacher Clash",
                constraint_type="hard",
                description="A teacher cannot teach two sections simultaneously.",
                parameters={"type": "teacher_clash"},
                is_active=True,
            ),
            Constraint(
                name="No Section Clash",
                constraint_type="hard",
                description="A section cannot have two subjects simultaneously.",
                parameters={"type": "section_clash"},
                is_active=True,
            ),
            Constraint(
                name="Weekly Subject Frequency",
                constraint_type="hard",
                description="Weekly subject frequency must be satisfied for each class.",
                parameters={"type": "frequency"},
                is_active=True,
            ),
            Constraint(
                name="Teacher Mapping Only",
                constraint_type="hard",
                description="Only mapped teachers can teach subjects.",
                parameters={"type": "mapping"},
                is_active=True,
            ),
            Constraint(
                name="Teacher Workload Limit",
                constraint_type="hard",
                description="Teacher workload limits must be respected (max 6/day, 32/week).",
                parameters={"type": "workload", "max_per_day": 6, "max_per_week": 32},
                is_active=True,
            ),
            Constraint(
                name="No Scheduling During Breaks",
                constraint_type="hard",
                description="No scheduling during break periods.",
                parameters={"type": "break"},
                is_active=True,
            ),
            Constraint(
                name="Complete Assignment",
                constraint_type="hard",
                description="Every class must have valid assignments for all periods — zero free periods for students.",
                parameters={"type": "complete"},
                is_active=True,
            ),
            # Soft constraints (future)
            Constraint(
                name="Balanced Workload",
                constraint_type="soft",
                description="Balance teacher workloads evenly across days.",
                parameters={"type": "balance"},
                is_active=False,
            ),
            Constraint(
                name="Subject Distribution",
                constraint_type="soft",
                description="Distribute subjects evenly across the week.",
                parameters={"type": "distribution"},
                is_active=False,
            ),
        ]
        for c in default_constraints:
            db.add(c)
        await db.flush()
        summary["constraints"] = len(default_constraints)
    else:
        summary["constraints"] = f"Already exists ({existing})"

    await db.commit()
    return summary
