from context_manager import ContextManager

def test_add_message_and_trim_by_count() -> None:
    ctx = ContextManager(max_messages=2)
    ctx.add_message('user', 'hello')
    ctx.add_message('assistant', 'hi')
    ctx.add_message('user', 'how are you')
    assert len(ctx.history) == 2
    assert ctx.history[0]['content'] == 'hi'

def test_trim_by_chars() -> None:
    ctx = ContextManager(max_chars=10)
    ctx.add_message('user', '12345678901')
    assert len(ctx.history) == 1
    assert ctx.history[0]['content'] == '2345678901'

def test_trim_both_limits() -> None:
    ctx = ContextManager(max_messages=3, max_chars=15)
    ctx.add_message('user', 'hello')
    ctx.add_message('assistant', 'world')
    ctx.add_message('user', '!!')
    ctx.add_message('user', 'longertext')
    assert len(ctx.history) == 2
    total = sum(len(m['content']) for m in ctx.history)
    assert total <= 15

def test_reset() -> None:
    ctx = ContextManager()
    ctx.add_message('user', 'test')
    ctx.reset()
    assert ctx.history == []