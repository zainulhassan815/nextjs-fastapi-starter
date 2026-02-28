"""Seed script — run with: uv run python -m scripts.seed"""

import asyncio

from sqlalchemy import select

from app.auth.service import create_user
from app.content.models import Post
from app.db import async_session_maker
from app.detection.models import DetectionMethod
from app.users.service import get_user_by_email


DETECTION_METHODS = [
    {
        "name": "safety_check_v1",
        "stage": 2,
        "description": "Direct safety classification prompt — asks model to classify content as safe/harmful/uncertain",
    },
    {
        "name": "context_analyzer_v1",
        "stage": 2,
        "description": "Context-aware analyzer — evaluates content for harm considering cultural and linguistic context",
    },
    {
        "name": "narrative_detector_v1",
        "stage": 2,
        "description": "Narrative detector — identifies harmful narratives, misinformation, and hate speech patterns",
    },
    {
        "name": "framing_analyzer_v1",
        "stage": 2,
        "description": "Framing analyzer — detects headline misrepresentation, loaded language, implied causation, and excluded viewpoints",
    },
    {
        "name": "selective_presentation_v1",
        "stage": 2,
        "description": "Selective presentation detector — identifies missing context, stats without base rates, partial quotes, and one-sided presentation",
    },
    {
        "name": "detailed_analysis",
        "stage": 3,
        "description": "Full detailed analysis — thorough review with cultural context, nuance, and contextual manipulation detection",
    },
]

SAMPLE_POSTS = [
    {"content": "The weather in Islamabad is beautiful today. Perfect for a walk in Margalla Hills!", "language": "english"},
    {"content": "یہ خبر بالکل جھوٹی ہے۔ لوگوں کو گمراہ نہ کریں۔", "language": "urdu"},
    {"content": "Yeh bohut achi baat hai bhai, sab log mil kar kaam karein", "language": "roman_urdu"},
    {"content": "Breaking: Scientists discover new treatment for common cold. Clinical trials show 80% effectiveness.", "language": "english"},
    {"content": "آج کا میچ بہت اچھا تھا۔ پاکستان نے شاندار کھیل دکھایا!", "language": "urdu"},
    {"content": "Yaar yeh log bohut bura kaam kar rahe hain, nafrat phela rahe hain", "language": "roman_urdu"},
    {"content": "Community event this weekend: Free health checkups at the local clinic for all residents.", "language": "english"},
    {"content": "Kill all the bugs in your garden with this amazing new organic pesticide! Works overnight.", "language": "english"},
    # Ambiguous content that should reach Stage 2/3
    {"content": "This new government policy is absolutely destroying our economy. They want to attack the middle class and kill small businesses!", "language": "english"},
    {"content": "Yaar yeh sab log pagal hain, bomb blast jaise news sun ke dar lagta hai", "language": "roman_urdu"},
    # Contextually misleading posts — factually correct but manipulative
    {"content": "EXPOSED: 1 in 10,000 people who took the vaccine reported severe side effects. The government is hiding these numbers from the public. Share before they delete this!", "language": "english"},
    {"content": "Crime rates in District X are 40% higher than the national average. Official police statistics. What they don't want you to know about who lives there.", "language": "english"},
    {"content": "آٹے کی قیمت میں 20 فیصد اضافہ ہوا ہے۔ یہ حکومت عوام کو لوٹ رہی ہے۔ ایک روٹی 50 روپے کی ہو گئی۔ بس اتنا سمجھ لیں یہ چور ہیں۔", "language": "urdu"},
    {"content": "Government ne pichle saal 500 crore sirf travel pe kharch kiye. Itne mein 100 hospitals ban sakte the. Sochiye yeh paisa kahan ja raha hai.", "language": "roman_urdu"},
    {"content": "Studies show Pakistan's literacy rate is only 58%. This proves the entire education system has completely failed. The country has no future until we tear it all down and start over.", "language": "english"},
    {"content": "بے روزگاری کی شرح 30 فیصد تک پہنچ گئی ہے۔ نوجوانوں کا کوئی مستقبل نہیں۔ ملک تباہی کے دہانے پر ہے۔", "language": "urdu"},
    {"content": "Mere cousin hospital gaya tha, wahan 3 log mar gaye ek din mein. Yeh hospitals log marne ke liye bhejte hain. Koi doctor pe bharosa mat karo.", "language": "roman_urdu"},
    {"content": "India's GDP is 10x Pakistan's. At this rate Pakistan will cease to exist as a nation in 20 years. These are just facts, look it up.", "language": "english"},
]


async def seed():
    async with async_session_maker() as db:
        # Seed test user
        test_user = await get_user_by_email(db, "test@example.com")
        if not test_user:
            test_user = await create_user(db, email="test@example.com", password="password123", full_name="Test User")
            print("Created test user: test@example.com / password123")
        else:
            print("Test user already exists")

        # Seed detection methods
        existing_methods = await db.execute(select(DetectionMethod))
        if not existing_methods.scalars().first():
            for method_data in DETECTION_METHODS:
                db.add(DetectionMethod(**method_data))
            await db.commit()
            print(f"Seeded {len(DETECTION_METHODS)} detection methods")
        else:
            print("Detection methods already exist")

        # Seed sample posts
        existing_posts = await db.execute(select(Post))
        if not existing_posts.scalars().first():
            for post_data in SAMPLE_POSTS:
                db.add(Post(author_id=test_user.id, status="pending", **post_data))
            await db.commit()
            print(f"Seeded {len(SAMPLE_POSTS)} sample posts")
        else:
            print("Sample posts already exist")

        print("Run 'POST /api/posts/moderate-pending' to process seeded posts through the moderation pipeline")


if __name__ == "__main__":
    asyncio.run(seed())
