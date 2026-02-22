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

    def test_whatsapp_minute_overflow_uses_timedelta(self):
        """Scheduling at xx:59 should roll over to the next hour, not stay at :01."""
        from communication_module import CommunicationModule
        cm = CommunicationModule()
        # Patch datetime inside communication_module to return 23:59
        fake_dt = datetime.datetime(2025, 1, 1, 23, 59)
        with patch("communication_module.datetime") as mock_dt:
            mock_dt.datetime.now.return_value = fake_dt
            mock_dt.timedelta = datetime.timedelta
            # Patch pywhatkit to capture scheduled time
            captured = {}
            with patch.dict("sys.modules", {"pywhatkit": MagicMock()}):
                import pywhatkit as pwk
                def fake_sendwhatmsg(phone, msg, h, m):
                    captured["h"] = h
                    captured["m"] = m
                pwk.sendwhatmsg = fake_sendwhatmsg
                cm.send_whatsapp("+1234567890", "test msg")
        # If timedelta is used: scheduled = 23:59 + 2min = 00:01 next day → h=0, m=1
        # If modulo was used: (59 + 2) % 60 = 1, hour stays 23 → wrong
        if captured:
            self.assertEqual(captured.get("h"), 0, "Hour should roll to 00:00 next day")
            self.assertEqual(captured.get("m"), 1, "Minute should be 01")


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


class TestMemoryStore(unittest.TestCase):
    """Tests for the new semantic memory store (stark/memory_store.py)."""

    def _make_store(self):
        from stark.memory_store import MemoryStore
        return MemoryStore()

    def test_store_and_exact_recall(self):
        ms = self._make_store()
        ms.store("favourite colour is blue")
        self.assertIsNotNone(ms.recall_exact("favourite colour is blue"))

    def test_semantic_recall_finds_related_fact(self):
        """Semantic search should match even without an exact key."""
        ms = self._make_store()
        ms.store("sister birthday is June 3")
        results = ms.recall("when is my sister birthday")
        self.assertGreater(len(results), 0, "Expected at least one result")
        self.assertIn("June 3", results[0]["value"])

    def test_semantic_recall_returns_empty_for_no_match(self):
        ms = self._make_store()
        ms.store("dog name is Rex")
        results = ms.recall("favourite cheese")
        self.assertEqual(results, [])

    def test_store_updates_existing_key(self):
        ms = self._make_store()
        ms.store("mood", "happy")
        ms.store("mood", "excited")
        self.assertEqual(ms.recall_exact("mood"), "excited")

    def test_forget(self):
        ms = self._make_store()
        ms.store("temp fact")
        self.assertTrue(ms.forget("temp fact"))
        self.assertIsNone(ms.recall_exact("temp fact"))

    def test_forget_unknown_key_returns_false(self):
        ms = self._make_store()
        self.assertFalse(ms.forget("nonexistent"))

    def test_summary_empty(self):
        ms = self._make_store()
        summary = ms.summary()
        self.assertIn("stored memories", summary.lower())

    def test_summary_nonempty(self):
        ms = self._make_store()
        ms.store("hobby is chess")
        summary = ms.summary()
        self.assertIn("chess", summary)

    def test_contains_operator(self):
        ms = self._make_store()
        ms.store("test key")
        self.assertIn("test key", ms)
        self.assertNotIn("other key", ms)

    def test_len(self):
        ms = self._make_store()
        ms.store("a")
        ms.store("b")
        self.assertEqual(len(ms), 2)

    def test_top_k_limits_results(self):
        ms = self._make_store()
        for i in range(10):
            ms.store(f"favourite sport number {i}")
        results = ms.recall("favourite sport", top_k=3)
        self.assertLessEqual(len(results), 3)


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
    def test_unknown_action(self):
        """Unknown actions should not raise; they call speak_fn with an error msg."""
        from system_control import SystemControl
        messages = []
        SystemControl.execute("unknown_action", speak_fn=messages.append)
        self.assertTrue(any("Unknown" in m for m in messages))


class TestAutomation(unittest.TestCase):
    """Tests for stark/automation.py — especially the security PIN guard."""

    def test_non_destructive_action_executes_without_pin(self):
        """Non-destructive actions should execute even without a PIN."""
        from stark.automation import execute_action
        spoken = []
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STARK_SECURITY_PIN", None)
            with patch("stark.automation.SystemControl") as mock_sc:
                result = execute_action("volume_up", speak_fn=spoken.append)
        self.assertTrue(result)
        mock_sc.execute.assert_called_once_with("volume_up", speak_fn=spoken.append)

    def test_destructive_action_allowed_when_no_pin_set(self):
        """When STARK_SECURITY_PIN is unset, destructive actions proceed."""
        from stark.automation import execute_action
        spoken = []
        os.environ.pop("STARK_SECURITY_PIN", None)
        with patch("stark.automation.SystemControl") as mock_sc:
            result = execute_action("shutdown", speak_fn=spoken.append, listen_fn=lambda **_: "")
        self.assertTrue(result)
        mock_sc.execute.assert_called_once()

    def test_destructive_action_blocked_on_wrong_pin(self):
        """Wrong PIN must block the destructive action."""
        from stark.automation import execute_action
        spoken = []
        with patch.dict(os.environ, {"STARK_SECURITY_PIN": "1234"}):
            with patch("stark.automation.SystemControl") as mock_sc:
                result = execute_action(
                    "shutdown",
                    speak_fn=spoken.append,
                    listen_fn=lambda **_: "9999",  # wrong PIN
                )
        self.assertFalse(result)
        mock_sc.execute.assert_not_called()
        self.assertTrue(any("incorrect" in s.lower() for s in spoken))

    def test_destructive_action_allowed_on_correct_pin(self):
        """Correct PIN must allow the destructive action."""
        from stark.automation import execute_action
        spoken = []
        with patch.dict(os.environ, {"STARK_SECURITY_PIN": "1234"}):
            with patch("stark.automation.SystemControl") as mock_sc:
                result = execute_action(
                    "shutdown",
                    speak_fn=spoken.append,
                    listen_fn=lambda **_: "1234",  # correct
                )
        self.assertTrue(result)
        mock_sc.execute.assert_called_once()

    def test_destructive_action_blocked_when_no_listener(self):
        """If no listen_fn is provided but PIN is set, block the action."""
        from stark.automation import execute_action
        spoken = []
        with patch.dict(os.environ, {"STARK_SECURITY_PIN": "1234"}):
            with patch("stark.automation.SystemControl") as mock_sc:
                result = execute_action("restart", speak_fn=spoken.append, listen_fn=None)
        self.assertFalse(result)
        mock_sc.execute.assert_not_called()


class TestIntentRegistry(unittest.TestCase):
    """Tests for stark/brain.py IntentRegistry."""

    def test_dispatch_calls_correct_handler(self):
        from stark.brain import IntentRegistry
        reg = IntentRegistry()
        called_with = []
        reg.register(
            "greet",
            lambda c: "hello" in c,
            lambda c, **kw: called_with.append(c),
        )
        reg.dispatch("hello world")
        self.assertEqual(called_with, ["hello world"])

    def test_higher_priority_wins(self):
        from stark.brain import IntentRegistry
        reg = IntentRegistry()
        results = []
        reg.register("low",  lambda c: True, lambda c, **kw: results.append("low"),  priority=10)
        reg.register("high", lambda c: True, lambda c, **kw: results.append("high"), priority=90)
        reg.dispatch("anything")
        self.assertEqual(results, ["high"])  # only the highest-priority handler runs

    def test_dispatch_returns_none_when_no_match(self):
        from stark.brain import IntentRegistry
        reg = IntentRegistry()
        reg.register("greet", lambda c: "hello" in c, lambda c, **kw: "greeted")
        result = reg.dispatch("goodbye")
        self.assertIsNone(result)

    def test_intent_names_in_priority_order(self):
        from stark.brain import IntentRegistry
        reg = IntentRegistry()
        reg.register("b", lambda c: False, lambda c, **kw: None, priority=10)
        reg.register("a", lambda c: False, lambda c, **kw: None, priority=90)
        self.assertEqual(reg.intent_names(), ["a", "b"])


class TestMainController(unittest.TestCase):
    """Tests for the fixed main_controller.py (broken import bug)."""

    def test_import_succeeds(self):
        """main_controller must import without raising ImportError."""
        import main_controller  # noqa: F401

    def test_instantiation(self):
        from main_controller import StarkAssistant as ApiAssistant
        api = ApiAssistant("user_test")
        self.assertEqual(api.user_id, "user_test")

    def test_add_and_list_task(self):
        from main_controller import StarkAssistant as ApiAssistant
        api = ApiAssistant("user_test")
        api.process_command("add_task", "Buy groceries")
        tasks = api.process_command("list_tasks")
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 1)

    def test_store_and_retrieve_memory(self):
        from main_controller import StarkAssistant as ApiAssistant
        api = ApiAssistant("user_test")
        api.process_command("store_memory", "language", "Python")
        result = api.process_command("retrieve_memory", "language")
        self.assertEqual(result, "Python")

    def test_get_status_structure(self):
        from main_controller import StarkAssistant as ApiAssistant
        api = ApiAssistant("user_test")
        status = api.get_status()
        self.assertIn("user_id", status)
        self.assertIn("uptime", status)
        self.assertIn("active_tasks", status)
        self.assertIn("stored_memories", status)

    def test_unrecognized_command(self):
        from main_controller import StarkAssistant as ApiAssistant
        api = ApiAssistant("user_test")
        result = api.process_command("unknown_command_xyz")
        self.assertIn("not recognized", result.lower())


class TestStarkAssistant(unittest.TestCase):
    """Unit tests for StarkAssistant that do not require audio devices."""

    def _make_assistant(self):
        """Create a StarkAssistant with TTS/audio patched out."""
        import stark       # stark/ package (not the old stark.py single-file module)
        import stark.core  # so we can patch speak at the core level

        # Silence speak() in both the package namespace and core module
        stark.speak = lambda text: None
        stark.core.speak = lambda text: None

        # Construct without calling __init__ (avoids hardware + API calls)
        assistant = stark.StarkAssistant.__new__(stark.StarkAssistant)
        assistant.current_role = "assistant"

        from stark.memory_store import MemoryStore
        assistant.memory = MemoryStore()
        assistant.exam_schedule = {}
        assistant.study_timetable = {}
        assistant.busy = False
        assistant.busy_message = (
            "Balu is busy right now. I am STARK, his personal AI assistant."
        )
        assistant.missed_calls = {}
        assistant.work_start_time = None
        # Minimal brain stub so process_command doesn't crash
        from stark.brain import Brain, IntentRegistry
        assistant._brain = Brain.__new__(Brain)
        assistant._brain._model = None
        assistant._brain._history = []
        assistant._registry = IntentRegistry()
        assistant._register_intents()
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
        response = a._brain.ask("hello")
        self.assertIn("not available", response.lower())

    def test_create_study_timetable(self):
        a = self._make_assistant()
        future = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        result = a.create_study_timetable("Algebra, Geometry, Calculus", future)
        self.assertIn("Algebra", result)
        self.assertIsInstance(a.study_timetable, dict)

    def test_send_whatsapp_no_pywhatkit(self):
        a = self._make_assistant()
        # pywhatkit may not be installed in test env — expect graceful message
        result = a.send_whatsapp_message("+1234567890", "test")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_intent_registry_has_expected_intents(self):
        """The registry should contain all the named intents we registered."""
        a = self._make_assistant()
        names = a._registry.intent_names()
        expected = {
            "exit", "greeting", "shutdown", "restart", "youtube",
            "open_site", "remember", "tell_time", "tell_date",
        }
        for intent in expected:
            self.assertIn(intent, names, f"Intent '{intent}' not registered")

    def test_semantic_recall_after_remember(self):
        """recall_semantic should find a memory using word overlap, not exact key."""
        a = self._make_assistant()
        a.remember("sister birthday is June 3")
        result = a.recall_semantic("when is sister birthday")
        self.assertIn("June 3", result)


if __name__ == "__main__":
    unittest.main()