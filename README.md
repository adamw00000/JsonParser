# JSON parser

This code implements a JSON parser according to [JSON specification](https://www.json.org/json-en.html) using Python.

## Usage
```python
from json_parser import read_json

filename = 'path/to/example.json'
result = read_json(filename)
print(result)
```


## Requirements

Used in unit tests (parser itself has no dependencies):
```pip install parameterized==0.8.1```

## Examples

There is a total of 40 examples included with the code, split into valid and invalid JSON examples. They are located in `examples/valid` and `examples/invalid` directories.

## Unit tests

Tests are split into two groups: for valid JSONs and invalid ones. For valid JSONs, parser outputs are compared against `json` package parser outputs, and assertion error is raised in case of a mismatch. For invalid JSONs, `ValueError` exception is expected in both cases (or its subclass, `JSONDecodeError` for `json` package parser). Each test corresponds to parsing one of the examples in `examples/` directory.

In order to run those tests, use command:

```python -m unittest tests -v```


## Parser outputs for each test case

You can view implemented parser's output (or error message) for each example file using the script:

```python tests_with_outputs.py```
