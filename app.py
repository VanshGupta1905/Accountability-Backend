from flask import Flask, redirect, request, session, url_for, render_template
import os
import requests
from dotenv import load_dotenv
from routes.quiz import quiz
from routes.planner import planner
from routes.interview import interview


load_dotenv()
app = Flask(__name__)
app.register_blueprint(quiz)
app.register_blueprint(planner)
app.register_blueprint(interview)
UPLOAD_FOLDER = 'uploads'
app.config['uploads'] = UPLOAD_FOLDER



app.secret_key = os.getenv('SECRET_KEY')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = "http://127.0.0.1:5000/authorize"





@app.route('/')
def home():
    if 'user' in session:
        user = session['user']
        return render_template('home.html', user=user)
    return redirect('/login')



@app.route('/login')
def login():
    auth_url = (
        f"{GOOGLE_AUTH_URL}?response_type=code&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile"
        f"&access_type=offline&prompt=consent"
    )
    return redirect(auth_url)



@app.route('/authorize')
def authorize():
    if 'error' in request.args:
        return f"Error: {request.args['error']}"


    code = request.args.get("code")
    
 
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
    token_response_data = token_response.json()
    
    if "error" in token_response_data:
        return f"Error fetching token: {token_response_data['error_description']}"
    
  
    access_token = token_response_data.get("access_token")
    id_token = token_response_data.get("id_token")
    

    user_info_response = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_response.json()

    session['user'] = {
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "id_token": id_token
    }
    print(session['user'])
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
