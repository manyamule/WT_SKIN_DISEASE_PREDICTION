from flask import Flask, render_template, request,flash
from tensorflow import keras
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'SkinDisease'
app.config['SECRET_KEY'] = 'sumit1410'

mysql = MySQL(app)

dic = {0: 'cellulitis', 1: 'impetigo', 2: 'Athletes Foot', 3: 'Nail Fungus', 4: 'ringworm', 5: 'Cutaneous Larva Migrans', 6: 'chickenpox', 7: 'shingles'}

model = load_model('skin.h5')
model.make_predict_function()

img_size = (234,234)

#function for preprocessing...
def preprocess_image(image_path):
    img = image.load_img(image_path,target_size=img_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array,axis=0)
    return img_array

def predict_image(img_path):
    processed_image = preprocess_image(img_path)
    preds = model.predict(processed_image)
    predicted_class = dic[np.argmax(preds)]
    confidence = np.max(preds)*100
    
    return np.argmax(preds),confidence




@app.route('/')
def index():
    
   # cur.execute("CREATE TABLE IF NOT EXISTS users2 (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL)")
   # mysql.connection.commit()
   # cur.close()
   cur = mysql.connection.cursor()
   return render_template('index.html')

@app.route('/login')
def loginpage():
    return render_template('login.html')

@app.route('/login2',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        # Check if the user exists and the password is correct
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user_data = cur.fetchone()

        if user_data:
            flash('Login successful!', 'success')
            return render_template('Banner.html')

        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        # Check if the username is already registered
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
        else:
            # Create a new user
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            flash('Registration successful. Please log in.', 'success')
            return render_template('login.html')

    return render_template('login.html')




@app.route('/Banner')
def index2():
    return render_template('Banner.html')

@app.route('/index')
def index3():
    return render_template('index2.html')

@app.route('/submit', methods=['POST', 'GET'])
def get_output():
  if request.method == 'POST':
    img = request.files['my_image']
    cur = mysql.connection.cursor()
    img_path = "static/upload/" + img.filename
    img.save(img_path)
    p ,accuracy= predict_image(img_path)
    cur.execute("SELECT * FROM diseases WHERE srno = %s",(p+1,))
    users = cur.fetchall()
    print(type(p))

  return render_template("result.html",prediction=users[0][1], img_path=img_path,accuracy=accuracy,info=users)

if __name__ == "__main__":
    app.run(debug=True)
