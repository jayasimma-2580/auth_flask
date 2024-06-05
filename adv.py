from flask import Flask,render_template,request,redirect,url_for,flash
import mysql.connector
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

class User(UserMixin):
    def __init__(self,id, username):
          self.id=id
          self.username = username


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'advocate'
}

conn = mysql.connector.connect(**db_config)

cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT id, email FROM advocate WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return User(id=user_data[0], username=user_data[1])
    return None


@app.route('/')
def hello_world():
     return render_template('login.html')

@app.route('/login')
def lg():
     return render_template('login.html')

@app.route('/signup')
def loog():
     return render_template('signup.html')

@app.route('/signup',methods=['POST'])
def signup():
    email=request.form.get('email')
    password=request.form.get('password')
    phone=request.form.get('phone')
    insert_data_query = '''
    INSERT INTO `advocate` (`email`, `password`, `phone`) VALUES (%s,%s,%s)
    '''
    data = (email,password,phone)
    r=cursor.execute(insert_data_query, data)
    conn.commit()
    print(r)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM advocate WHERE email = %s", (username,))
        user_data = cursor.fetchone()
        

        if user_data and password == user_data[1]:
            user = User(id=user_data[0], username=username)
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('protected_route'))

        flash('Login failed. Check your credentials.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/protected')
@login_required
def protected_route():
    return render_template('user.html')

@app.route('/forgot',methods=['GET','POST'])
def forgot_pass():
    if request.method == 'GET':
        return render_template('forgot.html')
    
    if request.method == 'POST':
        username = request.form.get('email')
        cursor.execute("SELECT email FROM advocate WHERE email = %s", (username,))
        user_data = cursor.fetchone()
        if(user_data):
            return render_template('reset.html')
        else:
            return render_template('forgot.html')


    
# Run the application if this script is executed
if __name__ == '__main__':
    app.run(debug=True)