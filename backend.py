import base64
import os
from google.generativeai import types
from google.generativeai import GenerativeModel
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel
import json

load_dotenv()


class suggestion(BaseModel):

    #response: str
    questions: str
    level: int

api_key= os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)


generation_config={
    'temperature':0.85,
    'response_mime_type': "text/plain",
    'response_mime_type': "application/json",
    'response_schema': suggestion,
}

model= genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-05-20",
    generation_config=generation_config
    )






def generate_prompt(topic, current_level):
    prompt =f"""
You are a quiz generator. Given a topic and the current level a user has reached, return only valid JSON containing a harder question for the next level (i.e., level = current_level + 1).

Format:
{{
  "level": <next_level>,
  "questions": [
    {{
      "question": "string",
      "options": ["option1", "option2", "option3", "option4"],
      "correctAnswer": "correct option from above"
    }}
  ]
}}
Topic: {topic}  
Current Level: {current_level}

Instructions:
- Generate one question only.
- Make sure the question reflects a slightly increased difficulty based on the level.
- Only return valid JSON. Do not include any explanations or extra text.


"""


    
    try:
        input= model.generate_content([

            f'query: {prompt}',
            'output: ',
        ]   
        )
        input= json.loads(input.text) 

        level= input['level']
        
        que= input['questions']
        parsed_que = json.loads(que)

        quiz= parsed_que[0]

        question= quiz.get('question')
        option= quiz.get('options')
        correctAnswer= quiz.get('correctAnswer')



        return level, question, option, correctAnswer


    except Exception as e:
        print(f'error is : {e}')

    
    
 



if __name__ == "__main__":
    while True:
        prompt= input('YOU: ')
        if prompt.lower() in ['bye','exit', 'close', 'quit']:
            print('Goodbye')
            break
        level, question, option, correctAnswer= generate_prompt(prompt)

        print(f'level is {level}')
        print(f'question is {question}')
        print(f'option is {option}')
        print(f'correctAnswer is {correctAnswer}')
