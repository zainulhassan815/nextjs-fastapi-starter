import json
import logging
import random
import re

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.content.models import Post
from app.db import async_session_maker
from app.moderation.models import ModerationResult
from app.moderation.prompts import STAGE_2_PROMPTS, STAGE_3_PROMPT

logger = logging.getLogger(__name__)

# Harmful keyword lists (multilingual)
HARMFUL_KEYWORDS_EN = {"kill", "murder", "bomb", "attack", "terrorism", "hate", "slur", "destroy"}
HARMFUL_KEYWORDS_UR = {"قتل", "بم", "حملہ", "دہشت", "نفرت", "تباہ"}
HARMFUL_KEYWORDS_RU = {"maar", "qatal", "bomb", "hamla", "dehshat", "nafrat", "tabah"}
ALL_KEYWORDS = HARMFUL_KEYWORDS_EN | HARMFUL_KEYWORDS_UR | HARMFUL_KEYWORDS_RU


def _keyword_scan(content: str) -> tuple[int, list[str]]:
    """Stage 1: Count harmful keyword matches. Returns (count, matched_keywords)."""
    content_lower = content.lower()
    words = set(re.findall(r"\w+", content_lower))
    matched = [kw for kw in ALL_KEYWORDS if kw in words or kw in content_lower]
    return len(matched), matched


def _parse_claude_response(text: str) -> dict:
    """Extract JSON from Claude's response."""
    try:
        # Try direct JSON parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Try extracting JSON from markdown code block
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"verdict": "uncertain", "confidence": 0.0, "reasoning": "Failed to parse AI response"}


async def _call_claude(prompt: str, model: str = "claude-haiku-4-5-20241022") -> tuple[str, float]:
    """Call Claude API. Returns (response_text, estimated_cost_usd)."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    message = await client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    response_text = message.content[0].text
    # Estimate cost: input + output tokens
    input_cost = message.usage.input_tokens * 0.00000025  # Haiku pricing
    output_cost = message.usage.output_tokens * 0.00000125
    cost = input_cost + output_cost
    return response_text, cost


async def _run_stage_1(db: AsyncSession, post: Post) -> ModerationResult:
    """Stage 1: Keyword scan — free, instant."""
    hit_count, matched = _keyword_scan(post.content)
    if hit_count >= 3:
        verdict = "harmful"
    elif hit_count == 0:
        verdict = "safe"
    else:
        verdict = "uncertain"
    confidence = min(hit_count / 5.0, 1.0) if hit_count > 0 else 0.9
    reasoning = f"Keyword scan: {hit_count} hits" + (f" ({', '.join(matched[:5])})" if matched else "")
    result = ModerationResult(
        post_id=post.id,
        stage=1,
        method_name="keyword_scan",
        verdict=verdict,
        confidence=confidence,
        reasoning=reasoning,
        cost_usd=0.0,
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)
    return result


async def _run_stage_2(db: AsyncSession, post: Post) -> ModerationResult:
    """Stage 2: Lightweight Claude with rotated prompt."""
    from app.detection.service import record_usage, select_method

    method = await select_method(db, stage=2)
    method_name = method.name if method else random.choice(list(STAGE_2_PROMPTS.keys()))
    prompt_template = STAGE_2_PROMPTS.get(method_name, list(STAGE_2_PROMPTS.values())[0])
    prompt = prompt_template.format(content=post.content, language=post.language)

    # Check budget before calling Claude
    from app.budget.service import check_budget_remaining, log_cost

    has_budget = await check_budget_remaining(db)
    if not has_budget:
        logger.warning("Budget exceeded, skipping Stage 2 AI call for post %d", post.id)
        result = ModerationResult(
            post_id=post.id,
            stage=2,
            method_name=method_name,
            verdict="uncertain",
            confidence=0.0,
            reasoning="Budget exceeded — skipped AI analysis",
            cost_usd=0.0,
        )
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result

    response_text, cost = await _call_claude(prompt)
    parsed = _parse_claude_response(response_text)

    result = ModerationResult(
        post_id=post.id,
        stage=2,
        method_name=method_name,
        verdict=parsed.get("verdict", "uncertain"),
        confidence=parsed.get("confidence", 0.0),
        reasoning=parsed.get("reasoning", ""),
        cost_usd=cost,
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)

    # Record detection method usage and cost
    if method:
        await record_usage(db, method.id)
    await log_cost(db, cost, stage=2, post_id=post.id)

    return result


async def _run_stage_3(db: AsyncSession, post: Post, previous_reasoning: str) -> ModerationResult:
    """Stage 3: Detailed Claude analysis."""
    from app.budget.service import check_budget_remaining, log_cost

    has_budget = await check_budget_remaining(db)
    if not has_budget:
        logger.warning("Budget exceeded, skipping Stage 3 AI call for post %d", post.id)
        result = ModerationResult(
            post_id=post.id,
            stage=3,
            method_name="detailed_analysis",
            verdict="escalate",
            confidence=0.0,
            reasoning="Budget exceeded — escalating to human review",
            cost_usd=0.0,
        )
        db.add(result)
        await db.commit()
        await db.refresh(result)
        return result

    prompt = STAGE_3_PROMPT.format(
        content=post.content,
        language=post.language,
        previous_reasoning=previous_reasoning,
    )
    response_text, cost = await _call_claude(prompt)
    parsed = _parse_claude_response(response_text)

    result = ModerationResult(
        post_id=post.id,
        stage=3,
        method_name="detailed_analysis",
        verdict=parsed.get("verdict", "escalate"),
        confidence=parsed.get("confidence", 0.0),
        reasoning=parsed.get("reasoning", ""),
        cost_usd=cost,
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)

    await log_cost(db, cost, stage=3, post_id=post.id)
    return result


async def run_moderation_pipeline(post_id: int) -> None:
    """Run the full 3-stage moderation pipeline. Called as a background task."""
    async with async_session_maker() as db:
        post = await db.get(Post, post_id)
        if not post:
            logger.error("Post %d not found for moderation", post_id)
            return

        try:
            # Stage 1: Keyword scan
            stage1 = await _run_stage_1(db, post)
            if stage1.verdict == "safe":
                post.status = "safe"
                await db.commit()
                return
            if stage1.verdict == "harmful":
                post.status = "harmful"
                await db.commit()
                return

            # Stage 2: Lightweight Claude
            stage2 = await _run_stage_2(db, post)
            if stage2.verdict == "safe":
                post.status = "safe"
                await db.commit()
                return
            if stage2.verdict == "harmful":
                post.status = "harmful"
                await db.commit()
                return

            # Stage 3: Detailed Claude
            stage3 = await _run_stage_3(db, post, previous_reasoning=stage2.reasoning or "")
            if stage3.verdict == "escalate":
                post.status = "escalated"
                # Create review queue entry
                from app.review.service import create_review_item

                await create_review_item(db, post_id=post.id, reasoning=stage3.reasoning or "")
            else:
                post.status = stage3.verdict  # safe or harmful
            await db.commit()

        except Exception:
            logger.exception("Moderation pipeline failed for post %d", post_id)
            post.status = "escalated"
            await db.commit()


async def get_moderation_results(db: AsyncSession, post_id: int) -> list[ModerationResult]:
    """Get all moderation results for a post."""
    result = await db.execute(
        select(ModerationResult).where(ModerationResult.post_id == post_id).order_by(ModerationResult.stage)
    )
    return list(result.scalars().all())
