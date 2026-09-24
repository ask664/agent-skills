import importlib.util
import io
import json
import unittest
from decimal import DecimalException
from pathlib import Path
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]


def load(skill, script):
    spec = importlib.util.spec_from_file_location(skill, ROOT / "skills" / skill / "scripts" / script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillsTest(unittest.TestCase):
    def test_calculator(self):
        calc = load("calculator", "calculate.py").calculate
        self.assertEqual(calc("add", "0.1", "0.2"), "0.3")
        self.assertEqual(calc("subtract", "3", "5"), "-2")
        self.assertEqual(calc("multiply", "12.5", "8"), "100.0")
        self.assertEqual(calc("divide", "10", "4"), "2.5")
        with self.assertRaises(DecimalException):
            calc("divide", "1", "0")
        with self.assertRaises(ValueError):
            calc("add", "NaN", "1")

    def test_retrieval(self):
        retrieve = load("data-retrieval", "retrieve.py").retrieve
        self.assertEqual(retrieve("P100")["price"], "4.50")
        self.assertIsNone(retrieve("missing"))

    def test_api_with_mock_response(self):
        lookup = load("api-lookup", "lookup.py").lookup
        def opener(request, timeout):
            self.assertEqual(request.full_url, "https://api.github.com/repos/kagent-dev/kagent")
            self.assertEqual(timeout, 10)
            return io.StringIO(json.dumps({"full_name": "kagent-dev/kagent", "stargazers_count": 42, "default_branch": "main"}))
        self.assertEqual(lookup("kagent-dev", "kagent", opener)["stars"], 42)
        with self.assertRaises(ValueError):
            lookup("https://example.com", "kagent", opener)
        def unavailable(*args, **kwargs):
            raise URLError("offline")
        with self.assertRaises(URLError):
            lookup("kagent-dev", "kagent", unavailable)


if __name__ == "__main__":
    unittest.main()
