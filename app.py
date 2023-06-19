from flask import Flask, render_template, redirect, abort, request, url_for
import psycopg2
import datetime
import pyrobot

conn = psycopg2.connect(
    host="127.0.0.1",
    database="Robot",
    user="postgres",
    password="1234"
)

cur = conn.cursor()
#Скорость
cur.execute("""SELECT "Id","speed" FROM "Parameters" """)
rows = cur.fetchall()
data_speed = [{"id": row[0], "result": row[1]} for row in rows]
#Состояние_системы движения
cur.execute("""SELECT "Id","drive_state" FROM "Parameters" """)
rows = cur.fetchall()
data_state = [{"id": row[0], "result": row[1]} for row in rows]
#Пройденный путь
cur.execute("""SELECT "Id","passed" FROM "Parameters" """)
rows = cur.fetchall()
data_passed = [{"id": row[0], "result": row[1]} for row in rows]

cur.execute("""SELECT "Id","passed" FROM "Parameters" ORDER BY "Id" DESC LIMIT 1""")
row_passed = cur.fetchone()
#Угол по гироскопу
cur.execute("""SELECT "Id","angle_gyroscope" FROM "Parameters" """)
rows = cur.fetchall()
data_angle = [{"id": row[0], "result": row[1]}  for row in rows]
#Напряжение на батарее
cur.execute("""SELECT "Id","voltage_battery" FROM "Parameters" """)
rows = cur.fetchall()
data_voltage = [{"id": row[0], "result": row[1]} for row in rows]
#Ток на моторе
cur.execute("""SELECT "Id","current_lft_motor", "current_rgt_motor" FROM "Parameters" """)
rows = cur.fetchall()
data_current = [{"id": row[0], "lft": row[1], "rgt": row[2]}  for row in rows]
#ШИМ мотора
cur.execute("""SELECT "Id","lft_pwm", "rgt_pwm" FROM "Parameters" """)
rows = cur.fetchall()
data_pwn = [{"id": row[0], "lft": row[1], "rgt": row[2]}  for row in rows]
#координаты
cur.execute("""SELECT "Id","coords", "coords0" FROM "Parameters" """)
rows = cur.fetchall()
data_coords = [{"id": row[0], "coords": row[1], "coords0": row[2]}  for row in rows]
#расстояние по сонару
cur.execute("""SELECT "Id","frw_rgt_dst", "frw_lft_dst", "lft_frw_dst", "lft_bkw_dst", "rgt_frw_dst", "rgt_bkw_dst" FROM "Parameters" ORDER BY "Id" DESC LIMIT 1""")
rows = cur.fetchall()
data_dst = [{"frw_rgt_dst": row[1], "frw_lft_dst": row[2], "lft_frw_dst": row[3], "lft_bkw_dst": row[4], "rgt_frw_dst": row[5], "rgt_bkw_dst": row[6]}  for row in rows]
#расстояние по ИК датчику
cur.execute("""SELECT "Id","frw_rgt_ik", "frw_lft_ik", "lft_ik", "rgt_ik", "bkw_ik" FROM "Parameters" ORDER BY "Id" DESC LIMIT 1 """)
rows = cur.fetchall()
data_ik = [{"frw_rgt_ik": row[1], "frw_lft_ik": row[2], "lft_ik": row[3], "rgt_ik": row[4], "bkw_ik":row[5]}  for row in rows]
#расстояние по лидару
cur.execute("""SELECT "Id", "frw_lft_ld", "frw_mdl_ld", "frw_rgt_ld", "lft_frw_ld", "lft_mdl_ld", "lft_bck_ld", "bck_lft_ld", "bck_mdl_ld", "bck_rgt_ld", "rgt_frw_ld", "rgt_mdl_ld", "rgt_bck_ld" FROM "Parameters" ORDER BY "Id" DESC LIMIT 1 """)
rows = cur.fetchall()
data_ld = [{"frw_lft_ld": row[1], "frw_mdl_ld": row[2], "frw_rgt_ld": row[3], "lft_frw_ld": row[4], "lft_mdl_ld": row[5], "lft_bck_ld": row[6], "bck_lft_ld": row[7], "bck_mdl_ld": row[8], "bck_rgt_ld": row[9], "rgt_frw_ld": row[10], "rgt_mdl_ld": row[11], "rgt_bck_ld": row[12]}  for row in rows]
# выполняем запрос на подсчет количества записей в таблице
cur.execute(""" SELECT COUNT(*) FROM "Tasks" """)
count = cur.fetchone()[0]
#Последняя уборка
cur.execute("""SELECT "date","time","location","status" FROM "Tasks" ORDER BY "Id" DESC LIMIT 1""")
row_tasks = cur.fetchone()

app=Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html", row_passed=row_passed, count=count, row_tasks=row_tasks)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/control')
def control():    
    return render_template("control.html")
@app.route('/control_move', methods=['GET', 'POST'])
def control_robot():
    if request.method == 'POST':
        if 'move_forward' in request.form:
            return move_forward() # вызов функции для перемещения робота вперед
        elif 'move_backward' in request.form:
            return move_backward() # вызов функции для перемещения робота назад
        elif 'turn_left' in request.form:
            return turn_left() # вызов функции для поворота робота налево
        elif 'turn_right' in request.form:
            return turn_right() # вызов функции для поворота робота направо
    return render_template('control.html')

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

# Обработчик POST-запроса с данными для добавления в таблицу
@app.route('/add-data', methods=['POST'])
def add_data():
    conn = psycopg2.connect(
    host="127.0.0.1",
    database="Robot",
    user="postgres",
    password="1234"
)
    cur = conn.cursor()    
    # Получаем данные из формы
    date = datetime.date.today().strftime('%d/%m/%Y')
    time = datetime.datetime.now().strftime("%H:%M:%S")    
    # Формируем SQL-запрос на добавление данных
    query = """ INSERT INTO "Tasks" ("date","time") VALUES (%s, %s) """
    data = (date, time)    
    # Выполняем запрос и фиксируем изменения
    cur.execute(query, data)
    conn.commit()    
    # Закрываем соединение с базой данных
    cur.close()
    conn.close()    
    # Выводим сообщение об успешном добавлении данных
    return render_template("washing.html")

@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/parameters')
def parameters():
    return render_template("parameters.html",  data_speed=data_speed, data_state=data_state, data_voltage=data_voltage, data_current=data_current,data_angle=data_angle,data_pwn=data_pwn, data_coords=data_coords, data_dst=data_dst, data_passed=data_passed, data_ik=data_ik, data_ld=data_ld)


@app.route('/controller')
def showController():
    return render_template('controller.html')

# Маршрут для перемещения робота вперед
@app.route('/move_forward', methods=['POST'])
def move_forward():
    distance = request.form.get('distance')
    speed = request.form.get('speed')
    robot.move_forward(distance=float(distance), speed=float(speed))
    return 'Success'

# Маршрут для перемещения робота назад
@app.route('/move_backward', methods=['POST'])
def move_backward():
    distance = request.form.get('distance')
    speed = request.form.get('speed')
    robot.move_backward(distance=float(distance), speed=float(speed))
    return 'Success'

# Маршрут для поворота робота влево
@app.route('/turn_left', methods=['POST'])
def turn_left():
    angle = request.form.get('angle')
    speed = request.form.get('speed')
    robot.turn_left(angle=float(angle), speed=float(speed))
    return 'Success'

# Маршрут для поворота робота вправо
@app.route('/turn_right', methods=['POST'])
def turn_right():
    angle = request.form.get('angle')
    speed = request.form.get('speed')
    robot.turn_right(angle=float(angle), speed=float(speed))
    return 'Success'

# Маршрут для остановки движения робота
@app.route('/stop', methods=['POST'])
def stop():
    robot.stop()
    return 'Success'

cur.close()
conn.close()


if __name__=="__main__":
    app.run(debug=True)
