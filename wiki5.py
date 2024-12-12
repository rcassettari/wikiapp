from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, g 
import MySQLdb
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'dbserver01'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin123456'
app.config['MYSQL_DB'] = 'wikidb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Config MySQL
DB_CONFIG = {
    'host': 'awsuse1db01.ch2wiuwyggwl.us-east-1.rds.amazonaws.com',
    'user': 'wiki',
    'passwd': 'admin123456',
    'db': 'wikidb'
}

# Begin - old code 
# init MYSQL
#mysql = MySQL(app)
# End - old code 

#Articles = Articles()

# Connect to the database before each request
@app.before_request
def before_request():
    try:
        g.db = MySQLdb.connect(**DB_CONFIG)
    except Exception as e:
        app.logger.error(f"Erro ao conectar ao banco: {e}")

# Close the database connection after each request
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Articles
@app.route('/articles')
def articles():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    # Close connection
    cur.close()


#Single Article
@app.route('/article/<string:id>/')
def article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    return render_template('article.html', article=article)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# BEGIN - old code 
# User Register
#@app.route('/register', methods=['GET', 'POST'])
#def register():
#    form = RegisterForm(request.form)
#    if request.method == 'POST' and form.validate():
#        name = form.name.data
#        email = form.email.data
#        username = form.username.data
#        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
#        cur = mysql.connection.cursor()

        # Execute query
#        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
#        mysql.connection.commit()

        # Close connection
#        cur.close()

#        flash('You are now registered and can log in', 'success')

 #       return redirect(url_for('login'))
 #   return render_template('register.html', form=form)
 # END - old code 
    
# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data
            email = form.email.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))

            cur = g.db.cursor()
            cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                        (name, email, username, password))
            g.db.commit()
            cur.close()

            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Erro ao registrar usuário: {e}")
            return f"Erro ao registrar usuário: {e}"
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = g.db.cursor()

        # Get user by username
        result = cur.execute("SELECT password FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data[0]
 
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')
    
#New wiki4 code 
# User login
#@app.route('/login', methods=['GET', 'POST'])
#def login():
#    if request.method == 'POST':
#        try:
#            username = request.form['username']
#            password_candidate = request.form['password']

#            cur = g.db.cursor()
#            result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

#            if result > 0:
#                data = cur.fetchone()
#                password = data['password']
#                cur.close()

#                if sha256_crypt.verify(password_candidate, password):
#                    session['logged_in'] = True
#                    session['username'] = username
#                    flash('You are now logged in', 'success')
#                    return redirect(url_for('dashboard'))
#                else:
#                    error = 'Invalid login'
#                    return render_template('login.html', error=error)
#            else:
#                error = 'Username not found'
#                return render_template('login.html', error=error)
#        except Exception as e:
#            app.logger.error(f"Erro ao fazer login: {str(e)}")
#            return f"Erro ao fazer login: {str(e)}"
#    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = g.db.cursor()

    # Get articles
    #result = cur.execute("SELECT * FROM articles")
    # Show articles only from the user logged in 
    result = cur.execute("SELECT id, title, author FROM articles WHERE author = %s", [session['username']])

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()

# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        cur = g.db.cursor()        

        # Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

        # Commit to DB
        g.db.commit()

        #Close connection
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)


# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    cur.close()
    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(title)
        # Execute
        cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
        # Commit to DB
        mysql.connection.commit()

        #Close connection
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    #Close connection
    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(host='0.0.0.0',port=8080, debug=True)

