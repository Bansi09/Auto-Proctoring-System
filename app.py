from flask import Flask, render_template, Response, request, redirect,url_for,flash,make_response
import cv2
import os
import numpy as np
from threading import Thread
import Capture_Image
import csv
import Train_Image
import Recognize
import pandas as pd
import detect_open_mouth
from time import time




def train_image():
    Train_Image.TrainImages()
    

# instatiate flask app
app = Flask(__name__, template_folder='./templates')


cam = cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from cam
    global out, capture, rec_frame
    file = pd.read_csv('./StudentDetails/StudentDetails.csv')

    df=pd.DataFrame(file.iloc[:,:].values)

    df=pd.DataFrame(file.iloc[-1:,:].values)
    det = df.values.tolist()
    Id = str(det[0][4])
    name = str(det[0][0])
    success, frame = cam.read()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    sampleNum = 0
    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(
            gray, 1.3, 5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        for(x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (10, 159, 255), 2)
            # incrementing sample number
            sampleNum = sampleNum+1
            # saving the captured face in the dataset folder TrainingImage
            cv2.imwrite("TrainingImage" + os.sep + name + "."+Id + '.'+str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])
            # display the frame
            cv2.imshow('frame', frame)
        try:
            ret, buffer = cv2.imencode('.jpeg', cv2.flip(frame, 1))
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            pass
        if cv2.waitKey(100) & 0xFF == ord('q'):
                break

        elif sampleNum > 151:
            cam.release()
            # cv2.destroyAllWindows()
            break        
    train_image()
    return "True"
    
# MOUTH OPENING
# def mouth_open():
#     b=str(detect_open_mouth.Talking())
#     return b

def mouth_open():
    # b=str(detect_open_mouth.Talking())
    # return b
    return detect_open_mouth.Talking()


def capture_image():
    Capture_Image.takeImages()

def recognize_feed():
    a=str(Recognize.recognize_attendence())
    return a

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/exam_feed')
def exam_feed():
    # return render_template('index.html',reg=gen_frames(),mimetype='multipart/x-mixed-replace; 
    # boundary=frame')
    # return render_template("pythonexam.html", b = mouth_open())
    return Response(mouth_open(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    # return render_template('index.html',reg=gen_frames(),mimetype='multipart/x-mixed-replace; 
    # boundary=frame')
    
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/register')
def register():
    
    return render_template('register.html')



@app.route('/gfg',methods = ['GET','POST'])
def gfg():
    if(request.method == 'POST'):
        fname = str(request.form.get('fname'))
        email = request.form.get('email')
        className = request.form.get('className')
        rollno = request.form.get('rollno')
        regno = str(request.form.get('regno'))
        password = request.form.get('password')
        row = [fname, email, className, rollno, regno, password]
        with open("StudentDetails"+os.sep+"StudentDetails.csv", 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        print(time())
        video_feed()
    return render_template('camera.html',t=True)


@app.route('/login', methods=['POST'])

def login():

    register = int(request.form.get('register'))

    password = request.form.get('password')

    df = pd.read_csv('./StudentDetails/StudentDetails.csv',usecols=["Id", "Password"])



    if(df[df.Id == register].empty ):

        return render_template('index.html', e = "Login Failed")

    elif(df[df.Password == password].empty):

        return render_template('index.html', e = "Login Failed")

    elif(df[df.Id == register].empty and df[df.Password == password].empty):

        return render_template('index.html', e = "Login Failed")

    else:

        return render_template('startExam.html', e = "Login Success")

@app.route('/camera', methods=['GET', 'POST'])
def camera():
    return render_template('camera.html',text="Hello Sid")

@app.route('/recognize')
def recognize():
    return render_template('recognize.html', a=recognize_feed())
    # recognize_feed()
    # return render_template('recognize.html')




def nai():
    return detect_open_mouth.Talking()

@app.route('/exam')
def exam():
    # b=""
    # executor.submit(b=mouth_open())
    # return render_template('pythonexam.html', b=mouth_open())
    
    # a=exam_feed()
    # exam_feed()
    # nai()
    # b=mouth_open()
    return render_template('pythonexam.html')
    

def new_frames():  # generate frame by frame from camera
    while True:
        success, frame = cam.read() 
        if success:                
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass
            
@app.route('/new_feed')
def new_feed():
    return Response(new_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/python')
# def python():
#     return render_template('pythonexam.html')
if __name__ == "__main__":
    app.run(port='3000', debug=True)