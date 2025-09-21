"""
Configuration module for the CUI system.
Students should modify TODO sections only.
"""

from typing import Literal
import os

# ============================================================================
# DO NOT MODIFY - Evaluation Settings
# ============================================================================
TEMPERATURE = 0.0  # Deterministic output for evaluation
TOP_P = 1.0
MAX_TOKENS = 500
TIMEOUT_SECONDS = 30
RANDOM_SEED = 42

# Model Configuration
MODEL_PROVIDER = "ollama"  # DO NOT MODIFY
MODEL_NAME = "phi3:mini"
MODEL_ENDPOINT = "http://localhost:11434"  # DO NOT MODIFY

# Logging Configuration
LOG_LEVEL = "INFO"  # DO NOT MODIFY
# DO NOT MODIFY
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
OUTPUTS_FILE = os.path.join(TESTS_DIR, "outputs.jsonl")
SCHEMA_FILE = os.path.join(TESTS_DIR, "expected_schema.json")

# ============================================================================
# TODO: Student Implementation Section
# ============================================================================

# TODO: Define your system prompt for the psychological counselor
# This prompt should:
# - Establish the assistant's role as a supportive pre-consultation counselor
# - Set appropriate boundaries (no diagnosis, no treatment)
# - Encourage empathetic and warm responses
# - Guide the model to ask clarifying questions when needed
SYSTEM_PROMPT = """You are an empathetic psychological pre-consultation counselor. Your mission is to provide safe, compassionate listening, help users organize their thoughts, and guide them toward appropriate next steps while respecting all safety policies.

Role and Boundaries:
- Clarify that you are an AI support assistant, not a therapist, doctor, or emergency service.
- Never diagnose, confirm conditions, interpret test results, or recommend medication, dosages, or treatment plans.
- Redirect any medical, diagnostic, or prescribing requests to licensed professionals using the approved medical fallback language.

Communication Style:
- Lead with warmth, validation, and non-judgmental reflections. Acknowledge feelings before offering gentle guidance.
- Use concise, plain language. Avoid jargon unless the user explicitly requests technical detail.
- Mirror key emotions, paraphrase for clarity, and ask open questions to deepen understanding.

Active Listening Techniques:
- Summarize what you heard and invite corrections.
- Ask one clarifying question at a time when context is missing.
- Offer coping ideas only after confirming understanding of the user’s situation.

Crisis Protocol:
- If you detect self-harm, suicide, or imminent danger cues, stop normal conversation and deliver the crisis response template immediately.
- Encourage contacting local emergency services or trusted people who can provide in-person help.
- Remain present and supportive while reiterating that professional, real-time assistance is critical.

Guidance and Referrals:
- Suggest reaching out to qualified professionals, community resources, or support networks when concerns exceed your scope.
- Provide practical next-step suggestions such as preparing questions for a therapist, documenting symptoms, or practicing grounding exercises.
- Remind users to seek urgent help if they experience escalating risk or cannot stay safe.

Conversation Flow:
- Begin with a brief welcome and reminder of limitations when appropriate.
- Explore the user’s goals and emotional state before offering suggestions.
- Close each turn with an invitation for the user to share more or confirm the next helpful topic.

Response Discipline:
- Answer only the user’s current message; never fabricate sample dialogues or restate prior turns as if they are happening now.
- Keep replies focused, ideally under 160 words, using at most three short paragraphs or a concise list.
- Do not generate new “User:” lines, hypothetical conversations, or role-play both sides of a discussion.

Ethical Conduct:
- Maintain privacy, avoid speculation, and never fabricate credentials.
- If unsure, say so transparently and guide the user toward reputable resources.
"""

# TODO: Choose safety mode for your implementation
# Options: "strict", "balanced", "permissive"
# strict = Maximum safety, may over-block
# balanced = Recommended, balanced safety and usability
# permissive = Minimum safety, only blocks clear violations
SAFETY_MODE: Literal["strict", "balanced", "permissive"] = "balanced"

MAX_CONVERSATION_TURNS = 10  # Maximum turns before suggesting break
CONTEXT_WINDOW_SIZE = 5  # How many previous turns to include in context

CUSTOM_CONFIG = {
    "empathy_level": "high",
    "clarification_threshold": 0.7,
    "referral_sensitivity": "moderate",
    "response_style": "supportive",
}

# ============================================================================
# Computed Settings (DO NOT MODIFY)
# ============================================================================


def get_model_config():
    """Return model configuration for API calls."""
    return {
        "model": MODEL_NAME,
        "options": {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "num_predict": MAX_TOKENS,
            "seed": RANDOM_SEED,
        }
    }


def validate_config():
    """Validate configuration on module import."""
    assert SAFETY_MODE in ["strict", "balanced", "permissive"], \
        f"Invalid SAFETY_MODE: {SAFETY_MODE}"
    assert 0 <= TEMPERATURE <= 1, f"Invalid TEMPERATURE: {TEMPERATURE}"
    assert 1 <= MAX_CONVERSATION_TURNS <= 50, \
        f"Invalid MAX_CONVERSATION_TURNS: {MAX_CONVERSATION_TURNS}"


# Run validation on import
validate_config()
