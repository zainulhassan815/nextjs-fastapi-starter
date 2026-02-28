import anthropic

from app.config import settings

_client: anthropic.AsyncAnthropic | None = None


def get_claude_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def complete(
    prompt: str,
    system: str = "You are a helpful assistant.",
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4096,
) -> str:
    client = get_claude_client()
    message = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
