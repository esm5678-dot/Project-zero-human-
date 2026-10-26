import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from local_ai_agent import aggregate, execute_allowlisted, verified_model


class LocalAgentSafety(unittest.TestCase):
    def test_input_is_aggregate_only(self):
        counts = aggregate()
        self.assertEqual(set(counts), {"entries", "completed_research"})
        self.assertTrue(all(isinstance(value, int) for value in counts.values()))
        self.assertLessEqual(counts["completed_research"], counts["entries"])

    def test_untrusted_model_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "qwen2.5-0.5b-instruct-q4_k_m.gguf"
            path.write_bytes(b"not the approved model")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verified_model(path)

    def test_model_cannot_choose_external_task(self):
        with self.assertRaisesRegex(ValueError, "no allowlisted task"):
            execute_allowlisted("send_customer_email", {"entries": 1})


if __name__ == "__main__":
    unittest.main()
