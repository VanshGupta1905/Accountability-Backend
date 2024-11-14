from flask import Blueprint, request, render_template, current_app,url_for,redirect,jsonify
import time
from routes.planner import gemini
from routes.planner import variables
from collections import deque
import json
interview=Blueprint('interview',__name__)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "response_schema": {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["id", "topic", "questions"],
            "properties": {
                "id": {"type": "integer"},
                "topic": {"type": "string"},
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["question", "options"],
                        "properties": {
                            "question": {"type": "string"},
                            "options": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["text", "correct"],
                                    "properties": {
                                        "text": {"type": "string"},
                                        "correct": {"type": "boolean"},
                                        "reasoning": {"type": "string"},
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "response_mime_type": "application/json",
}
def quiz_for_topic(topics,prompt):
    prompt2 = f"topic={topics}"
    output = gemini.session.send_message(prompt + prompt2, generation_config=generation_config)
    ans = output.text
    print(ans)
    start_idx = ans.find('[')
    end_idx = ans.rfind(']')
    data =  json.loads(ans[start_idx:end_idx + 1])
    return data


@interview.route('/generate_interview_questions')
def generating_quiz():
    prompt = """
     "Given the following text, generate a set of multiple-choice questions with four options each.
     For the inteview of candidate the questions must be from the prespective of interviewer in similar tone 
     The question should have     
      Provide a concise explanation for each correct answer. 
      If there is a technology mentioned ask very specific question that only a person with deep knowledge of that technology is able to know
      "Example if mentioned react.js then What is virtual dom ? and then multiple options"
      "Like the question found on GFG,Interview-Bit,Leetcode blogs etc for Product based companies"
     The questions should be designed to test understanding of candidate knowledge about the key concepts and information presented in the text. the output must have atleast 3 question from each topic
     the questions must be able to detect whether candidate really have indepth knowledge or he/she is bluffing.
      output must be in JSON fromat in {

  [  
  {
  "id": <integer>, // Unique identifier for the question set
  "topic": <string>, // Topic of the questions
  "questions": [
    {
      "question": <string>, // The question text
      "options": [
        {
          "text": <string>, // Option text
          "correct": <boolean>, // Whether the option is correct
          "reasoning": <string> // Explanation for the correctness or incorrectness of the option
        }
      ]
    }
  ]
  },.... ]

    way. make sure all topics are used please return nothing except JSON",
        """
    Current_data=variables['Current_data']
    topics_left = deque(Current_data['subtopics'])
    quiz = []
    for i in range(len(topics_left) // 4):
        li = [topics_left.popleft(), topics_left.popleft(), topics_left.popleft(), topics_left.popleft()]
        quiz.extend(quiz_for_topic(li, prompt))
    rem = []
    while topics_left: rem.append(topics_left.popleft())

    quiz.extend(quiz_for_topic(rem, prompt))

    return render_template('Quiz.html', data=quiz)