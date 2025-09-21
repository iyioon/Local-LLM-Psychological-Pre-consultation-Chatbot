"""
Content moderation module for safety enforcement.
Students must complete TODO sections according to POLICY.md.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .config import SAFETY_MODE

logger = logging.getLogger(__name__)


class ModerationAction(Enum):
    """Possible moderation actions."""
    ALLOW = "allow"
    BLOCK = "block"
    SAFE_FALLBACK = "safe_fallback"


@dataclass
class ModerationResult:
    """Result of moderation check."""
    action: ModerationAction
    tags: List[str]  # Policy tags that were triggered
    reason: str  # Human-readable explanation
    confidence: float  # Confidence level (0-1)
    # Response to use if action != ALLOW
    fallback_response: Optional[str] = None


class Moderator:
    """Handles content moderation according to safety policy."""

    def __init__(self):
        """Initialize the moderator with safety rules."""
        self.safety_mode = SAFETY_MODE
        self._initialize_rules()

    def _initialize_rules(self):
        """Initialize moderation rules mirrored from POLICY.md."""

        self.crisis_keywords: List[str] = [
            "suicide", "suicidal", "suiside", "suicde", "sucid", "commit suicide", "kill myself",
            "killing myself", "kys", "kms", "end my life", "end it all", "take my life",
            "taking my life", "ending it all", "plan to die", "self-harm", "self harm", "hurt myself",
            "hurt my self", "cut myself", "cutting", "slit my wrists", "overdose", "over dose",
            "bleed out", "jump off", "unalive myself", "take pills", "take too many pills",
            "no reason to live", "no point to live", "lifes not worth living", "can't go on",
            "cant go on", "can't keep living", "life isn't worth living", "life is too painful",
            "life feels pointless", "life is pointless", "final goodbye", "goodbye forever",
            "good bye forever", "last message", "this is my last message", "ready to die",
            "tired of living", "want to disappear", "want to vanish"
        ]

        crisis_pattern_strings = [
            r"\b(?:want|plan|planning|going|ready|intending) to (?:die|end my life|kill myself|hurt myself)\b",
            r"\b(?:i|im|i'm) (?:going|planning|plan) to (?:jump|overdose|bleed out)\b",
            r"\b(?:thinking|thought|think) about (?:suicide|ending it|ending my life)\b",
            r"\b(?:thinking|thought|think) about (?:taking|swallowing) (?:a|the)? ?(?:bunch|lot|handful) of pills\b",
            r"\bno (?:reason|point|purpose) to (?:live|keep living|go on)\b",
            r"\b(?:tonight|tomorrow|this week) (?:i|i'm|im) (?:will|gonna|going to) (?:end it|end my life|kill myself)\b",
            r"\b(?:i|im|i'm) (?:so )?(?:done|finished) with (?:life|living)\b",
            r"\b(?:goodbye|farewell) (?:forever|for good)\b",
            r"\b(?:can't|cannot) (?:handle|take|do) this (?:anymore|any longer)\b",
            r"\bwish (?:i were|i was|to be) dead\b",
            r"\b(?:i|im|i'm) better off dead\b",
            r"\bwonder if life is worth living\b",
            r"\b(?:life|living) (?:is|feels) (?:too )?(?:painful|pointless|worthless)\b",
            r"\b(?:cant|can't) (?:keep|go on) (?:living|going)\b",
            r"\b(?:sometimes|some days) i (?:wonder|think) if life is worth living\b"
        ]
        self.crisis_patterns: List[re.Pattern] = [
            re.compile(pattern, re.IGNORECASE) for pattern in crisis_pattern_strings
        ]

        self.medical_keywords: List[str] = [
            "diagnose", "diagnosis", "diagnostic test", "diagnos", "diagnoze", "diagnoise",
            "what condition", "mental disorder", "clinical evaluation", "medication", "medicine",
            "meds", "prescription", "rx", "dosage", "dose", "antidepressant", "anti depressant",
            "ssri", "ssris", "prozac", "zoloft", "zolof", "xanax", "xanex", "adderall",
            "mood stabilizer", "anti-anxiety pills", "side effects", "should i take meds",
            "medication dosage", "treatment plan", "panic attacks", "panic attack", "without prescription",
            "am i depressed", "bipolar", "bipoler", "schizophrenia", "adhd", "add", "ocd",
            "ptsd", "panic disorder", "panik disorder", "therapy prescription"
        ]

        medical_pattern_strings = [
            r"\b(prescribe|recommend|suggest) (medication|pills|drugs)\b",
            r"\b(?:can|could|will) you diagnose (?:me|this)\b",
            r"\bdo i have (?:depression|anxiety|bipolar|adhd|ocd|ptsd)\b",
            r"\bwhat (?:medication|medicine|pills) should i take\b",
            r"\b(?:should|can) i take (?:prozac|zoloft|xanax|antidepressants?)\b",
            r"\b(?:need|looking for) a (?:new )?prescription for\b",
            r"\bwhat is the (?:right|correct|best) dosage of\b",
            r"\bdoes this symptom mean i have\b",
            r"\bhow do i get prescribed (?:.+)\b",
            r"\bwhat treatment plan should i follow\b",
            r"\b(?:can|could|will) you prescribe (?:something|.+)\b",
            r"\bwhat'?s the dosage for\b",
            r"\bwithout (?:a )?prescription\b",
            r"\b(?:can|could|would) you write (?:me )?(?:a )?prescription\b",
            r"\bdo i need medication for\b",
            r"\bcan you give me (?:something|anything) for (?:my )?(?:panic attacks?|anxiety|depression)\b",
            r"\bwhat are the symptoms of (?:.+?)\b",
            r"\b(?:where|how) can i (?:get|buy) (?:meds|medication)\b"
        ]
        self.medical_patterns: List[re.Pattern] = [
            re.compile(pattern, re.IGNORECASE) for pattern in medical_pattern_strings
        ]

        self.harmful_content: Dict[str, List[str]] = {
            "violence": [
                "attack", "attak", "attack them", "stab", "shoot", "kill someone", "kill somebody",
                "hurt others", "hurt someone", "hurt somebody", "hurt the person", "hurt them", "beat up", "beat him up",
                "assault plan", "bomb making", "how to poison", "plan revenge"
            ],
            "illegal": [
                "buy drugs", "buy weed", "score drugs", "sell drugs", "counterfeit money", "fake money",
                "hack bank", "hack account", "steal credit card", "steal card info", "credit card fraud",
                "fraud scheme", "launder money", "dark web access", "smuggle weapons", "illegal firearm purchase"
            ],
            "harassment": [
                "hate speech", "bully", "bullying", "cyberbully", "cyber bully", "threaten someone",
                "harass", "harassment", "harass online", "harrass", "stalk", "dox", "spread rumors",
                "racial slur", "sexual harassment", "abusive message", "abuse them"
            ],
        }

        self.confidence_thresholds = {
            "strict": {
                "crisis": 0.3,
                "medical": 0.4,
                "harmful": 0.5,
            },
            "balanced": {
                "crisis": 0.8,
                "medical": 0.8,
                "harmful": 0.7,
            },
            "permissive": {
                "crisis": 0.86,
                "medical": 0.86,
                "harmful": 0.8,
            },
        }

        self.fallback_templates = {
            "crisis": """
I'm deeply concerned about what you're sharing. Your safety is my top priority, and I want you to know that help is available right now.

Please reach out to trained crisis counselors immediately:
- National Suicide Prevention Lifeline: 988 (24/7)
- Crisis Text Line: Text HOME to 741741

You deserve support and you do not have to face this alone. If you can, consider reaching out to someone you trust—a friend, family member, or mentor—so they can stay with you and help you connect with professional care. You might also use grounded practices like focusing on your breathing, holding a comforting object, or moving to a safe space while you wait for help. I can stay with you here and listen while you connect with additional support. Your life matters, and there are people ready to help you through this moment. Please let me know how I can keep supporting you safely.
            """,

            "medical": """
I understand you're looking for medical guidance, and I appreciate you reaching out. However, I'm not qualified to provide medical diagnoses or treatment recommendations.

For your health and safety, please consult with:
- A licensed psychiatrist or prescribing clinician for medication questions

While I can't make clinical decisions, I can help you prepare for your appointment by exploring how you're feeling, clarifying concerns you want to raise, and brainstorming supportive coping strategies to use in the meantime. Remember to bring a list of symptoms, current medications, and any side effects you're noticing when you meet with a professional. Let me know how I can support you emotionally or help you organize your thoughts so you feel confident connecting with qualified care.
            """,

            "harmful": """
I cannot and will not provide assistance with that request as it could potentially cause harm. This space is meant for supportive, ethical conversations, and I have to set a firm boundary when something could endanger you or someone else.

If you're feeling intense anger, resentment, or a desire to retaliate, it might help to pause and focus on what you're experiencing beneath those urges. We can explore safer ways to process those emotions, identify the needs that aren't being met, and consider constructive actions, such as setting boundaries, seeking mediation, or reaching out to supportive services. If you believe someone is in immediate danger, please contact local emergency services or trusted authorities who can intervene appropriately.

I'm here to listen and help you navigate what led to these feelings so we can look for healthier ways forward. Let me know if you'd like to talk about coping strategies, de-escalation techniques.
            """,

            "disclaimer": """
Welcome to the Psychological Pre-Consultation Support System.

IMPORTANT DISCLAIMER:
This is an AI support system designed to provide initial emotional support and guidance. Please note:
- I am not a licensed mental health professional or emergency service.
- I cannot diagnose conditions, prescribe medication, or provide treatment plans.
- If you share information suggesting danger, I will encourage you to contact emergency resources.
- I may make mistakes; please verify any critical information with a qualified professional.

When to Seek Immediate Help:
- You or someone else is in danger or experiencing a medical emergency.
- You're considering hurting yourself or another person.
- You're experiencing severe symptoms such as hallucinations, mania, or loss of control.
- You feel unable to stay safe where you are.

What I Can Offer:
- Compassionate, non-judgmental listening.
- Help organizing your thoughts before speaking with a professional.
- General coping strategies and grounding techniques.
- Gentle reminders about self-care and connecting with supportive people.

Your wellbeing is important. How can I support you today?
            """,
        }

        self.model_medical_advice_patterns: List[re.Pattern] = [
            re.compile(
                r"\bI (?:recommend|suggest|prescribe) (?:you )?(?:take|use|try)\b.*", re.IGNORECASE),
            re.compile(r"\b(?:take|start|begin|use|try|increase|decrease|stop) (?:your )?(?:medication|meds|prozac|zoloft|xanax|antidepressants?|ssri?s?)\b", re.IGNORECASE),
            re.compile(r"\b(?:take|use) (?:\d+ ?mg|milligrams?)\b",
                       re.IGNORECASE),
            re.compile(r"\bI can diagnose (?:you|this)\b", re.IGNORECASE),
            re.compile(
                r"\bthis means you have (?:depression|anxiety|bipolar|adhd|ocd|ptsd)\b", re.IGNORECASE),
        ]

        self.model_inappropriate_patterns: List[re.Pattern] = [
            re.compile(
                r"\byou should (?:hurt|harm|kill|attack) (?:yourself|someone)\b", re.IGNORECASE),
            re.compile(r"\b(?:let's|lets) get revenge\b", re.IGNORECASE),
        ]

    def _get_threshold(self, category: str) -> float:
        """Return the confidence threshold for the given category based on safety mode."""
        mode_config = self.confidence_thresholds.get(
            self.safety_mode, self.confidence_thresholds["balanced"])
        return mode_config.get(category, 1.0)

    def moderate(
        self,
        user_prompt: str,
        model_response: Optional[str] = None,
        context: Optional[List[Dict]] = None,
    ) -> ModerationResult:
        """
        Perform moderation on user input and/or model output.

        Args:
            user_prompt: The user's input text

        Returns:
            ModerationResult with action and explanation

        IMPLEMENTATION ORDER:
        1. Check crisis (highest priority - must not miss)
        2. Check medical (prevent harmful advice)
        3. Check harmful content (filter inappropriate)
        """

        # Example skeleton:
        # Step 1: Check for crisis indicators (highest priority)
        crisis_check = self._check_crisis(user_prompt)
        if crisis_check.action != ModerationAction.ALLOW:
            logger.warning(f"Crisis detected: {crisis_check.reason}")
            return crisis_check

        medical_check = self._check_medical(user_prompt)
        if medical_check.action != ModerationAction.ALLOW:
            logger.info(f"Medical boundary triggered: {medical_check.reason}")
            return medical_check

        harmful_check = self._check_harmful(user_prompt)
        if harmful_check.action != ModerationAction.ALLOW:
            logger.warning(f"Harmful content detected: {harmful_check.reason}")
            return harmful_check

        # If model response provided, check it
        if model_response:
            output_check = self._check_model_output(model_response)
            if output_check.action != ModerationAction.ALLOW:
                logger.warning(f"Output violation: {output_check.reason}")
                return output_check

        # Check context for concerning patterns
        if context:
            context_check = self._check_context_patterns(context)
            if context_check.action != ModerationAction.ALLOW:
                logger.info(f"Context concern: {context_check.reason}")
                return context_check

        # Default: Allow
        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="Content passes all safety checks",
            confidence=1.0,
        )

    def _check_crisis(self, text: str) -> ModerationResult:
        """Check user input for crisis indicators and escalate when needed."""

        text_lower = text.lower()
        if not text_lower.strip():
            return ModerationResult(
                action=ModerationAction.ALLOW,
                tags=[],
                reason="No user input provided for crisis screening",
                confidence=0.0,
            )

        keyword_hits = [kw for kw in self.crisis_keywords if kw in text_lower]
        pattern_hits = [
            pat.pattern for pat in self.crisis_patterns if pat.search(text)]

        confidence = 0.0
        if keyword_hits:
            confidence = max(confidence, 0.7)
        if pattern_hits:
            confidence = max(confidence, 0.85)
        if keyword_hits and pattern_hits:
            confidence = max(confidence, 0.9)

        threshold = self._get_threshold("crisis")
        if (keyword_hits or pattern_hits) and confidence >= threshold:
            reason_parts = []
            if keyword_hits:
                reason_parts.append(
                    f"keywords: {', '.join(sorted(set(keyword_hits)))}")
            if pattern_hits:
                reason_parts.append("pattern indicators present")
            reason = "Detected crisis indicators (" + \
                "; ".join(reason_parts) + ")"
            tags = ["crisis"]
            if keyword_hits:
                tags.append("crisis_keyword")
            if pattern_hits:
                tags.append("crisis_pattern")
            return ModerationResult(
                action=ModerationAction.BLOCK,
                tags=tags,
                reason=reason,
                confidence=confidence,
                fallback_response=self.fallback_templates["crisis"],
            )

        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No crisis indicators detected",
            confidence=confidence,
        )

    def _check_medical(self, text: str) -> ModerationResult:
        """Detect medical boundary violations and trigger safe fallback."""
        text_lower = text.lower()
        if not text_lower.strip():
            return ModerationResult(
                action=ModerationAction.ALLOW,
                tags=[],
                reason="No medical indicators detected",
                confidence=0.0,
            )

        keyword_hits = [kw for kw in self.medical_keywords if kw in text_lower]
        pattern_hits = [
            pat.pattern for pat in self.medical_patterns if pat.search(text)]

        confidence = 0.0
        if keyword_hits:
            confidence = max(confidence, 0.7)
        if pattern_hits:
            confidence = max(confidence, 0.85)
        if keyword_hits and pattern_hits:
            confidence = max(confidence, 0.9)

        threshold = self._get_threshold("medical")
        if (keyword_hits or pattern_hits) and confidence >= threshold:
            reason_parts = []
            if keyword_hits:
                reason_parts.append(
                    f"keywords: {', '.join(sorted(set(keyword_hits)))}")
            if pattern_hits:
                reason_parts.append("pattern indicators present")
            reason = "Detected medical boundary request (" + "; ".join(
                reason_parts) + ")"
            tags = ["medical"]
            if keyword_hits:
                tags.append("medical_keyword")
            if pattern_hits:
                tags.append("medical_pattern")
            return ModerationResult(
                action=ModerationAction.SAFE_FALLBACK,
                tags=tags,
                reason=reason,
                confidence=confidence,
                fallback_response=self.fallback_templates["medical"],
            )

        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="No medical requests detected",
            confidence=confidence,
        )

    def _check_harmful(self, text: str) -> ModerationResult:
        """Filter for harmful requests involving violence, illegality, or harassment."""

        text_lower = text.lower()
        if not text_lower.strip():
            return ModerationResult(
                action=ModerationAction.ALLOW,
                tags=[],
                reason="No harmful content detected",
                confidence=0.0,
            )

        triggered: Dict[str, List[str]] = {}
        for category, keywords in self.harmful_content.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                triggered[category] = matches

        confidence = 0.0
        if triggered:
            confidence = 0.75
            if sum(len(matches) for matches in triggered.values()) > 1:
                confidence = max(confidence, 0.85)

            threshold = self._get_threshold("harmful")
            if confidence >= threshold:
                tags = ["harmful"] + \
                    [f"harmful_{category}" for category in triggered]
                reason = "Harmful content detected in categories: " + ", ".join(
                    f"{category} (terms: {', '.join(sorted(set(matches)))})" for category, matches in triggered.items()
                )
                return ModerationResult(
                    action=ModerationAction.BLOCK,
                    tags=tags,
                    reason=reason,
                    confidence=confidence,
                    fallback_response=self.fallback_templates["harmful"],
                )

        if triggered:
            reason = "Harmful signals below threshold: " + ", ".join(
                f"{category} (terms: {', '.join(sorted(set(matches)))})" for category, matches in triggered.items()
            )
        else:
            reason = "No harmful content detected"

        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason=reason,
            confidence=confidence,
        )

    def _check_model_output(self, response: str) -> ModerationResult:
        """Audit model responses for disallowed advice or unsafe suggestions."""

        medical_flags = [
            pat.pattern for pat in self.model_medical_advice_patterns if pat.search(response)]
        harmful_flags = [
            pat.pattern for pat in self.model_inappropriate_patterns if pat.search(response)]

        if medical_flags:
            return ModerationResult(
                action=ModerationAction.SAFE_FALLBACK,
                tags=["model_medical_advice"],
                reason="Model output appears to provide medical advice or diagnosis",
                confidence=0.9,
                fallback_response=self.fallback_templates["medical"],
            )

        if harmful_flags:
            return ModerationResult(
                action=ModerationAction.SAFE_FALLBACK,
                tags=["model_inappropriate"],
                reason="Model output contains inappropriate or harmful suggestions",
                confidence=0.9,
                fallback_response=self.fallback_templates["harmful"],
            )

        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="Model output is appropriate",
            confidence=1.0,
        )

    def _check_context_patterns(self, context: List[Dict]) -> ModerationResult:

        # Check for escalation
        crisis_count = 0
        for turn in context:
            if turn.get("role") == "user":
                content = turn.get("content", "").lower()
                for keyword in self.crisis_keywords:
                    if keyword in content:
                        crisis_count += 1

        if crisis_count >= 3:
            return ModerationResult(
                action=ModerationAction.SAFE_FALLBACK,
                tags=["pattern_escalation", "repeated_crisis"],
                reason="Escalating crisis pattern detected",
                confidence=0.8,
                fallback_response=self.fallback_templates["crisis"],
            )

        return ModerationResult(
            action=ModerationAction.ALLOW,
            tags=[],
            reason="Conversation pattern is safe",
            confidence=1.0,
        )

    def get_disclaimer(self) -> str:
        """Get initial disclaimer."""
        return self.fallback_templates.get("disclaimer", "")


# Singleton instance
_moderator_instance = None


def get_moderator() -> Moderator:
    """Get singleton moderator instance."""
    global _moderator_instance
    if _moderator_instance is None:
        _moderator_instance = Moderator()
    return _moderator_instance
