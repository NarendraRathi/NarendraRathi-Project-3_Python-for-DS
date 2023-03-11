from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import sklearn
  
app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb')) # loading the trained model

app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@J5k5l56q'
app.config['MYSQL_DB'] = 'loan_Predictor'
 
mysql = MySQL(app)
 
@app.route('/')
def home():
     return render_template('home.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('predict.html')
            
        else:
                msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
@app.route('/predict',methods=['POST'])
def predict():                
 
                if request.method == 'POST':
                    gender=float(request.form['gender'])
                    married = int(request.form['married'])
                    dependents = int(request.form['dependents'])
                    education = request.form['education']
                    self_employed = request.form['self_employed']
                    applicantincome=request.form['applicantincome']
                    coapplicantincome=request.form['coapplicantincome']
                    loanamount=request.form['loanamount']
                    loan_amount_term=request.form['loan_amount_term']
                    credit_history=request.form['credit_history']
                    property_area=request.form['property_area']
            
                    prediction = model.predict([[ gender,married,dependents,education,self_employed,applicantincome,coapplicantincome,loanamount,loan_amount_term,credit_history,property_area]]) # making prediction

                    output=round(prediction[0],3)
                if(output>0.5):
                    return render_template('predict.html', prediction_text="Congrats!! You are eligible for the loan ".format(output)) # rendering the predicted result 
                else:
                    return render_template('predict.html', prediction_text="oh!!! You are  not eligible for the loan ".format(output)) # rendering the predicted result 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form  :
        username = request.form['username']
        password = request.form['password']
        # email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password :
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s)', (username, password, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)



if __name__ == "__main__":
    app.run(debug=True)