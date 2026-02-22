import unittest
import datetime
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

# ---------------------------------------------------------------------------
# Stub out audio packages that require hardware / aren't installed in CI.
# These stubs must be applied before any module that imports pyttsx3 / sr.
# ---------------------------------------------------------------------------
_AUDIO_STUBS = {
    "pyttsx3": MagicMock(),
    "speech_recognition": MagicMock(),
    "pyaudio": MagicMock(),
    "dotenv": MagicMock(),
}
_AUDIO_STUBS["pyttsx3"].init.return_value = MagicMock()

for _name, _stub in _AUDIO_STUBS.items():
    sys.modules.setdefault(_name, _stub)


class TestTaskManager(unittest.TestCase):
    def test_task_creation(self):
        from task_manager import TaskManager
        tm = TaskManager()
        result = tm.add_task("Test task", "user_001")
        self.assertIn("Test task", result)

    def test_task_failure_handling(self):
        from task_manager import TaskManager
        tm = TaskManager()
        result = tm.complete_task(9999)
        self.assertIn("not found", result.lower())


class TestCommunication(unittest.TestCase):
    def test_send_message(self):
        from communication_module import CommunicationModule
        cm = CommunicationModule()
        result = cm.send_message("Alice", "Hello")
        self.assertIn("Alice", result)

    def test_receive_message(self):
        from communication_module import CommunicationModule
        cm = CommunicationModule()
        cm.send_message("Bob", "Hi Bob", user_id="u1")
        msgs = cm.get_messages("u1")
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["recipient"], "Bob")

    def test_notification(self):
        from communication_module import CommunicationModule
        cm = CommunicationModule()
        cm.send_notification("Test notification", user_id="u2")
        notes = cm.get_notifications("u2")
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["content"], "Test notification")

    def test_busy_auto_reply(self):
        from communication_module import CommunicationModule
        reply = CommunicationModule.busy_auto_reply("caller_123")
        self.assertIn("busy", reply.lower())
        self.assertIn("STARK", reply)


class TestMemory(unittest.TestCase):
    def test_memory_storage(self):
        from memory import MemoryManager
        mm = MemoryManager()
        result = mm.store_information("fav_color", "blue")
        self.assertIn("stored", result.lower())

    def test_memory_retrieval(self):
        from memory import MemoryManager
        mm = MemoryManager()
        mm.store_information("fav_food", "pizza")
        value = mm.retrieve_information("fav_food")
        self.assertEqual(value, "pizza")

    def test_missing_key(self):
        from memory import MemoryManager
        mm = MemoryManager()
        result = mm.retrieve_information("nonexistent_key")
        self.assertIn("No information", result)


class TestStudyModule(unittest.TestCase):
    def test_create_timetable_valid(self):
        from study_module import StudyModule
        future = (datetime.datetime.now() + datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        result = StudyModule.create_timetable("Math, Physics, Chemistry", future)
        self.assertIsInstance(result, dict)
        self.assertIn("timetable", result)
        self.assertIn("summary", result)
        self.assertIn("topics", result)
        self.assertEqual(len(result["topics"]), 3)

    def test_create_timetable_past_date(self):
        from study_module import StudyModule
        result = StudyModule.create_timetable("Math", "2000-01-01")
        self.assertIsInstance(result, str)
        self.assertIn("passed", result.lower())

    def test_create_timetable_invalid_date(self):
        from study_module import StudyModule
        result = StudyModule.create_timetable("Math", "not-a-date")
        self.assertIsInstance(result, str)
        self.assertIn("Invalid", result)

    def test_days_until_exam(self):
        from study_module import StudyModule
        future = (datetime.datetime.now() + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        days = StudyModule.days_until_exam(future)
        self.assertGreaterEqual(days, 4)

    def test_days_until_exam_invalid(self):
        from study_module import StudyModule
        days = StudyModule.days_until_exam("bad-date")
        self.assertEqual(days, -1)


class TestSystemControl(unittest.TestCase):
    def test_unknown_action(self, ):
        """Unknown actions should not raise; they call speak_fn with an error msg."""
        from system_control import SystemControl
        messages = []
        SystemControl.execute("unknown_action", speak_fn=messages.append)
        self.assertTrue(any("Unknown" in m for m in messages))


class TestStarkAssistant(unittest.TestCase):
    """Unit tests for StarkAssistant that do not require audio devices."""

    def _make_assistant(self):
        """Create a StarkAssistant with TTS/audio patched out."""
        import stark  # noqa: PLC0415 – imported after stubs are in sys.modules

        # Silence speak() during tests
        stark.speak = lambda text: None

        # Construct without calling __init__ (avoids hardware + API calls)
        assistant = stark.StarkAssistant.__new__(stark.StarkAssistant)
        assistant.current_role = "assistant"
        assistant.memory = {}
        assistant.conversation_history = []
        assistant.exam_schedule = {}
        assistant.study_timetable = {}
        assistant.busy = False
        assistant.busy_message = (
            "Balu is busy right now. I am STARK, his personal AI assistant."
        )
        assistant.missed_calls = {}
        assistant.work_start_time = None
        assistant._gemini_model = None
        return assistant

    def test_remember_and_recall(self):
        a = self._make_assistant()
        a.remember("loves chess")
        self.assertIn("loves chess", a.memory)
        recall = a.recall_all()
        self.assertIn("loves chess", recall)

    def test_recall_empty(self):
        a = self._make_assistant()
        result = a.recall_all()
        self.assertIn("stored memories", result.lower())

    def test_set_busy(self):
        a = self._make_assistant()
        a.set_busy(True)
        self.assertTrue(a.busy)
        a.set_busy(False)
        self.assertFalse(a.busy)

    def test_handle_incoming_call_busy(self):
        a = self._make_assistant()
        a.set_busy(True)
        reply = a.handle_incoming_call("caller_001")
        self.assertIn("busy", reply.lower())
        self.assertIn("caller_001", a.missed_calls)

    def test_handle_incoming_call_free(self):
        a = self._make_assistant()
        a.set_busy(False)
        reply = a.handle_incoming_call("caller_002")
        self.assertEqual(reply, "")

    def test_create_todo_list(self):
        a = self._make_assistant()
        todo = a.create_todo_list(["Study Python", "Review notes"])
        self.assertEqual(len(todo), 2)
        self.assertEqual(todo[0]["task"], "Study Python")
        self.assertFalse(todo[0]["done"])

    def test_process_command_exit(self):
        a = self._make_assistant()
        result = a.process_command("goodbye")
        self.assertFalse(result)

    def test_process_command_empty(self):
        a = self._make_assistant()
        result = a.process_command("")
        self.assertTrue(result)

    def test_process_command_time(self):
        """Time command should return True (keep running)."""
        a = self._make_assistant()
        result = a.process_command("what is the time")
        self.assertTrue(result)

    def test_process_command_date(self):
        a = self._make_assistant()
        result = a.process_command("what is today's date")
        self.assertTrue(result)

    def test_ask_ai_no_key(self):
        a = self._make_assistant()
        response = a.ask_ai("hello")
        self.assertIn("not available", response.lower())

    def test_create_study_timetable(self):
        a = self._make_assistant()
        future = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        result = a.create_study_timetable("Algebra, Geometry, Calculus", future)
        self.assertIn("Algebra", result)
        self.assertIsInstance(a.study_timetable, dict)

    def test_send_whatsapp_no_pywhatkit(self):
        a = self._make_assistant()
        # pywhatkit may not be installed in test env - expect graceful message
        result = a.send_whatsapp_message("+1234567890", "test")
        # Either scheduled or "not installed"
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == "__main__":
    unittest.main()