import re

def parse_malformed_json(message: str) -> dict:
    """
    Parses a malformed JSON string missing commas between key-value pairs into a dictionary.
    Handles nested confirmation_levels dictionary as well.
    """
    result = {}
    # Remove outer braces if present
    msg = message.strip()
    if msg.startswith("{") and msg.endswith("}"):
        msg = msg[1:-1]

    # Regex to match key-value pairs, including nested dict for confirmation_levels
    # This regex matches keys and values separated by colon, values can be strings, numbers, booleans, or nested dict
    pattern = re.compile(
        r'"(?P<key>[^"]+)"\s*:\s*(?P<value>"[^"]*"|\d+\.?\d*|true|false|null|\{[^{}]*\})'
    )

    for match in pattern.finditer(msg):
        key = match.group("key")
        value = match.group("value").strip()
        # Parse value
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value == "true":
            value = True
        elif value == "false":
            value = False
        elif value == "null":
            value = None
        elif value.startswith("{") and value.endswith("}"):
            # Parse nested dict for confirmation_levels
            nested_str = value[1:-1]
            nested_dict = {}
            nested_pattern = re.compile(
                r'"(?P<nkey>[^"]+)"\s*:\s*(?P<nvalue>"[^"]*"|\d+\.?\d*|true|false|null)'
            )
            for nmatch in nested_pattern.finditer(nested_str):
                nkey = nmatch.group("nkey")
                nvalue = nmatch.group("nvalue").strip()
                if nvalue.startswith('"') and nvalue.endswith('"'):
                    nvalue = nvalue[1:-1]
                elif nvalue == "true":
                    nvalue = True
                elif nvalue == "false":
                    nvalue = False
                elif nvalue == "null":
                    nvalue = None
                else:
                    try:
                        if '.' in nvalue:
                            nvalue = float(nvalue)
                        else:
                            nvalue = int(nvalue)
                    except:
                        pass
                nested_dict[nkey] = nvalue
            value = nested_dict
        else:
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except:
                pass
        result[key] = value
    return result
