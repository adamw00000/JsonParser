# %%
import json
import unittest
from json_parser import read_json
from parameterized import parameterized

### Valid JSONs ###

class ValidJsonTests(unittest.TestCase):
    def __test_valid(self, json_path):
        value = read_json(json_path)
        with open(json_path, 'r', encoding='utf8') as f:
            correct_value = json.load(f)

        self.assertEqual(value, correct_value)
    
    @parameterized.expand([
        ['examples/valid/1.json'],
        ['examples/valid/2.json'],
        ['examples/valid/3.json'],
    ])
    def test_valid_examples(self, path):
        self.__test_valid(path)
    
    @parameterized.expand([
        ['examples/valid/big_example_1.json'],
        ['examples/valid/big_example_2.json'],
        ['examples/valid/big_example_3.json'],
        ['examples/valid/big_example_4.json'],
        ['examples/valid/big_example_5.json'],
    ])
    def test_valid_big_jsons(self, path):
        self.__test_valid(path)
    
    @parameterized.expand([
        ['examples/valid/control_sequences.json'],
    ])
    def test_valid_control_sequences(self, path):
        self.__test_valid(path)
    
    @parameterized.expand([
        ['examples/valid/empty_array.json'],
        ['examples/valid/empty_object.json'],
        ['examples/valid/empty_string.json'],
    ])
    def test_valid_empty_constructs(self, path):
        self.__test_valid(path)

    @parameterized.expand([
        ['examples/valid/numbers.json'],
    ])
    def test_valid_numbers(self, path):
        self.__test_valid(path)
    
    @parameterized.expand([
        ['examples/valid/whitespace_around_root.json'],
        ['examples/valid/whitespace_in_object.json'],
        ['examples/valid/whitespace_in_array.json'],
    ])
    def test_valid_whitespace(self, path):
        self.__test_valid(path)

### Invalid JSONs ###

class InvalidJsonTests(unittest.TestCase):
    def __test_invalid(self, json_path):
        with self.assertRaises(ValueError):
            read_json(json_path)
        with self.assertRaises(json.JSONDecodeError):
            with open(json_path, 'r', encoding='utf8') as f:
                json.load(f)

    @parameterized.expand([
        ['examples/invalid/invalid_control_sequence_1.json'],
        ['examples/invalid/invalid_control_sequence_2.json'],
        ['examples/invalid/invalid_control_sequence_3.json'],
    ])
    def test_invalid_control_sequences(self, path):
        self.__test_invalid(path)
    
    @parameterized.expand([
        ['examples/invalid/multiline_string.json'],
        ['examples/invalid/unfinished_string_1.json'],
        ['examples/invalid/unfinished_string_2.json'],
        ['examples/invalid/unfinished_string_3.json'],
    ])
    def test_invalid_strings(self, path):
        self.__test_invalid(path)
    
    @parameterized.expand([
        ['examples/invalid/array_no_comma.json'],
        ['examples/invalid/unfinished_array.json'],
    ])
    def test_invalid_arrays(self, path):
        self.__test_invalid(path)
    
    @parameterized.expand([
        ['examples/invalid/unfinished_object_1.json'],
        ['examples/invalid/unfinished_object_2.json'],
        ['examples/invalid/unfinished_object_3.json'],
        ['examples/invalid/unfinished_object_4.json'],
    ])
    def test_invalid_objects(self, path):
        self.__test_invalid(path)
    
    @parameterized.expand([
        ['examples/invalid/invalid_number_fraction_1.json'],
        ['examples/invalid/invalid_number_fraction_2.json'],
        ['examples/invalid/invalid_number_fraction_3.json'],
        ['examples/invalid/invalid_number_leading_0.json'],
        ['examples/invalid/invalid_number_exponent_1.json'],
        ['examples/invalid/invalid_number_exponent_2.json'],
        ['examples/invalid/invalid_number_exponent_3.json'],
        ['examples/invalid/invalid_number_exponent_4.json'],
    ])
    def test_invalid_numbers(self, path):
        self.__test_invalid(path)
    
    @parameterized.expand([
        ['examples/invalid/false_typo.json'],
        ['examples/invalid/null_typo.json'],
        ['examples/invalid/true_typo.json'],
    ])
    def test_invalid_typos_in_keywords(self, path):
        self.__test_invalid(path)


if __name__ == '__main__':
    unittest.main()

# %%
