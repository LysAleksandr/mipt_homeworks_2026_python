import os
from typing import cast, Any, Dict
from openai import OpenAI
from context_manager import ContextManager
from file_utils import replace_file_attachments
from chunk_processor import file_chunk_mode
from openai.types.chat import ChatCompletionChunk
from openai.types.chat import ChatCompletionMessageParam

def clear_screen() -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

class Chat:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.client = OpenAI(
            base_url=config['api_host'],
            api_key=config['api_key'],
        )
        self.model = config.get('model', 'gemma3:270m')
        self.temperature = config.get('temperature', 0.7)
        self.system_prompt = config.get('system_prompt', 'You are a helpful assistant.')
        self.context = ContextManager(
            max_messages=config.get('limit_message'),
            max_chars=config.get('limit_chars'),
            system_prompt=self.system_prompt,
        )

    def run(self) -> None:
        print('GigaVibeMiptCode Chat. Type \\q to exit, /reset to clear history.')
        print('Use @::filepath:: to attach files.')
        while True:
            user_input = input('>>> ').strip()

            if not user_input:
                continue

            if user_input == '\\q':
                print('Goodbye!')
                break
            if user_input == '/reset':
                self.context.reset()
                clear_screen()
                print('History cleared.')
                continue
            if user_input.startswith('/file_chunk'):
                file_chunk_mode(self.client, self.model, self.system_prompt)
                continue

            processed, errors = replace_file_attachments(user_input)
            for err in errors:
                print('[Warning] ' + err)

            self.context.add_message('user', processed)

            messages = [{'role': 'system', 'content': self.system_prompt}]
            messages.extend(self.context.get_messages())

            full_response = ''
            print('Assistant: ', end='', flush=True)
            try:
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=cast(list[ChatCompletionMessageParam], messages),
                    temperature=self.temperature,
                    stream=True,
                )
                for chunk in stream:
                    if isinstance(chunk, ChatCompletionChunk):
                        content = chunk.choices[0].delta.content or ''
                        print(content, end='', flush=True)
                        full_response += content
                print()
            except KeyboardInterrupt:
                print('\n[Interrupted]')
                if self.context.history and self.context.history[-1]['role'] == 'user':
                    self.context.history.pop()
                continue
            except Exception as e:
                print('\n[Error] ' + str(e))
                if self.context.history and self.context.history[-1]['role'] == 'user':
                    self.context.history.pop()
                continue

            if full_response:
                self.context.add_message('assistant', full_response)