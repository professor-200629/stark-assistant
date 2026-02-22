import unittest
from datetime import date, timedelta

from task_manager import TaskManager
from communication_module import CommunicationManager
from memory import MemoryManager
from education_module import EducationModule
from system_control import SystemControl


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()

    def test_task_creation(self):
        result = self.manager.add_task("Write report", "user_001")
        self.assertIn("added successfully", result)
        self.assertEqual(len(self.manager.tasks), 1)

    def test_task_failure_handling(self):
        result = self.manager.complete_task(999)
        self.assertIn("not found", result)

    def test_list_tasks_empty(self):
        result = self.manager.list_tasks("user_001")
        self.assertIn("no pending tasks", result)

    def test_delete_task(self):
        self.manager.add_task("Temp task", "user_001")
        task_id = self.manager.tasks[0]['id']
        result = self.manager.delete_task(task_id)
        self.assertIn("deleted", result)
        self.assertEqual(len(self.manager.tasks), 0)


class TestCommunication(unittest.TestCase):
    def setUp(self):
        self.comm = CommunicationManager(owner_name="balu")

    def test_send_message(self):
        result = self.comm.send_message("Alice", "Hello!", sender_id="user_001")
        self.assertIn("sent", result.lower())

    def test_receive_message(self):
        self.comm.send_message("Alice", "Hello!", sender_id="user_001")
        messages = self.comm.get_messages("user_001")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['recipient'], "Alice")

    def test_busy_message_content(self):
        msg = self.comm.get_busy_message()
        self.assertIn("busy", msg.lower())
        self.assertIn("STARK", msg)
        self.assertIn("Balu", msg)

    def test_send_notification(self):
        result = self.comm.send_notification("Test alert", "user_001")
        self.assertIn("Notification", result)
        notifications = self.comm.get_notifications("user_001")
        self.assertEqual(len(notifications), 1)


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryManager()

    def test_memory_storage(self):
        result = self.memory.store_information("favorite_color", "blue")
        self.assertIn("stored", result)

    def test_memory_retrieval(self):
        self.memory.store_information("favorite_food", "pizza")
        value = self.memory.retrieve_information("favorite_food")
        self.assertEqual(value, "pizza")

    def test_memory_missing_key(self):
        result = self.memory.retrieve_information("nonexistent_key")
        self.assertIn("No information", result)

    def test_memory_update(self):
        self.memory.store_information("mood", "happy")
        result = self.memory.update_information("mood", "calm")
        self.assertIn("updated", result)
        self.assertEqual(self.memory.retrieve_information("mood"), "calm")


class TestEducationModule(unittest.TestCase):
    def setUp(self):
        self.edu = EducationModule()

    def test_add_syllabus(self):
        result = self.edu.add_syllabus(
            "Python",
            ["Variables", "Loops", "Functions"],
            str(date.today() + timedelta(days=30)),
        )
        self.assertIn("added successfully", result)
        self.assertIn("Python", self.edu.syllabus)

    def test_generate_mcq_count(self):
        mcqs = self.edu.generate_mcq("Python", count=5)
        self.assertEqual(len(mcqs), 5)

    def test_generate_mcq_structure(self):
        mcqs = self.edu.generate_mcq("Maths", count=1)
        q = mcqs[0]
        self.assertIn('question', q)
        self.assertIn('options', q)
        self.assertIn('answer', q)
        self.assertIn(q['answer'], ['A', 'B', 'C', 'D'])

    def test_generate_mcq_invalid_count(self):
        with self.assertRaises(ValueError):
            self.edu.generate_mcq("Topic", count=0)

    def test_exam_timetable_no_syllabus(self):
        result = self.edu.create_exam_timetable()
        self.assertIsInstance(result, str)
        self.assertIn("No syllabus", result)

    def test_exam_timetable_with_syllabus(self):
        self.edu.add_syllabus(
            "History",
            ["Ancient", "Medieval", "Modern"],
            str(date.today() + timedelta(days=15)),
        )
        timetable = self.edu.create_exam_timetable()
        self.assertIsInstance(timetable, dict)
        self.assertGreater(len(timetable), 0)

    def test_todo_list_empty_syllabus(self):
        result = self.edu.create_todo_list()
        self.assertEqual(result, [])

    def test_todo_list_with_syllabus(self):
        self.edu.add_syllabus(
            "Chemistry",
            ["Atoms", "Bonds"],
            str(date.today() + timedelta(days=10)),
        )
        todo = self.edu.create_todo_list("Chemistry")
        self.assertEqual(len(todo), 2)
        self.assertFalse(todo[0]['done'])

    def test_mark_topic_covered(self):
        self.edu.add_syllabus(
            "Physics",
            ["Motion", "Force"],
            str(date.today() + timedelta(days=10)),
        )
        result = self.edu.mark_topic_covered("Physics", "Motion")
        self.assertIn("covered", result)
        todo = self.edu.create_todo_list("Physics")
        done = {t['topic']: t['done'] for t in todo}
        self.assertTrue(done["Motion"])
        self.assertFalse(done["Force"])

    def test_exam_reminders_upcoming(self):
        self.edu.add_syllabus(
            "Biology",
            ["Cells", "Genetics"],
            str(date.today() + timedelta(days=5)),
        )
        reminders = self.edu.get_exam_reminders()
        self.assertEqual(len(reminders), 1)
        self.assertEqual(reminders[0]['subject'], "Biology")
        self.assertEqual(reminders[0]['days_left'], 5)

    def test_answer_question_structure(self):
        result = self.edu.answer_question("What is Newton's first law?", subject="Physics")
        self.assertIn('question', result)
        self.assertIn('answer', result)
        self.assertEqual(result['subject'], "Physics")


class TestSystemControl(unittest.TestCase):
    def setUp(self):
        self.sys_ctrl = SystemControl()

    def test_open_website_adds_scheme(self):
        # Monkey-patch webbrowser.open so the test does not open a browser
        import webbrowser
        opened = []
        original_open = webbrowser.open
        webbrowser.open = lambda url, **kw: opened.append(url)
        try:
            result = self.sys_ctrl.open_website("example.com")
            self.assertTrue(opened[0].startswith("https://"))
            self.assertIn("Opening", result)
        finally:
            webbrowser.open = original_open

    def test_open_website_preserves_scheme(self):
        import webbrowser
        opened = []
        original_open = webbrowser.open
        webbrowser.open = lambda url, **kw: opened.append(url)
        try:
            self.sys_ctrl.open_website("http://example.com")
            self.assertEqual(opened[0], "http://example.com")
        finally:
            webbrowser.open = original_open

    def test_play_youtube_builds_url(self):
        import webbrowser
        opened = []
        original_open = webbrowser.open
        webbrowser.open = lambda url, **kw: opened.append(url)
        try:
            result = self.sys_ctrl.play_youtube("animal trailer", "telugu")
            self.assertIn("youtube.com", opened[0])
            self.assertIn("animal", opened[0])
            self.assertIn("telugu", opened[0])
            self.assertIn("Sir", result)
        finally:
            webbrowser.open = original_open

    def test_increase_volume_returns_message(self):
        # We cannot test actual hardware; just verify the return message
        result = self.sys_ctrl.increase_volume(5)
        self.assertIn("Volume increased", result)

    def test_decrease_volume_returns_message(self):
        result = self.sys_ctrl.decrease_volume(5)
        self.assertIn("Volume decreased", result)


if __name__ == '__main__':
    unittest.main()