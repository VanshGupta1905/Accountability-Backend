from flask import Blueprint, request, render_template, current_app,url_for,redirect,jsonify
from collections import deque
import time
from routes.planner import gemini
from routes.planner import variables

import json
quiz=Blueprint('quiz',__name__)
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


@quiz.route('/generate_quiz')
def generating_quiz():
    
    prompt = """
     "Given the following text, generate a set of multiple-choice questions with four options each.
      Each question should have a clear topic from the topic list, and the correct answer should be indicated. Provide a concise explanation for each correct answer. 
     The questions should be designed to test understanding of the key concepts and information presented in the text. the output must have atleast 3 question from each topic.
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
        break  # Remove this
    rem = []
    # while topics_left: rem.append(topics_left.popleft())

    quiz.extend(quiz_for_topic(rem, prompt))

    return render_template('Quiz.html', data=quiz)