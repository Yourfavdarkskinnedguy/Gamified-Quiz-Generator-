from flask import Flask, render_template, request, redirect, url_for, session
from backend import generate_prompt
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import time
import functools

import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame



load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


app= Flask(__name__)
app.secret_key= os.getenv('app_secret_key')







@app.route('/')
def home():
    return redirect(url_for('login'))



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =="GET":
        return render_template('login.html')
    elif request.method =="POST":
        email= request.form.get('email')
        password= request.form.get('password')

        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['access_token'] = user.session.access_token
            session['userID']= user.user.id

            return redirect(url_for('index'))
        
        except Exception as e:
            print(f'error during login is {e}')
            return 'error'




@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method =="GET":
        return render_template('signup.html')
    elif request.method =="POST":
        signup_email= request.form.get('signup-email')
        signup_password= request.form.get('signup-password')
        try:
            user= supabase.auth.sign_up({'email': signup_email, 'password': signup_password})
            session['userID']= user.user.id
            #once a user signups up, create a table for the user
            return redirect(url_for('index'))
        except Exception as e: 
            print(f'error during signup is {e}')
            return render_template('signup.html')



def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "userID" not in session:
            return render_template('unauthorized.html')
        return func(*args, **kwargs)

    return secure_function
    

def topic_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if 'topic' not in session:
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return secure_function



@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == "GET":
        return render_template('/index.html')
    
    elif request.method == "POST":
        # we re using this to check to check amount of time taken for logging
        start = time.time()


        topic= request.form.get('topic')
        current_level = 0
        gemini_time_time= time.time()
        level, question, option, correctAnswer= generate_prompt(topic, current_level)
        print("gemini took", time.time() - gemini_time_time, "seconds")
        
        session['level']= level
        session['question']= question
        session['option']= option
        session['correctAnswer']= correctAnswer
        session['topic']= topic

        #####3#here!!!!

        userID= session.get('userID')
        score=0
        session['score']= score


        index_supabase_time= time.time()
        response = supabase.table("user_progress").upsert({
        "id": userID,
        "level": level,
        "topic": topic,
        "question": question,
        "scores": score
    }).execute() 
        print("index supabase took", time.time() - index_supabase_time, "seconds")
        print(f'response in index is {response}')



        print("index route took", time.time() - start, "seconds")
        return redirect(url_for(
    "quiz"
))







@app.route('/api/quiz', methods=['POST', 'GET'])
@topic_required
def quiz():
    
 
    if request.method =="GET":

        userID= session.get('userID')
        response = supabase.table("user_progress").select("*").eq("id",userID).execute()
        option= session.get('option')
        print(f'new options logged is {option}')
        if response.data: 
            row = response.data[0]  # Get the first (and usually only) row
            level = row.get("level")
            topic = row.get("topic")
            question = row.get("question")
            score = row.get("scores")
        else:
            print('No user found!')


        return render_template('quiz.html',
        score=score,
        level=level,
        question=question,
        options=option,  # You can parse this later
        )
    
    elif request.method== 'POST':
        pygame.mixer.init()  # Initialize the mixer module.
        win_sound_filepath= os.path.join(os.getcwd(),'buzzer-4-183895.mp3')
        lost_sound_filepath= os.path.join(os.getcwd(),'chime-sound-7143.mp3')
        win_sound = pygame.mixer.Sound(win_sound_filepath)
        lost_sound= pygame.mixer.Sound(lost_sound_filepath)

        start= time.time()
        answer= request.form.get('answer')
        userID= session.get('userID')

        response = supabase.table("user_progress").select("scores").eq("id",userID).single().execute()
        score = response.data['scores']
        print(f'check this score: {score}')

        level= session.get('level')


    

        correct_answer= session.get('correctAnswer')
        print(f'correct answer is {correct_answer}')
         

        if answer== correct_answer:
            win_sound.play()
            score+=10
            print(f'new updated score is {score}')
            level+=1
            print(f'new updated level is {level}')
            session['level']= level
            
     
            
        else:
            lost_sound.play()
            print('Incorrect answer')

        
       
        
        #get content from table here!
        response = supabase.table("user_progress").select("*").eq("id",userID).execute()
        topic= session.get('topic')
        n, question, option, correctAnswer= generate_prompt(topic, level)
        
        session['question']= question
        session['option']= option
        session['correctAnswer']= correctAnswer
        
        

        start_for_supabase= time.time()
        supabase.table("user_progress").upsert({
        "id": userID,
        "level": level,
        "topic": topic,
        "question": question,
        "scores": score
    }).execute()
        print("supabse took", time.time() - start_for_supabase, "seconds")


        print("quiz route took", time.time() - start, "seconds")
        
        return render_template(
        "quiz.html",
        score= score,
        level=level,
        question=question,
        options=option,
        display_text="HOLD ON...",
        correctAnswer=correctAnswer


    )










if __name__ == "__main__":
    app.run(debug=True)


