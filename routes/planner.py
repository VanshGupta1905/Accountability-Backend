import json
import time
from collections import deque
from flask import Blueprint, request, render_template, current_app,url_for,redirect,jsonify
import os
from routes.gemini import model
gemini=model()
planner = Blueprint('planner', __name__)
from PyPDF2 import PdfReader
ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'pptx'}
variables={}
text=None
data=None
topics=None



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_subtopic(text):
    global topics
    prompt="""
    The topics should only be technical for Engineering Students
    given text return the list of topics 
    And how long it will take to complete it give three estimates
    for each topic short, avg and long meaning how much time it will take for a user to learn that topic 
    based on learning intensity return in JSON . The Output should be in this schema .
    Try not give exact text provided in the resource modify a little
    
    
    {"subtopics": ["string"],
     "time_estimates": {
     "string": {
      "avg": "string",
      "long": "string",
      "short": "string"
        }
      }
    }
    """
    response=gemini.session.send_message(prompt+text)
    ans= str(response.text)
    start_idx=ans.find('{')
    end_idx=ans.rfind('}')
    topics= json.loads(ans[start_idx:end_idx+1])
    print(topics)
    return topics

def Extract_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file) 

        num_pages = len(reader.pages)

        text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

@planner.route('/planner')
def upload_form():
    current_app.config['uploads'] = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(current_app.config['uploads']):
        os.makedirs(current_app.config['uploads'])

    return render_template('uploadFiles.html')


@planner.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):

        global text
        filename = file.filename
        file.save(os.path.join(current_app.config['uploads'], filename))
        
        path = os.path.join(current_app.config['uploads'], filename)

        text=Extract_text(path)

        os.remove(path)
        Current_data=generate_subtopic(text)
        variables['Current_data']=Current_data
        return render_template('Planning.html',data=Current_data)


    return 'File type not allowed'



@planner.route('/upload_resume',methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        global text
        filename = file.filename
        file.save(os.path.join(current_app.config['uploads'], filename))
        path = os.path.join(current_app.config['uploads'], filename)
        text = Extract_text(path)
        os.remove(path)
        Current_data = generate_subtopic(text)
        variables['Current_data'] = Current_data
        return render_template('Planning.html', data=Current_data,content='resume')

    return 'File type not allowed'


