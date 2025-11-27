'''
Module 4: Dialogue Generator - Korean/V2R

Model Configuration: gpt-4.1
Author: 
    Minki Hong (⚠️ Contact Me: jackyh1@dgu.ac.kr)
    Jangho Choi (⚠️ Contact Me: 2025120382@dgu.ac.kr)
'''

# Import libraries
import os
import time
import pandas as pd
import pickle
import json
import re
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Setting API
client = OpenAI(api_key=os.getenv("YOUR_OPEN_API_KEY"))

MODEL = 'gpt-4.1'
TEMPERATURE = 0.9
MAX_TOKENS=1024
OUTPUT_DIR = 'YOUR DIRECTORY'
CSV_PATH = "YOUR_PATH/situation_korean_v2r.csv"
OUTPUT_PATH = "YOUR_PATH/dialogue_korean_v2r.csv"

# Call GPT API
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gpt_api(messages, temp=TEMPERATURE, max_tokens=MAX_TOKENS):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temp,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❗ Fail to call: {e}")
        raise

# Generate Dialogue
def generate_dialogue(category, norm, scenario, situation):
    prompt = f"""
다음은 한국의 사회적 규범에 대한 설명과 규범을 위반하였으나 해결한 예시입니다.

[사회적 규범 카테고리]
{category}

[사회적 규범 설명]
{norm}

[규범을 위반하였으나 해결한 Scenario]
{scenario}

[규범을 위반하였으나 해결한 Situation]
{situation}

해당 내용을 바탕으로 Situation에 대한 Dialogue를 생성해 주세요. 
Dialogue는 두 사람 간의 대화 형식으로 작성해 주세요. 
대화의 주제는 규범을 위반한 뒤, 이를 원만하게 해결하는 상황에 대한 것입니다.
사회적 규범을 위반한 문제를 만드세요. 그런 뒤, 문제를 인식하고 규범을 준수하도록 문제를 해결하세요.
규범이 위반한 상황이 존재하며, 대화가 진행되며 규범 위반에 대해 상황이 해결됩니다.
대화의 내용은 자연스럽고 일상적인 대화로 구성되어야 하며, 
각 인물의 이름과 대사로 구분되어야 합니다. 
대화는 다음과 같은 형식으로 작성해 주세요.

Dialogue:
정 부장: 민수 씨, 이 보고서 여기 수치 잘못됐어요. 지난 분기 자료가 그대로 들어갔잖아요.
민수: (모니터에서 눈도 떼지 않고) 아, 네. 그럴 수도 있죠.
정 부장: …그럴 수도 있다뇨? 발표 자료인데 이런 실수가 반복되면 곤란하잖아요.
민수: (작게 한숨 쉬며) 아니 뭐, 요즘 너무 일 많아서 그렇죠. 제가 이것만 하는 것도 아니고요.
정 부장: (표정 굳으며) 지금 제 말이 귀찮다는 겁니까?

(잠시 정적. 민수는 부장님의 말투가 단호해진 걸 느끼고, 그제야 모니터에서 눈을 떼고 정 부장을 바라본다)

민수: (고개를 살짝 숙이며) 아… 부장님, 죄송합니다. 제가 방금은 너무 무성의하게 말씀드렸네요.
(목소리를 낮추며) 사실 요즘 일정에 쫓기다 보니 제가 예민했던 것 같아요. 그래도 그런 식으로 반응한 건 제 잘못입니다.

(정 부장은 잠시 민수를 바라보다가 말없이 고개를 끄덕인다)

민수: 보고서 내용도 다시 확인해서, 오늘 안으로 수정본 제출드리겠습니다. 혹시 발표 전에 더 확인하실 부분 있으시면 말씀 주세요.
정 부장: (조금 누그러진 목소리로) 음, 알겠어요. 힘든 거 이해합니다. 그래도 발표 자료는 팀 전체의 얼굴이에요. 다음부턴 조금 더 꼼꼼하게 챙겨줘요.
민수: 네, 그렇게 하겠습니다. 다시 한 번 죄송합니다.

(정 부장은 다시 자료를 넘겨보며 다음 안건으로 넘어가고, 민수는 살짝 깊은 숨을 내쉬며 회의에 집중한다. 싸늘했던 분위기는 서서히 정리된다.)
[끝]

→ 당신의 대화:"""
    messages = [{"role": "user", "content": prompt}]
    return gpt_api(messages)

# Run module
def run_dialogue_generation():
    df = pd.read_csv(CSV_PATH).reset_index(drop=True)

    dialogues = []
    for idx, row in df.iterrows():
        category = row.get("Category", "")
        norm = row.get("Norm", "")
        scenario = row.get("Violation_Scenario", "")
        situation = row.get("Violation_Situation", "")

        if pd.isna(norm) or pd.isna(situation):
            dialogues.append("")
            continue

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
        
    df["Dialogue"] = dialogues
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    
