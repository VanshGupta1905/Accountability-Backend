import google.generativeai as genai
import os

class model:
    def __init__(self):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.session=self.model.start_chat(history=[])
        
        