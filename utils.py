import json
import re


def transform_empty_strings_to_none(d):
    return {k: (v if v != "" else None) for k, v in d.items()}


def find_last_json_blob(text):
    stack = []
    last_index = -1

    for i, char in enumerate(text):
        if char == "{":
            stack.append(i)
        elif char == "}":
            if stack:
                start = stack.pop()
                if not stack:
                    last_index = i

    if last_index != -1:
        json_str = text[start : last_index + 1]
        return json_str
    return None


def remove_trailing_commas(json_like: str):
    json_like = re.sub(",\s*}", "}", json_like)
    json_like = re.sub(",\s*\]", "]", json_like)
    return json_like


def remove_comments(text):
    text = re.sub(r"//.*?\n|/\*.*?\*/", "", text, flags=re.S)
    return text


def str_to_json(str_input):
    try:
        result = str_input.replace("None", "null")
        result = result.replace("'", '"')
        result = remove_trailing_commas(result)
        result = find_last_json_blob(result)
        result = remove_comments(result)
        result = json.loads(result, object_hook=transform_empty_strings_to_none)
        return result
    except Exception as e:
        return None
