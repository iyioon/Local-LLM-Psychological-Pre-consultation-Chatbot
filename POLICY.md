# Safety and Moderation Policy

## Overview

This document defines the safety boundaries and moderation policies for the psychological pre-consultation CUI system. The system prioritizes user safety while providing supportive dialogue within appropriate boundaries.

## Policy Framework

### 1. Safety Categories

#### 1.1 Crisis Situations

**Definition**: Immediate risk of harm to self or others

**Implementation Requirements**:

- Maintain at least 20 crisis keywords covering direct, implicit, and misspelled expressions
- Maintain diverse regex patterns that capture plans, timelines, and negation cues
- Use highest sensitivity in all safety modes

```python
# Student Implementation Required:
# Minimum 20 keywords covering various crisis expressions
CRISIS_KEYWORDS = [
    # Direct suicide mentions and misspellings
    "suicide", "suicidal", "suiside", "suicde", "sucid", "commit suicide", "kill myself", "killing myself", "kys", "kms",
    "end my life", "end it all", "take my life", "taking my life", "ending it all", "plan to die",

    # Self-harm expressions and methods
    "self-harm", "self harm", "hurt myself", "hurt my self", "cut myself", "cutting", "slit my wrists", "overdose", "over dose",
    "bleed out", "jump off", "unalive myself", "take pills", "take too many pills",

    # Imminent danger indicators and emotional crisis expressions
    "no reason to live", "no point to live", "lifes not worth living", "can't go on", "cant go on", "can't keep living", "life isn't worth living",
    "life is too painful", "life feels pointless", "life is pointless", "final goodbye", "goodbye forever", "good bye forever",
    "last message", "this is my last message", "ready to die", "tired of living", "want to disappear", "want to vanish"
]

# Minimum 8 regex patterns for complex expressions
CRISIS_PATTERNS = [
    # Pattern-based detection for implicit and explicit high-risk statements
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
```

**Action**: `BLOCK` + Crisis referral

**Example Response Template (Complete this with 150-200 words)**:

```text
I'm deeply concerned about what you're sharing. Your safety is my top priority, and I want you to know that help is available right now.

Please reach out to trained crisis counselors immediately:
- National Suicide Prevention Lifeline: 988 (24/7)
- Crisis Text Line: Text HOME to 741741

You deserve support and you do not have to face this alone. If you can, consider reaching out to someone you trust—a friend, family member, or mentor—so they can stay with you and help you connect with professional care. You might also use grounded practices like focusing on your breathing, holding a comforting object, or moving to a safe space while you wait for help. I can stay with you here and listen while you connect with additional support. Your life matters, and there are people ready to help you through this moment. Please let me know how I can keep supporting you safely.
```

#### 1.2 Medical Requests

**Definition**: Requests for diagnosis, treatment, or medication advice

**Implementation Requirements**:

- Maintain comprehensive medical boundary keywords across diagnoses, medication, and condition terms
- Maintain regex patterns for prescriptions, diagnoses, and treatment seeking
- Use SAFE_FALLBACK action

```python
# Student Implementation Required:
# Minimum 20 keywords
MEDICAL_INDICATORS = [
    # Diagnosis and assessment requests
    "diagnose", "diagnosis", "diagnostic test", "diagnos", "diagnoze", "diagnoise", "what condition", "mental disorder", "clinical evaluation",

    # Medication and treatment terminology
    "medication", "medicine", "meds", "prescription", "rx", "dosage", "dose", "antidepressant", "anti depressant", "ssri", "ssris",
    "prozac", "zoloft", "zolof", "xanax", "xanex", "adderall", "mood stabilizer",
    "anti-anxiety pills", "side effects", "should i take meds", "medication dosage", "treatment plan", "panic attacks", "panic attack", "without prescription",

    # Mental health specific conditions and questions
    "am i depressed", "bipolar", "bipoler", "schizophrenia", "adhd", "add", "ocd", "ptsd", "panic disorder", "panik disorder", "therapy prescription"
]

# Minimum 8 regex patterns for complex expressions
MEDICAL_PATTERNS = [
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
```

**Action**: `SAFE_FALLBACK`

**Response Template (Complete with structured format)**:

```text
I understand you're looking for medical guidance, and I appreciate you reaching out. However, I'm not qualified to provide medical diagnoses or treatment recommendations.

For your health and safety, please consult with:
- A licensed psychiatrist or prescribing clinician for medication questions

While I can't make clinical decisions, I can help you prepare for your appointment by exploring how you're feeling, clarifying concerns you want to raise, and brainstorming supportive coping strategies to use in the meantime. Remember to bring a list of symptoms, current medications, and any side effects you're noticing when you meet with a professional. Let me know how I can support you emotionally or help you organize your thoughts so you feel confident connecting with qualified care.
```

#### 1.3 Harmful Content

**Definition**: Violence, illegal activities, harassment

**Implementation Requirements**:

- Minimum 20 keywords
- Consider both direct and indirect expressions

```python
# Student Implementation Required:
HARMFUL_CATEGORIES = {
    "violence": [
        "attack", "attak", "attack them", "stab", "shoot", "kill someone", "kill somebody", "hurt others", "hurt someone",
        "hurt somebody", "hurt the person", "hurt them", "beat up", "beat him up", "assault plan", "bomb making", "how to poison",
        "plan revenge"
    ],

    "illegal": [
        "buy drugs", "buy weed", "score drugs", "sell drugs", "counterfeit money", "fake money", "hack bank", "hack account",
        "steal credit card", "steal card info", "credit card fraud", "fraud scheme", "launder money", "dark web access",
        "smuggle weapons", "illegal firearm purchase"
    ],

    "harassment": [
        "hate speech", "bully", "bullying", "cyberbully", "cyber bully", "threaten someone", "harass", "harassment", "harass online",
        "harrass", "stalk", "dox", "spread rumors", "racial slur", "sexual harassment", "abusive message", "abuse them"
    ]
}
```

**Action**: `BLOCK`

**Example Response Template (Complete this with 150-200 words)**:

```text
I cannot and will not provide assistance with that request as it could potentially cause harm. This space is meant for supportive, ethical conversations, and I have to set a firm boundary when something could endanger you or someone else.

If you're feeling intense anger, resentment, or a desire to retaliate, it might help to pause and focus on what you're experiencing beneath those urges. We can explore safer ways to process those emotions, identify the needs that aren't being met, and consider constructive actions, such as setting boundaries, seeking mediation, or reaching out to supportive services. If you believe someone is in immediate danger, please contact local emergency services or trusted authorities who can intervene appropriately.

I'm here to listen and help you navigate what led to these feelings so we can look for healthier ways forward. Let me know if you'd like to talk about coping strategies, de-escalation techniques.
```

#### 1.4 Supportive Dialogue

**Definition**: General emotional support, stress discussion, life challenges

**Acceptable Topics** (define at least 10):

```python
SUPPORTIVE_TOPICS = [
    "stress management",
    "relationship challenges",
    "work-life balance",
    "anxiety coping",
    "grief and loss",
    "coping with loneliness",
    "mindfulness practice",
    "self-compassion exercises",
    "sleep hygiene",
    "managing burnout",
    "building resilience",
    "goal setting",
    "communication skills",
    "emotional regulation"
]
```

**Action**: `ALLOW`

### 2. Action Definitions

- **ALLOW**: Proceed with normal dialogue
- **BLOCK**: Refuse interaction with safety message and resources
- **SAFE_FALLBACK**: Redirect to appropriate resources while maintaining support

### 3. Confidence and Ambiguity

**Confidence Score Guidelines**:

- Keyword match: 0.7 confidence
- Pattern match: 0.8-0.9 confidence
- Multiple matches: Use maximum confidence

**Implementation Requirements**:

- Maintain calibrated confidence thresholds for each safety mode and document tuning rationale
- Prioritize crisis safeguards when multiple categories fire to minimize missed high-risk cases

**Confidence Thresholds by Safety Mode**:

```python
CONFIDENCE_THRESHOLDS = {
    "strict": {
        # Maximum sensitivity - err on side of caution
        "crisis": 0.3,   # Very low threshold for crisis detection
        "medical": 0.4,  # Low threshold for medical boundaries
        "harmful": 0.5   # Moderate threshold for harmful content
    },
    "balanced": {
        # Balanced approach for production use
        "crisis": 0.8,
        "medical": 0.8,
        "harmful": 0.7,
    },
    "permissive": {
        # Minimum filtering - only clear violations
        "crisis": 0.86,
        "medical": 0.86,
        "harmful": 0.8,
    }
}
```

### 5. Response Templates

```python
RESPONSE_TEMPLATES = {
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

I'm here to listen and help you navigate what led to these feelings so we can look for healthier ways forward. Let me know if you'd like to talk about coping strategies, de-escalation techniques, or resources for professional support that keep everyone safe.
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
    """
}
```
