'''
Evaluation Dialogue Quality

Model Configuration: gpt-4o-mini
Author: 
    Minki Hong (⚠️ Contact Me: jackyh1@dgu.ac.kr)
    Jangho Choi (⚠️ Contact Me: 2025120382@dgu.ac.kr)
'''

# import libraries
import os
import pandas as pd
import time
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
import json
from tqdm import tqdm

# Setting API
client = OpenAI(api_key=os.getenv("YOUR_OPEN_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"
temperature=0

# Build message
def build_message(prompt_text: str):
    return [
        {"role": "system", "content": "Respond ONLY with valid JSON. Do NOT add commentary."},
        {"role": "user", "content": prompt_text.strip()}
    ]

# Consistency template
CONSISTENCY_PROMPT = """
You are a professional dataset auditor for social-norm dialogues.
You given culture category.

Your task is to evaluate only the *Consistency* of the dialogue.  
Ignore grammar, fluency, or style. Focus only on whether the dialogue is logically and contextually consistent throughout.

[Culture]
{culture}

[Norm]
{norm}

[Dialogue]
{dialogue}

◼︎ Evaluation Question:
Assuming the dialogue adheres to the given social norm,  
are all utterances logically and emotionally coherent with one another?

- Do characters maintain a consistent attitude, tone, and perspective throughout?
- Are there any contradictions or abrupt shifts in reasoning, emotion, or information?
- Does the dialogue flow smoothly without unexpected or unjustified changes?

◼︎ Scoring Criteria (1 to 5 integer):
1 = Major inconsistencies or contradictions  
3 = Somewhat inconsistent or awkward transitions  
5 = Fully consistent and coherent throughout

◼︎ Output Format (JSON ONLY)
Respond ONLY in the following JSON format:
{{
    "criterion": "Consistency",
    "score": <integer between 1 and 5>,
    "explanation": "<1–2 sentence explanation in Korean>"
}}
"""

# Naturalness prompt
NATURALNESS_PROMPT = """
You are a professional dataset auditor for social-norm dialogues.

Your task is to evaluate only the *Naturalness* of the dialogue.  
Ignore whether the response is factually correct or norm-appropriate. Focus on how naturally the dialogue would sound to a native Korean speaker.

[Dialogue]
{dialogue}

◼︎ Evaluation Question:
Does the dialogue sound natural and fluent as if spoken by native Korean speakers in a real-world situation?

- Are the expressions, tone, and word choices contextually appropriate and idiomatic?
- Do the conversational turns flow smoothly without sounding robotic or overly scripted?
- Are there any awkward phrases or unnatural sentence structures?

◼︎ Scoring Criteria (1 to 5 integer):
1 = Extremely unnatural or robotic  
3 = Somewhat awkward or artificial  
5 = Very natural, fluent, and human-like

◼︎ Output Format (JSON ONLY)
Respond ONLY in the following JSON format:
{{
    "criterion": "Naturalness",
    "score": <integer between 1 and 5>,
    "explanation": "<1–2 sentence explanation in Korean>"
}}
"""

# Relevance template
RELEVANCE_PROMPT = """
You are a professional dataset auditor for social-norm dialogues.
You given culture category.

Your task is to evaluate only the *Relevance* of the dialogue to the provided Scenario and Situation.  
Ignore grammar, fluency, or logical consistency. Focus on whether the dialogue reflects the key intentions, emotions, and context described in the Scenario and Situation.

[Culture]
{culture}

[Scenario]
{scenario}

[Situation]
{situation}

[Dialogue]
{dialogue}

◼︎ Evaluation Question:
Does the dialogue appropriately address and reflect the actions, intentions, and emotional context presented in the scenario and situation?

- Are the key elements of the situation represented in the conversation (e.g., apology, embarrassment, disagreement)?
- Do the characters react in a way that makes sense for the described context?
- Are any critical actions or emotional responses missing from the dialogue?

◼︎ Scoring Criteria (1 to 5 integer):
1 = Dialogue is mostly irrelevant to the situation  
3 = Partially relevant, with some elements missing or misaligned  
5 = Dialogue is highly relevant and faithfully represents the described situation

◼︎ Output Format (JSON ONLY)
Respond ONLY in the following JSON format:
{{
    "criterion": "Relevance",
    "score": <integer between 1 and 5>,
    "explanation": "<1–2 sentence explanation in Korean>"
}}
"""

# Scenario-dialogue coherence template
SCE_SITU_DIAL_PROMPT = """
You are a professional dataset auditor for social-norm dialogues.

Your task is to evaluate only the *Scenario–Situation-Dialogue Coherence* of the dialogue.  
Ignore grammar or emotional tone. Focus on whether the dialogue logically and smoothly follows the sequence of events described in the scenario.

[Culture]
{culture}

[Scenario]
{scenario}

[Situation]
{situation}

[Dialogue]
{dialogue}

◼︎ Evaluation Question:
Does the dialogue unfold in a way that aligns with the narrative structure and event flow of the scenario (or situation)?

- Is there a smooth and coherent transition from the described situation into the dialogue?
- Are there any gaps, jumps, or inconsistencies between what the scenario sets up and what happens in the conversation?
- Does the dialogue logically follow the order of events and emotional pacing described in the scenario (or situation?

◼︎ Scoring Criteria (1 to 5 integer):
1 = Dialogue and scenario (or situation) are disconnected or contradictory  
3 = Some transitions or event links are missing or unclear  
5 = Dialogue flows logically and coherently from the scenario (or situation)

◼︎ Output Format (JSON ONLY)
Respond ONLY in the following JSON format:
{{
    "criterion": "Scenario-Situation-Dialogue Coherence",
    "score": <integer between 1 and 5>,
    "explanation": "<1–2 sentence explanation in Korean>"
}}
"""

# Emotion appropriateness template
EMOTION_APP_TEMPLATE = """
You are a professional dataset auditor for social-norm dialogues.
You given culture category.

Your task is to evaluate only the *Emotional Appropriateness* of the dialogue.  
Ignore grammar, norm correctness, or logical structure. Focus on whether the tone, expressions, and emotional language used in the dialogue match the emotional context of the situation.

[Culture]
{culture}

[Scenario]
{scenario}

[Situation]
{situation}

[Dialogue]
{dialogue}

◼︎ Evaluation Question:
Does the emotional tone, choice of words, and manner of speaking in the dialogue align appropriately with the emotional context of the situation?

- Does the dialogue reflect the expected emotional state (e.g., tension, regret, embarrassment, relief) implied in the situation?
- Are the expressions and tone suitable for the described emotional stakes?
- Is there any emotional mismatch that makes the dialogue feel unnatural or inappropriate?

◼︎ Scoring Criteria (1 to 5 integer):
1 = Emotionally disconnected or inappropriate  
3 = Emotion is somewhat present but weak or inconsistent  
5 = Emotional tone is highly appropriate and enhances the realism

◼︎ Output Format (JSON ONLY)
Respond ONLY in the following JSON format:
{{
    "criterion": "Emotion Appropriateness",
    "score": <integer between 1 and 5>,
    "explanation": "<1–2 sentence explanation in Korean>"
}}
"""

# Social norm appropriateness template
SOCIAL_NORM_TEMPLATE = """
You are a professional dataset auditor for social-norm dialogues.
You given culture category.

Your task is to evaluate only the *Social Norm Appropriateness* of the dialogue.  
Assess how well the conversation reflects the given social norm, and categorize the degree of adherence.

[Culture]
{culture}

[Norm]
{norm}

[Dialogue]
{dialogue}

◼︎ Evaluation Question:
Based on the given social norm, how well does the dialogue align with it?

- Does the dialogue completely follow the norm?  
- Does it violate the norm?  
- Does it violate the norm but later attempt to resolve it?  
- Is the behavior partially aligned with the norm?

Please choose one of the following classifications:
1 = Fully Violated  
2 = Partially Violated  
3 = Violation then Resolved  
4 = Partially Adhered  
5 = Fully Adhered

◼︎ Output Format (JSON ONLY)
Respond ONLY in the following JSON format:
{{
    "criterion": "Social Norm Appropriateness",
    "score": <integer from 1 to 5>,
    "explanation": "<1–2 sentence explanation in Korean>"
}}
"""

# Evaluate each criteria
def evaluate(culture: str, scenario: str, situation: str, dialogue: str):
    
    # Concatenate above evaluation template and build messages.
    '''
    Example:
    prompt = EMOTION_APP_TEMPLATE.format(
        culture=culture,
        scenario=scenario,
        situation=situation,
        dialogue=dialogue
    )
    messages = build_message(prompt)
    '''
    messages = ""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        return {"error": f"Failed to evaluate: {str(e)}"}

# ‼️ SAVE YOUR EVALUATION RESULTS USING YOUR OWN CODE:
# YOUR CODE:
