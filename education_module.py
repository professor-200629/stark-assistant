# Education Module

import random
from datetime import datetime, timedelta


class EducationModule:
    """Handles education Q&A, MCQ generation, exam timetabling, and reminders."""

    def __init__(self):
        self.syllabus = {}   # {subject: {topics, exam_date, covered}}
        self.todo_list = []

    # ------------------------------------------------------------------
    # Syllabus management
    # ------------------------------------------------------------------

    def add_syllabus(self, subject, topics, exam_date):
        """Register topics and exam date for a subject.

        ``exam_date`` can be a ``datetime.date`` object or a string 'YYYY-MM-DD'.
        """
        if isinstance(exam_date, str):
            exam_date = datetime.strptime(exam_date, "%Y-%m-%d").date()
        self.syllabus[subject] = {
            'topics': list(topics),
            'exam_date': exam_date,
            'covered': [],
        }
        return f"Syllabus for {subject} added successfully, Sir."

    def mark_topic_covered(self, subject, topic):
        """Mark a topic as covered so it is excluded from to-do lists."""
        if subject not in self.syllabus:
            return f"Subject '{subject}' not found, Sir."
        if topic not in self.syllabus[subject]['topics']:
            return f"Topic '{topic}' not found under {subject}, Sir."
        if topic not in self.syllabus[subject]['covered']:
            self.syllabus[subject]['covered'].append(topic)
        return f"Topic '{topic}' marked as covered for {subject}, Sir."

    # ------------------------------------------------------------------
    # Exam timetable
    # ------------------------------------------------------------------

    def create_exam_timetable(self):
        """Build a day-by-day study plan from today until each exam.

        Returns a dict keyed by date string ('YYYY-MM-DD'), with a list of
        ``{subject, topics}`` dicts for that day.
        """
        if not self.syllabus:
            return "No syllabus found. Please add subjects first, Sir."

        timetable = {}
        today = datetime.now().date()

        for subject, data in self.syllabus.items():
            exam_date = data['exam_date']
            topics = [t for t in data['topics'] if t not in data.get('covered', [])]
            days_left = (exam_date - today).days
            if days_left <= 0 or not topics:
                continue
            # Ceiling division so no topics are left unscheduled
            topics_per_day = (len(topics) + days_left - 1) // days_left
            for day_offset in range(days_left):
                date_key = str(today + timedelta(days=day_offset))
                start = day_offset * topics_per_day
                end = start + topics_per_day
                day_topics = topics[start:end]
                if not day_topics:
                    continue
                if date_key not in timetable:
                    timetable[date_key] = []
                timetable[date_key].append({
                    'subject': subject,
                    'topics': day_topics,
                })
        return timetable

    # ------------------------------------------------------------------
    # To-do list
    # ------------------------------------------------------------------

    def create_todo_list(self, subject=None):
        """Return a to-do list of uncovered topics.

        If ``subject`` is given, only that subject's topics are listed.
        """
        if subject:
            data = self.syllabus.get(subject)
            if not data:
                return f"Subject '{subject}' not found, Sir."
            topics = data['topics']
            covered = data.get('covered', [])
        else:
            topics = [t for d in self.syllabus.values() for t in d['topics']]
            covered = [t for d in self.syllabus.values() for t in d.get('covered', [])]

        todo = [{'topic': t, 'done': t in covered} for t in topics]
        self.todo_list = todo
        return todo

    # ------------------------------------------------------------------
    # Exam reminders
    # ------------------------------------------------------------------

    def get_exam_reminders(self):
        """Return reminders for exams within the next 30 days."""
        reminders = []
        today = datetime.now().date()
        for subject, data in self.syllabus.items():
            days_left = (data['exam_date'] - today).days
            if 0 < days_left <= 30:
                uncovered = [
                    t for t in data['topics']
                    if t not in data.get('covered', [])
                ]
                reminders.append({
                    'subject': subject,
                    'exam_date': str(data['exam_date']),
                    'days_left': days_left,
                    'topics_remaining': uncovered,
                })
        return reminders

    # ------------------------------------------------------------------
    # MCQ generation
    # ------------------------------------------------------------------

    def generate_mcq(self, topic, count=5):
        """Generate multiple-choice question stubs for a topic.

        In a production deployment the question bodies would be filled by
        an AI API (e.g. OpenAI / Gemini).  These stubs provide the correct
        structure so callers can extend them seamlessly.
        """
        if count < 1:
            raise ValueError("count must be at least 1")
        mcqs = []
        for i in range(1, count + 1):
            mcqs.append({
                'question_number': i,
                'topic': topic,
                'question': f"Q{i}. [Topic: {topic}] — Question {i} about {topic}?",
                'options': {
                    'A': f"Option A for Q{i}",
                    'B': f"Option B for Q{i}",
                    'C': f"Option C for Q{i}",
                    'D': f"Option D for Q{i}",
                },
                'answer': random.choice(['A', 'B', 'C', 'D']),
            })
        return mcqs

    # ------------------------------------------------------------------
    # Education Q&A
    # ------------------------------------------------------------------

    def answer_question(self, question, subject=None):
        """Answer an educational question.

        When an AI API key is configured (OPENAI_API_KEY / GEMINI_API_KEY)
        this method can be extended to call the API.  The stub returns a
        structured response so callers know what shape to expect.
        """
        return {
            'subject': subject or "General",
            'question': question,
            'answer': (
                f"Certainly, Sir! Here is the explanation for your question "
                f"about '{question}':\n"
                f"[Connect an AI API such as OpenAI or Gemini via OPENAI_API_KEY "
                f"or GEMINI_API_KEY in .env to receive a full answer.]"
            ),
        }
