import os
import re
from typing import List, Tuple

MAX_FILE_SIZE = 5 * 1024 * 1024
ATTACH_PATTERN = re.compile(r'@::(.+?)::')

def replace_file_attachments(text: str) -> Tuple[str, List[str]]:
    errors: List[str] = []

    def replace(match: re.Match[str]) -> str:
        filepath = match.group(1)
        try:
            if not os.path.isfile(filepath):
                errors.append('File not found: ' + filepath)
                return match.group(0)
            size = os.path.getsize(filepath)
            if size > MAX_FILE_SIZE:
                errors.append('File too large (>5MB): ' + filepath)
                return match.group(0)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return content
        except Exception as e:
            errors.append('Error reading ' + filepath + ': ' + str(e))
            return match.group(0)

    new_text = ATTACH_PATTERN.sub(replace, text)
    return new_text, errors