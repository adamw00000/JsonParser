### CONSTANTS ###

__NULL_TOKEN = 'null'
__TRUE_TOKEN = 'true'
__FALSE_TOKEN = 'false'

### PRIVATE NEXT-VALUE-TYPE FUNCTIONS ###

def __is_string_start(text, pos):
    return text[pos] == '"'


def __is_number_start(text, pos):
    return text[pos] == '-' or text[pos].isdigit()


def __is_object_start(text, pos):
    return text[pos] == '{'


def __is_array_start(text, pos):
    return text[pos] == '['


def __is_true_start(text, pos):
    return text[pos] == 't'


def __is_false_start(text, pos):
    return text[pos] == 'f'


def __is_null_start(text, pos):
    return text[pos] == 'n'

### PRIVATE PARSE FUNCTIONS ###

# Input: 
#   - text,
#   - start position of element to parse,
#   - (optional) element-specific extra input.
# Output: 
#   - parsed value,
#   - text (might be different from input in case of escape characters),
#   - start position of next element to parse.

#######################

def __parse_whitespace(text, start_pos):
    if start_pos == len(text):
        return '', text, start_pos
    
    pos = start_pos
    while text[pos].isspace():
        pos += 1

        if pos == len(text):
            break

    return text[start_pos:pos], text, pos


def __parse_keyword(text, start_pos, expected_keyword):
    if expected_keyword not in [__TRUE_TOKEN, __FALSE_TOKEN, __NULL_TOKEN]:
        raise ValueError(f'Invalid keyword')

    if start_pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}')
    
    input_end = start_pos + len(expected_keyword)
    input_string = text[start_pos:input_end]

    if input_end > len(text) or input_string != expected_keyword:
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected {expected_keyword}')

    # Return correct value
    if expected_keyword == __TRUE_TOKEN:
        value = True
    elif expected_keyword == __FALSE_TOKEN:
        value = False
    else:
        value = None
    return value, text, input_end


def __replace_control_sequence(text, start_pos):
    if text[start_pos] != '\\':
        return '', text, start_pos
    
    pos = start_pos + 1

    # Only correct sequences
    if pos == len(text) or text[pos] not in r'"\\/bfnrtu':
        raise ValueError(f'Invalid JSON format at position {pos}: expected valid control sequence')
    
    if text[pos] == 'u':
        character_code = ''

        # Four hex digits
        for _ in range(4):
            pos += 1

            if pos == len(text) or text[pos] not in '1234567890ABCDEF':
                raise ValueError(f'Invalid JSON format at position {pos}: expected Unicode character code')
            
            character_code += text[pos]
        
        # Find correct unicode character by hex code
        unicode_character = chr(int(character_code, 16))

        pos += 1
        text = text[:start_pos] + unicode_character + text[pos:]
        pos = start_pos + 1
    else:
        if text[pos] == '"':
            escape_character = '"'
        elif text[pos] == '\\':
            escape_character = '\\'
        elif text[pos] == '/':
            escape_character = '/'
        elif text[pos] == 'b':
            escape_character = '\b'
        elif text[pos] == 'f':
            escape_character = '\f'
        elif text[pos] == 'n':
            escape_character = '\n'
        elif text[pos] == 'r':
            escape_character = '\r'
        elif text[pos] == 't':
            escape_character = '\t'
        else:
            raise ValueError(f'Invalid JSON format at position {pos}: expected valid control sequence')
        
        pos += 1
        text = text[:start_pos] + escape_character + text[pos:]
        pos = start_pos + 1

    return text[start_pos:pos], text, pos

def __parse_string(text, start_pos):
    if start_pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected string')

    if text[start_pos] != '"':
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected """')
    pos = start_pos + 1

    while text[pos] != '"':
        if text[pos] == '\\':
            _, text, pos = __replace_control_sequence(text, pos)
        else:
            pos += 1

        # Handle multiline strings!
        if pos == len(text) or text[pos] == '\n':
            raise ValueError(f'Invalid JSON format at position {pos}: expected """')
    
    return text[start_pos + 1:pos], text, pos + 1


def __parse_integer_number_part(text, start_pos):
    if start_pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected number')
    
    # Handle numbers starting with zero
    if text[start_pos] == '0':
        return 0, text, start_pos + 1

    # Parse digits, first cannot be zero
    pos = start_pos
    while text[pos].isdigit():
        pos += 1

        if pos == len(text):
            break
        
    return int(text[start_pos:pos]), text, pos


def __parse_fraction_number_part(text, start_pos):    
    if start_pos == len(text) or text[start_pos] != '.':
        return 0, text, start_pos
    
    pos = start_pos + 1
    if pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected fraction')
    
    # Parse fraction digits
    while text[pos].isdigit():
        pos += 1
        if pos == len(text):
            break

    fraction_length = pos - (start_pos + 1)
    if fraction_length == 0:
        # No digits after .
        raise ValueError(f'Invalid JSON format at position {pos}: expected fraction')
    
    fraction_number = int(text[(start_pos + 1):pos])
    fraction_value = fraction_number / (10 ** fraction_length)
    return fraction_value, text, pos


def __parse_exponent_number_part(text, start_pos):    
    if start_pos == len(text) or text[start_pos].lower() != 'e':
        return 1, text, start_pos
    
    pos = start_pos + 1
    if pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected exponent')
    
    # Parse sign
    if text[pos] == '-' or text[pos] == '+':
        pos += 1
        if pos == len(text):
            raise ValueError(f'Invalid JSON format at position {start_pos}: expected exponent')
    
    # Parse exponent digits
    while text[pos].isdigit():
        pos += 1
        if pos == len(text):
            break

    exponent_length = pos - (start_pos + 1)
    if exponent_length == 0:
        # No digits after e+ / E- / e / ...
        raise ValueError(f'Invalid JSON format at position {pos}: expected exponent')
    
    exponent_number = int(text[(start_pos + 1):pos])
    exponent_value = (10 ** exponent_number)
    return exponent_value, text, pos


def __parse_number(text, start_pos):
    if start_pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected number')
    pos = start_pos

    # Handle negative numbers
    multiplier = 1
    if text[start_pos] == '-':
        multiplier = -1
        pos += 1

    if not text[pos].isdigit():
        raise ValueError(f'Invalid JSON format at position {pos}: expected number')
    
    integer_part, text, pos = __parse_integer_number_part(text, pos)
    fraction_part, text, pos = __parse_fraction_number_part(text, pos)
    exponent_part, text, pos = __parse_exponent_number_part(text, pos)

    number_value = multiplier * (integer_part + fraction_part) * exponent_part
    return number_value, text, pos


def __parse_value(text, start_pos):
    if start_pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected value')
    
    pos = start_pos
    _, text, pos = __parse_whitespace(text, pos)

    if pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected value')

    if __is_string_start(text, pos):
        value, text, pos = __parse_string(text, pos)
    elif __is_number_start(text, pos):
        value, text, pos = __parse_number(text, pos)
    elif __is_object_start(text, pos):
        value, text, pos = __parse_object(text, pos)
    elif __is_array_start(text, pos):
        value, text, pos = __parse_array(text, pos)
    elif __is_true_start(text, pos):
        value, text, pos = __parse_keyword(text, pos, __TRUE_TOKEN)
    elif __is_false_start(text, pos):
        value, text, pos = __parse_keyword(text, pos, __FALSE_TOKEN)
    elif __is_null_start(text, pos):
        value, text, pos = __parse_keyword(text, pos, __NULL_TOKEN)
    else:
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected value')
    
    _, text, pos = __parse_whitespace(text, pos)
    return value, text, pos


# Checks if query_token is the first token after whitespace ends
def __is_first_token_after_whitespace(text, start_pos, query_token):
    pos = start_pos
    for pos in range(start_pos, len(text)):
        if not text[pos].isspace():
            if text[pos] == query_token:
                return True, text, pos + 1
            else:
                return False, text, start_pos
    
    # Invoked when text ends before finding non-whitespace token
    raise ValueError(f'Invalid JSON format at position {len(text)}: expected "{query_token}"')
    

def __parse_array(text, start_pos):
    if start_pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected array')
    
    if text[start_pos] != '[':
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected "["')
    pos = start_pos + 1

    array = []

    # Handle empty array
    array_end_found, text, pos = __is_first_token_after_whitespace(text, pos, ']')
    if array_end_found:
        return array, text, pos
    else:
        is_last_value = False

    # Parse values
    while not is_last_value:
        value, text, pos = __parse_value(text, pos)
        array.append(value)
        
        if pos == len(text):
            raise ValueError(f'Invalid JSON format at position {pos}: expected "]"')
        
        # Next value / array end
        if text[pos] == ',':
            pos += 1
        elif text[pos] == ']':
            is_last_value = True
            pos += 1
        else:
            raise ValueError(f'Invalid JSON format at position {pos}: expected "]"')
    
    return array, text, pos


def __parse_object(text, start_pos):
    if start_pos == len(text):
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected object')
    
    if text[start_pos] != '{':
        raise ValueError(f'Invalid JSON format at position {start_pos}: expected ' + '"{"')
    pos = start_pos + 1

    values = {}
    
    # Handle empty object
    object_end_found, text, pos = __is_first_token_after_whitespace(text, pos, '}')
    if object_end_found:
        return values, text, pos
    else:
        is_last_pair = False

    # Parse key-value pairs
    while not is_last_pair:
        _, text, pos = __parse_whitespace(text, pos)
        key, text, pos = __parse_string(text, pos)
        _, text, pos = __parse_whitespace(text, pos)
        if pos == len(text) or text[pos] != ':':
            raise ValueError(f'Invalid JSON format at position {pos}: expected ":"')
        pos += 1
        value, text, pos = __parse_value(text, pos)

        values[key] = value

        if pos == len(text):
            raise ValueError(f'Invalid JSON format at position {pos}: expected ' + '"}"')
        
        # Next value / object end
        if text[pos] == ',':
            pos += 1
        elif text[pos] == '}':
            is_last_pair = True
            pos += 1
        else:
            raise ValueError(f'Invalid JSON format at position {pos}: expected ' + '"," or "}"')
        
    return values, text, pos


### PUBLIC INTERFACE ###

def read_json(path):
    """
    Read JSON from a file path.
    path - can be str or pathlib.Path
    """
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        
        # Parse root
        pos = 0
        value, text, pos = __parse_value(text, pos)

        # Handle multiple root elements
        if pos != len(text):
            raise ValueError(f'Invalid JSON format at position {pos}: unexpected token')
        
        return value

########################
