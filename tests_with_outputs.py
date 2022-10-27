# %%
import os
import json
from json_parser import read_json

def run_tests(dir, verbose=False):
    for file in os.listdir(dir):
        print(f'File: {file}')
        try:
            json_path = os.path.join(dir, file)
            value = read_json(json_path)
            with open(json_path, 'r', encoding='utf8') as f:
                correct_value = json.load(f)

            assert value == correct_value

            if verbose:
                print(value)
        except ValueError as e:
            if verbose:
                print(f'Error: {e}')
        print()

if __name__ == '__main__':
    print('-' * 20 + 'VALID JSON EXAMPLES' + '-' * 20 + '\n')
    run_tests(os.path.join('examples', 'valid'), verbose=True)

    print()

    print('-' * 20 + 'INVALID JSON EXAMPLES' + '-' * 20)
    run_tests(os.path.join('examples', 'invalid'), verbose=True)

# %%
