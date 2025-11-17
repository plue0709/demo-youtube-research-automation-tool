"""
OpenAI integration for motif coding

Uses OpenAI Structured Outputs to guarantee valid JSON
"""

import os
import logging
from openai import OpenAI
from typing import Dict
from dotenv import load_dotenv
from motif_schema import MotifCoding

load_dotenv()
logger = logging.getLogger(__name__)


class MotifCoder:
    """
    OpenAI-powered motif coding for video transcripts

    CRITICAL REQUIREMENTS:
    - Uses Structured Outputs (NOT JSON mode)
    - Zero tolerance for malformed JSON
    - Deterministic outputs matching schema exactly
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Cost-effective for MVP
        # Alternative: "gpt-4o" for better quality but ~10x cost

    def code_transcript(self, transcript_text: str, video_metadata: Dict) -> MotifCoding:
        """
        Main coding function

        Args:
            transcript_text: Full transcript text
            video_metadata: Dict with title, channel, duration

        Returns:
            MotifCoding: Pydantic model with structured data

        CRITICAL: Uses OpenAI Structured Outputs feature
        This GUARANTEES valid JSON matching schema
        """

        # Truncate transcript if too long
        max_length = 50000  # ~12k tokens
        if len(transcript_text) > max_length:
            logger.warning(f"Transcript too long ({len(transcript_text)} chars), truncating")
            transcript_text = transcript_text[:max_length] + "\n\n[TRUNCATED]"

        # Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(transcript_text, video_metadata)

        try:
            # CRITICAL: Use beta.chat.completions.parse for structured outputs
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=MotifCoding,  # Pydantic model
                temperature=0.1  # Low temperature for consistency
            )

            # This is guaranteed to match schema
            coding_result = response.choices[0].message.parsed

            # Log token usage
            usage = response.usage
            logger.info(
                f"AI coding complete. "
                f"Tokens: {usage.total_tokens} "
                f"(prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})"
            )

            return coding_result

        except Exception as e:
            logger.error(f"AI coding failed: {e}")
            raise

    def _build_system_prompt(self) -> str:
        """
        System prompt defining the task

        CRITICAL: Clear instructions for deterministic outputs
        """
        return """You are a research analyst specializing in coding YouTube transcripts about sports, fitness, performance science, and nutrition.

Your task is to analyze video transcripts and extract structured information according to a provided schema.

CRITICAL RULES:
1. Only include information EXPLICITLY mentioned in the transcript
2. Do not infer or assume information not stated
3. Be precise with categorization
4. For quotes, use exact wording from transcript (max 200 chars)
5. When unsure, leave field empty or mark as False
6. Maintain objectivity - don't add personal opinions

QUALITY CRITERIA:
- High quality: Cites research, features experts, provides detailed protocols
- Medium quality: Provides general advice, some specific details
- Low quality: Vague advice, promotional, lacks substance

TARGET AUDIENCE CRITERIA:
- Beginners: Basic concepts, introductory advice
- Intermediate: Assumes some knowledge, more detailed
- Advanced: Technical, assumes expertise
- Athletes: Performance-focused, competitive context
- General fitness: Broad appeal, practical advice"""

    def _build_user_prompt(self, transcript_text: str, metadata: Dict) -> str:
        """
        User prompt with transcript and metadata
        """
        prompt = f"""Analyze the following YouTube video and extract structured motif information.

VIDEO METADATA:
Title: {metadata.get('title', 'Unknown')}
Channel: {metadata.get('channel', 'Unknown')}
Duration: {metadata.get('duration', 0)} seconds

TRANSCRIPT:
{transcript_text}

Extract all relevant information according to the schema. Be thorough but precise."""

        return prompt

    def get_token_usage_estimate(self, transcript_text: str) -> Dict[str, int]:
        """
        Estimate token usage (rough approximation)

        Returns dict with estimated tokens and cost
        """
        # Rough estimate: 1 token ≈ 4 characters
        transcript_tokens = len(transcript_text) // 4
        system_tokens = 200  # System prompt
        completion_tokens = 800  # Typical completion

        total_tokens = transcript_tokens + system_tokens + completion_tokens

        # Cost estimation (GPT-4o-mini pricing)
        input_cost_per_1m = 0.15  # $0.15 per 1M input tokens
        output_cost_per_1m = 0.60  # $0.60 per 1M output tokens

        input_cost = (transcript_tokens + system_tokens) * input_cost_per_1m / 1_000_000
        output_cost = completion_tokens * output_cost_per_1m / 1_000_000
        total_cost = input_cost + output_cost

        return {
            'estimated_total_tokens': total_tokens,
            'estimated_cost_usd': round(total_cost, 4),
            'transcript_tokens': transcript_tokens,
            'completion_tokens': completion_tokens
        }


if __name__ == "__main__":
    # Test with sample transcript
    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("Testing OpenAI Motif Coder")
    print("=" * 70)

    sample_transcript = """
    Today we're talking about recovery methods for athletes.
    Ice baths are one of the most popular recovery techniques used by professional athletes.
    Research from Stanford University shows that cold exposure can reduce inflammation
    and speed up recovery time. I recommend doing ice baths for 10-15 minutes
    after intense training sessions.

    Also, don't forget about proper nutrition - protein intake is crucial for muscle recovery.
    I typically recommend 1.6 to 2.2 grams of protein per kilogram of body weight.
    Creatine is another supplement that has strong research backing.

    Progressive overload is the foundation of strength training. You need to gradually
    increase the weight, reps, or sets over time to see continued progress.
    """

    sample_metadata = {
        'title': 'Best Recovery Methods for Athletes',
        'channel': 'Fitness Science',
        'duration': 600
    }

    coder = MotifCoder()

    print("\n📊 Token Usage Estimate:")
    estimate = coder.get_token_usage_estimate(sample_transcript)
    for key, value in estimate.items():
        print(f"   {key}: {value}")

    print("\n🤖 Running AI Coding...")
    result = coder.code_transcript(sample_transcript, sample_metadata)

    print("\n✅ Coding Result:")
    print(f"   Primary topic: {result.primary_topic}")
    print(f"   Nutrition focus: {result.nutrition_focus}")
    print(f"   Cites research: {result.cites_research}")
    print(f"   Content quality: {result.content_quality}")
    print(f"   Recovery methods: {result.recovery_methods}")
    print(f"   Supplements: {result.supplements_mentioned}")

    print("\n📝 Key quotes:")
    for quote in result.key_quotes:
        print(f"   - {quote.text}")

    print("\n" + "=" * 70)
    print("✅ Test Complete!")
