import os
import re
from typing import cast, List
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from openai.types.chat import ChatCompletionMessageParam

MAX_FILE_SIZE = 5 * 1024 * 1024

def split_paragraphs(text: str, paragraph_count: int = 1) -> List[str]:
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    i = 0
    while i < len(paragraphs):
        chunk = paragraphs[i]
        for j in range(1, paragraph_count):
            if i + j < len(paragraphs):
                chunk += '\n\n' + paragraphs[i + j]
        chunks.append(chunk)
        i += paragraph_count
    return chunks

def split_by_length(text: str, chunk_len: int) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_len, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks

def file_chunk_mode(client: OpenAI, model: str, system_prompt: str) -> None:
    print('>>> Entering file chunk mode. Type \\q to exit back to main chat.')
    filepath = input('>>> Enter file path: ').strip()
    if filepath == '\\q':
        return

    if not os.path.isfile(filepath):
        print('>>> File not found.')
        return
    size = os.path.getsize(filepath)
    if size > MAX_FILE_SIZE:
        print('>>> File exceeds 5MB limit.')
        return
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            full_text = f.read()
    except Exception as e:
        print('>>> Error reading file: ' + str(e))
        return

    command = input(
        '>>> Chunking mode (e.g., paragraph=3, len=150, or empty for default): '
    ).strip()
    auto_mode = '-y' in command
    command = command.replace('-y', '').strip()

    chunks: List[str] = []
    if command.startswith('paragraph='):
        try:
            n = int(command.split('=', 1)[1])
            if n < 1:
                n = 1
        except ValueError:
            n = 1
        chunks = split_paragraphs(full_text, n)
    elif command.startswith('len='):
        try:
            n = int(command.split('=', 1)[1])
            if n < 1:
                n = 150
        except ValueError:
            n = 150
        chunks = split_by_length(full_text, n)
    else:
        chunks = split_paragraphs(full_text, 1)

    if not chunks:
        print('>>> No content to process.')
        return

    user_prompt = input('>>> Enter user prompt for each chunk: ').strip()
    if not user_prompt:
        print('>>> No prompt provided, aborting.')
        return

    print('>>> Processing chunks...\n')
    for i, chunk in enumerate(chunks, start=1):
        print('--- Chunk ' + str(i) + '/' + str(len(chunks)) + ' ---')
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt + '\n\n' + chunk}
        ]
        try:
            response = client.chat.completions.create(
                model=model,
                messages=cast(list[ChatCompletionMessageParam], messages),
                stream=True,
            )
            for part in response:
                if isinstance(part, ChatCompletionChunk):
                    content = part.choices[0].delta.content or ''
                    print(content, end='', flush=True)
            print()
        except KeyboardInterrupt:
            print('\n>>> Interrupted. Skip remaining chunks? (y/n): ', end='')
            ans = input().strip().lower()
            if ans == 'y':
                break
            continue
        except Exception as e:
            print('>>> Error processing chunk: ' + str(e))
            continue

        if not auto_mode and i < len(chunks):
            print('\nPress Enter for next chunk (or type \\q to stop): ', end='')
            nxt = input().strip()
            if nxt == '\\q':
                break
    print('>>> File chunk processing finished.')