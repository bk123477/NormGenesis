'''
Module 4: Labeling Dialogue

Model Configuration: gpt-4.1
Author: 
    Jangho Choi (⚠️ Contact Me: 2025120382@dgu.ac.kr)
    Minki Hong (⚠️ Contact Me: jackyh1@dgu.ac.kr)
'''

# Import libraries
import os
import pandas as pd
import time
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Setting API
client = OpenAI(api_key=os.getenv("YOUR_OPEN_API_KEY"))
MODEL = "gpt-4o-mini-2024-07-18"
TEMPERATURE = 0.7
MAX_TOKENS = 1024

CSV_PATH = "YOUR_PATH/DIALOGUE_PATH.csv"
OUTPUT_PATH = "YOUR_PATH/LABELED_DIALOGUE.xlsx"

# Call GPT API
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gpt_api(messages, temp=TEMPERATURE, max_tokens=MAX_TOKENS):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temp,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# Labeling dialogue
def label_dialogue(category, norm, Scenario, Situation, Dialogue):
    prompt = f"""The following is a conversation based on [EACH NATIONS] social norms.
Please determine whether each utterance follows the given norm and assign an appropriate label.

[Social Norm Category]
{category}

[Social Norm Description]
{norm}

[Scenario Demonstrating Compliance with the Norm]
{Scenario}

[Situation Demonstrating Compliance with the Norm]
{Situation}

[Dialogue Demonstrating Compliance with the Norm]
{Dialogue}



Please review the Dialogue based on the provided norm and assign the most appropriate label to each utterance.
    [Label List]
	1. Acknowledgment [ACK]  
    - Description: A response that explicitly acknowledges or recognizes the speaker's statement.  
    - Examples: "I understand.", "Got it."

    2. Agreement [AGR]  
    - Description: A response showing agreement or alignment with the speaker’s opinion.  
    - Examples: "I agree with you.", "That's right."

    3. Disagreement [DIS]  
    - Description: A response expressing disagreement or rejection of the speaker’s opinion or suggestion.  
    - Examples: "I don't think so.", "I can't agree with that."

    4. Apology [APO]  
    - Description: A response expressing regret for one's mistakes or causing inconvenience.  
    - Examples: "I'm sorry.", "It was my fault."

    5. Gratitude [THX]  
    - Description: A response expressing appreciation for help, consideration, or compliments.  
    - Examples: "Thank you so much.", "I really appreciate your help."

    6. Empathy / Support [EMP]  
    - Description: A response that emotionally resonates with or supports the speaker’s feelings or situation.  
    - Examples: "That must have been tough.", "I understand how you feel."

    7. Excuse / Justification [JUS]  
    - Description: A response offering reasons or explanations for one’s actions or mistakes.  
    - Examples: "Actually, it was because of ~", "I didn’t have enough time…"

    8. Suggestion / Advice [SUG]  
    - Description: A response proposing a solution or advice for a problem.  
    - Examples: "How about trying this?", "I think it would be better to ~."

    9. Question / Information Request [QUE]  
    - Description: A response asking for additional explanations or information.  
    - Examples: "Why do you think that?", "Could you explain more?"

    10. Criticism [CRT]  
        - Description: A response criticizing or negatively evaluating the speaker’s words or actions.  
        - Examples: "That's a serious problem.", "This part is incorrect."


If an utterance is not relevant to the given norm, label it as 'Not Relevant'.

When labeling, please format as follows: Role | Label | Explanation  
(using "|" to separate Role, Label, and Explanation)

Example:

```
Mrs. Davis: Hello, John. Is everything okay?  
(Not Relevant | Mrs. Davis initiates the conversation.)

John: Actually... my mother passed away two days ago.  
(Not Relevant | John shares personal information.)

Mrs. Davis: Oh, John... I'm so sorry. My deepest condolences to you and your family during this difficult time.  
(EMP | Mrs. Davis expresses sympathy and offers condolences.)

John: Thank you so much, Mrs. Davis. It's been really hard.  
(THX | John expresses appreciation for Mrs. Davis's sympathy.)

Mrs. Davis: Of course. Is there anything I can do for you? Should I contact someone or just be here to listen? Feel free to reach out anytime you need.  
(EMP | Mrs. Davis offers help and emotional support.)

John: Thank you, Mrs. Davis. I truly appreciate it. I'm just trying to come to terms with everything right now. But it means a lot that you're here.  
(THX | John expresses gratitude and explains his current emotional state.)

Mrs. Davis: Absolutely, John. I’ll keep you and your family in my prayers.  
(EMP | Mrs. Davis reiterates her sympathy and offers prayers.)

Please follow this format carefully and assign the best-fitting label to each utterance based on the dialogue and provided norm.

Labeling:"""


    messages = [{"role": "user", "content": prompt}]
    return gpt_api(messages)

# Run module
def run_full_labeling():
    df = pd.read_csv(CSV_PATH)
    processed_df = df.copy()
    labeled_results = []

    for idx, row in processed_df.iterrows():
        category = row.get("Category", "")
        norm = row.get("Norm", "")
        Scenario = row.get("Scenario", "")
        Situation = row.get("Situation", "")
        Dialogue = row.get("Dialogue", "")

        try:
            print(f"🔄 Processing index {idx}...")
            labeled = label_dialogue(category, norm, Scenario, Situation, Dialogue)
            labeled_results.append(labeled)
            time.sleep(1.5)
        except Exception as e:
            labeled_results.append(f"❌ Error: {e}")
    
    # Save dataframe
    processed_df["Labeled_Dialogue"] = labeled_results
    processed_df.to_excel(OUTPUT_PATH, index=False)