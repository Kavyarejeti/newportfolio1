from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to something secure
app.config.from_pyfile('config.py')

mail = Mail(app)
PROJECTS_FILE = 'data/projects.json'

# Load Projects from JSON
def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return []
    with open(PROJECTS_FILE, 'r') as f:
        return json.load(f)

# Save Projects to JSON
def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=4)

# Home
@app.route('/')
def index():
    return render_template("index.html")

# About
@app.route('/about')
def about():
    return render_template("about.html")

# Projects Page
@app.route('/projects')
def projects():
    return render_template("projects.html", projects=load_projects())

# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            msg = Message(
                subject=request.form['subject'],
                sender=request.form['email'],
                recipients=[app.config['MAIL_USERNAME']],
                body=f"From: {request.form['name']} <{request.form['email']}>\n\n{request.form['message']}"
            )
            mail.send(msg)
            return render_template("contact.html", message_sent=True)
        except Exception as e:
            return render_template("contact.html", error=str(e))
    return render_template("contact.html")

# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

# Admin Panel
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    projects = load_projects()

    if request.method == 'POST':
        new_project = {
            "title": request.form['title'],
            "description": request.form['description'],
            "link": request.form['link']
        }
        projects.append(new_project)
        save_projects(projects)
        return redirect(url_for('admin'))

    return render_template("admin.html", projects=projects)

# Run App
if __name__ == '__main__':
    app.run(debug=True)
