"""
Pydantic schema for AI motif coding of sports/fitness/nutrition videos

This schema defines structured output from OpenAI API
Focus: Sports, Fitness, Performance Science, Nutrition
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Quote(BaseModel):
    """Individual quote from transcript"""
    text: str = Field(description="Exact quote from transcript (max 200 chars)")
    context: str = Field(description="Why this quote is significant")


class MotifCoding(BaseModel):
    """
    Structured motif coding for sports/fitness/nutrition videos

    This schema captures key themes, topics, and insights from video transcripts
    """

    # ===== TRAINING & PERFORMANCE =====
    training_type: List[str] = Field(
        default_factory=list,
        description="Training types discussed: strength, endurance, HIIT, mobility, cardio, etc.",
        max_length=10
    )

    recovery_methods: List[str] = Field(
        default_factory=list,
        description="Recovery methods mentioned: ice bath, massage, sleep, stretching, etc.",
        max_length=10
    )

    equipment_mentioned: List[str] = Field(
        default_factory=list,
        description="Equipment or gear: weights, bands, machines, etc.",
        max_length=10
    )

    performance_metrics: List[str] = Field(
        default_factory=list,
        description="Metrics discussed: VO2 max, 1RM, body comp, etc.",
        max_length=5
    )

    # ===== NUTRITION =====
    nutrition_focus: bool = Field(
        description="Does the video have significant nutrition content?"
    )

    supplements_mentioned: List[str] = Field(
        default_factory=list,
        description="Supplements: protein, creatine, vitamins, pre-workout, etc.",
        max_length=10
    )

    diet_type: Optional[str] = Field(
        default=None,
        description="Diet type if mentioned: keto, paleo, vegan, carnivore, mediterranean, etc."
    )

    meal_timing_discussed: bool = Field(
        default=False,
        description="Discusses meal timing, fasting, or nutrient timing?"
    )

    # ===== CREDIBILITY & SCIENCE =====
    cites_research: bool = Field(
        description="Does video cite scientific studies or research?"
    )

    expert_featured: bool = Field(
        description="Features credentialed expert (coach, scientist, doctor, pro athlete)?"
    )

    studies_mentioned: List[str] = Field(
        default_factory=list,
        description="Specific studies, researchers, or institutions mentioned",
        max_length=5
    )

    # ===== CONTENT CHARACTERISTICS =====
    primary_topic: str = Field(
        description="Main topic: training, nutrition, recovery, mindset, competition, etc."
    )

    target_audience: str = Field(
        description="Target audience: beginners, intermediate, advanced, athletes, general fitness"
    )

    actionable_advice: bool = Field(
        description="Provides specific actionable steps/protocols?"
    )

    product_promotion: bool = Field(
        description="Promotes products or services?"
    )

    content_quality: str = Field(
        description="Quality based on depth and accuracy: high/medium/low"
    )

    # ===== KEY INSIGHTS =====
    key_quotes: List[Quote] = Field(
        default_factory=list,
        max_length=5,
        description="Most important/insightful quotes (max 5)"
    )

    main_claims: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Primary claims or conclusions of the video"
    )

    # ===== ADDITIONAL FLAGS =====
    mentions_injury: bool = Field(
        default=False,
        description="Discusses injury prevention or rehabilitation?"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "training_type": ["strength", "HIIT"],
                "recovery_methods": ["ice bath", "massage"],
                "equipment_mentioned": ["barbell", "resistance bands"],
                "performance_metrics": ["1RM", "body fat percentage"],
                "nutrition_focus": True,
                "supplements_mentioned": ["protein", "creatine"],
                "diet_type": None,
                "meal_timing_discussed": True,
                "cites_research": True,
                "expert_featured": True,
                "studies_mentioned": ["Stanford sleep study"],
                "primary_topic": "training",
                "target_audience": "intermediate",
                "actionable_advice": True,
                "product_promotion": False,
                "content_quality": "high",
                "key_quotes": [
                    {
                        "text": "Progressive overload is the key to muscle growth",
                        "context": "Main training principle discussed"
                    }
                ],
                "main_claims": ["Consistency beats intensity", "Recovery is crucial"],
                "mentions_injury": False
            }
        }


if __name__ == "__main__":
    # Test schema
    print("Motif Coding Schema Defined")
    print(f"Fields: {len(MotifCoding.model_fields)}")
    print("\nField names:")
    for field in MotifCoding.model_fields:
        print(f"  - {field}")
