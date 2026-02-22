"""
study_module.py – Study tools for STARK.

Provides timetable generation, exam reminders, and to-do lists for exam
preparation.
"""

import datetime


class StudyModule:
    """Static helpers for study and exam preparation."""

    @staticmethod
    def create_timetable(syllabus: str, exam_date_str: str):
        """
        Build a day-by-day study timetable from *syllabus* to *exam_date_str*.

        Parameters
        ----------
        syllabus:
            Comma-separated list of topics to study.
        exam_date_str:
            Target exam date in ``YYYY-MM-DD`` format.

        Returns
        -------
        dict
            Keys: ``timetable`` (date -> plan dict), ``topics`` (list),
            ``summary`` (human-readable string).
        str
            Error message if the date is invalid or already past.
        """
        try:
            exam_date = datetime.datetime.strptime(exam_date_str, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format, Sir. Please use YYYY-MM-DD."

        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_remaining = (exam_date - today).days

        if days_remaining <= 0:
            return "The exam date has already passed, Sir. Please enter a future date."

        topics = [t.strip() for t in syllabus.split(",") if t.strip()]
        if not topics:
            return "No topics provided, Sir. Please give a comma-separated syllabus."

        topics_per_day = max(1, len(topics) // days_remaining)
        timetable = {}
        topic_idx = 0

        for day_num in range(days_remaining):
            date_key = (today + datetime.timedelta(days=day_num)).strftime("%Y-%m-%d")
            revision_start_day = days_remaining - max(1, days_remaining // 5)
            is_revision = day_num >= revision_start_day

            daily_topics = []
            if is_revision:
                # Revision day: rotate through all topics from the beginning
                revision_day_idx = day_num - revision_start_day
                start = (revision_day_idx * topics_per_day) % len(topics)
                daily_topics = topics[start:start + topics_per_day]
                if not daily_topics:
                    daily_topics = topics[:topics_per_day]
            else:
                for _ in range(topics_per_day):
                    if topic_idx < len(topics):
                        daily_topics.append(topics[topic_idx])
                        topic_idx += 1

            timetable[date_key] = {
                "topics": daily_topics,
                "study_hours": "2-3 hours",
                "revision": is_revision,
            }

        # Build summary (show all days)
        lines = [
            f"Study timetable created - {days_remaining} days until exam on {exam_date_str}",
            f"Total topics: {len(topics)}",
            "",
        ]
        for date_key, plan in timetable.items():
            tag = " [REVISION]" if plan["revision"] else ""
            lines.append(f"{date_key}: {', '.join(plan['topics'])}{tag}")

        summary = "\n".join(lines)

        return {
            "timetable": timetable,
            "topics": topics,
            "summary": summary,
        }

    @staticmethod
    def days_until_exam(exam_date_str: str) -> int:
        """Return the number of days until the exam date, or -1 if invalid/past."""
        try:
            exam_date = datetime.datetime.strptime(exam_date_str, "%Y-%m-%d")
            return max(0, (exam_date - datetime.datetime.now()).days)
        except ValueError:
            return -1
