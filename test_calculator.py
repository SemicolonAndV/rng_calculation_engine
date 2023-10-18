import unittest
import calculator
from jsonschema.exceptions import ValidationError
import pandas as pd

class Test_calculator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dummy_data = {'title': 'title', 'n_workers': 5, 'n_sims': 20, 'random_seed': 101}
    
    def test_load_input(self):
        # incorrect json
        self.assertRaises(
            ValidationError, calculator.load_input, '{"1": "2"}')
        # incorrect json (without mandatory field)
        self.assertRaises(
            ValidationError, 
            calculator.load_input, 
            '{"n_workers": 4, "random_seed": 5, "n_sims": 6, "threshold": 7}'
        )
        # correct json (with all fields)
        self.assertTrue(
            calculator.load_input(
                '{"title": "mocktitle", "n_workers": 4, "random_seed": 5, "n_sims": 6, "threshold": 7}'
            )
        )
        # correct json (with all mandatory fields and without optional field)
        self.assertTrue(
            calculator.load_input(
                '{"title": "mocktitle", "n_workers": 4, "random_seed": 5, "n_sims": 6}'
                )
            )
        # correct json, compare with dummy data
        self.assertEqual(
            {'title': 'title', 'n_workers': 5, 'n_sims': 20, 'random_seed': 101},
            calculator.load_input(
                '{"title": "title", "n_workers": 5, "n_sims": 20, "random_seed": 101}'
            )
        )
        
    def test_rand_num_generator(self):
        rng = calculator.rand_num_generator(self.dummy_data["random_seed"])
        self.assertEqual(0.5811521325045647, next(rng))
        self.assertEqual(0.1947544955341367, next(rng))
        
    def test_evenly_split_workers(self):
        self.assertEqual(calculator.get_evenly_split_workers(2, 2), [1, 1])
        self.assertEqual(calculator.get_evenly_split_workers(11, 3), [4, 4, 3])
        self.assertEqual(calculator.get_evenly_split_workers(100, 5), [20, 20, 20, 20, 20])
         
    def test_generate_rng_results(self):
        self.assertIsInstance(calculator.generate_rng_results(self.dummy_data), list)
    
    def test_reduce_col(self):
        dummy_df = pd.DataFrame({"col1": [1, 1, 2, 3, 4]})
        dummy_stats = calculator.reduce_col(dummy_df, "col1", 2.5)
        self.assertEqual(dummy_stats["numof_samples"], 5)
        self.assertEqual(dummy_stats["numof_samples_thresh"], 2)
        self.assertEqual(dummy_stats["max_result"], 4)
        self.assertEqual(dummy_stats["min_result"], 1)
        self.assertEqual(dummy_stats["median"], 2)
        self.assertEqual(dummy_stats["count_distinct"], 4)
        self.assertEqual(dummy_stats["sum"], 11)