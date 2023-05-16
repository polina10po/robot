from flask import Flask, render_template, redirect, abort, request, url_for
import psycopg2
# import RPi.GPIO as GPIO

# m11=18
# m12=23
# m21=24
# m22=25
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(m11, GPIO.OUT)
# GPIO.setup(m12, GPIO.OUT)
# GPIO.setup(m21, GPIO.OUT)
# GPIO.setup(m22, GPIO.OUT)
# GPIO.output(m11 , 0)
# GPIO.output(m12 , 0)
# GPIO.output(m21, 0)
# GPIO.output(m22, 0)

conn = psycopg2.connect(
    host="127.0.0.1",
    database="Robot",
    user="postgres",
    password="1234"
)

cur = conn.cursor()
#батарея
cur.execute("""SELECT "ID","Battery" FROM "Parameters" """)
rows = cur.fetchall()
data = [{"date": row[0], "result": row[1]} for row in rows]
#мощность
cur.execute("""SELECT "ID","Power" FROM "Parameters" """)
rows = cur.fetchall()
data_power = [{"id": row[0], "result": row[1]} for row in rows]



app=Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/control')
def control():    
    return render_template("control.html")
@app.route('/left_side')
def left_side():
    data1="LEFT"
    GPIO.output(m11 , 0)
    GPIO.output(m12 , 0)
    GPIO.output(m21 , 1)
    GPIO.output(m22 , 0)
    return 'true'
@app.route('/right_side')
def right_side():
   data1="RIGHT"
   GPIO.output(m11 , 1)
   GPIO.output(m12 , 0)
   GPIO.output(m21 , 0)
   GPIO.output(m22 , 0)
   return 'true'
@app.route('/up_side')
def up_side():
   data1="FORWARD"
   GPIO.output(m11 , 1)
   GPIO.output(m12 , 0)
   GPIO.output(m21 , 1)
   GPIO.output(m22 , 0)
   return 'true'
@app.route('/down_side')
def down_side():
   data1="BACK"
   GPIO.output(m11 , 0)
   GPIO.output(m12 , 1)
   GPIO.output(m21 , 0)
   GPIO.output(m22 , 1)
   return 'true'
@app.route('/stop')
def stop():
   data1="STOP"
   GPIO.output(m11 , 0)
   GPIO.output(m12 , 0)
   GPIO.output(m21 , 0)
   GPIO.output(m22 , 0)
   return  'true'
@app.route('/save-photo', methods=['POST'])
def save_photo():
    imgBase64 = request.form['photo_data']
    imgBytes = base64.b64decode(imgBase64.split(',')[1])
    with open('photo.jpg', 'wb') as f:
        f.write(imgBytes)
    return 'Снимок сохранен'

@app.route('/washing')
def washing():
    return render_template("washing.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/parameters')
def parameters():
    return render_template("parameters.html",  data=data, data_power=data_power)


@app.route('/controller')
def showController():
    return render_template('controller.html')


cur.close()
conn.close()


if __name__=="__main__":
    app.run(debug=True)