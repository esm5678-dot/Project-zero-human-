import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from model_gate import evaluate

class TestGate(unittest.TestCase):
    def setUp(self):
        self.valid={'enabled':True,'max_new_spend_krw':0,'verified_zero_cash_billing':True,'human_approved_provider':True,'daily_request_limit':2,'allow_external_data':False}
    def test_default_denied(self):
        self.assertFalse(evaluate({'enabled':False})['allowed'])
    def test_approved_conditions(self):
        self.assertTrue(evaluate(self.valid)['allowed'])
    def test_unverified_free_tier_denied(self):
        d={**self.valid,'verified_zero_cash_billing':False}
        self.assertFalse(evaluate(d)['allowed'])
    def test_nonzero_budget_denied(self):
        d={**self.valid,'max_new_spend_krw':1}
        self.assertFalse(evaluate(d)['allowed'])
    def test_customer_data_denied(self):
        d={**self.valid,'allow_external_data':True}
        self.assertFalse(evaluate(d)['allowed'])
    def test_no_network_usage(self):
        self.assertEqual(evaluate(self.valid)['network_calls'],0)
if __name__=='__main__': unittest.main()
