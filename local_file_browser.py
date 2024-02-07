from flask import Flask, send_from_directory, render_template_string, request, redirect, url_for, session, render_template_string, render_template
from threading import Thread
import os
import requests
import sys
import random
from functools import wraps

# initialize Flask
app = Flask(__name__)
app.debug = True # Change to 'True' if you need more information
flask_pass = "{:04d}".format(random.randint(0, 9999)) #generate 4 digit random password
app.secret_key = flask_pass  # Change to a random secret key

typewrytes_dir = os.path.join(os.path.dirname(__file__), 'TypeWrytes')
server_thread = None

ascii_art_lines = [
    "+-----------------------------------+",
    "| _____                             |",
    "||_   _|   _ _ __   ___             |",
    "|  | || | | | '_ \\ / _ \\            |",
    "|  | || |_| | |_) |  __/            |",
    "|  |_| \\__, | .__/ \\___|            |",
    "|__    |___/|_|        _            |",
    "|\\ \\      / / __ _   _| |_ ___ _ __ |",
    "| \\ \\ /\\ / / '__| | | | __/ _ \\ '__||",
    "|  \\ V  V /| |  | |_| | ||  __/ |   |",
    "|   \\_/\\_/ |_|   \\__, |\\__\\___|_|   |",
    "|                |___/              |",
    "+-----------------------------------+",
]

def require_password(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if session.get('authenticated') != True:
            return redirect(url_for('login', next=request.url))
        return view_function(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == flask_pass:
            session['authenticated'] = True
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            return "Incorrect password", 403
    return render_template_string('''
        <form method="post">
            Password: <input type="password" name="password">
            <input type="submit" value="Login">
        </form>
    ''')

@app.route('/')
@require_password
def index():
    files = os.listdir(typewrytes_dir)
    ascii_art = "\n".join(ascii_art_lines)  # Convert list to string
    return render_template("index.html", files=files, ascii_art=ascii_art)

@app.route('/rename', methods=['POST'])
@require_password
def rename_file():
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    try:
        os.rename(os.path.join(typewrytes_dir, old_name), os.path.join(typewrytes_dir, new_name))
        return 'File renamed successfully'
    except FileNotFoundError:
        return 'File not found', 404

@app.route('/download/<filename>')
@require_password
def download_file(filename):
    try:
        return send_from_directory(typewrytes_dir, filename, as_attachment=True)
    except FileNotFoundError:
        return 'File not found', 404

@app.route('/delete', methods=['POST'])
@require_password
def delete_file():
    filename = request.form.get('filename')
    file_path = os.path.join(typewrytes_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return 'File deleted successfully'
    else:
        return 'File not found', 404

def run_server():
    try:
        log_file = 'web_server.log'
        with open(log_file, 'a') as log:
            app.run(host='0.0.0.0', port=5000, use_reloader=False)
            print("Server started", file=log)
    except Exception as e:
        with open('web_server.log', 'a') as log:
            print(f"An error occurred: {e}", file=log)

def start_server():
    global server_thread
    if server_thread is None:
        server_thread = Thread(target=run_server)
        server_thread.start()
        print("Starting Server")
    return flask_pass

def stop_server():
    global server_thread
    try:
        if server_thread:
            requests.get('http://localhost:8080/shutdown')
            server_thread.join()
            server_thread = None
            # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    except Exception as e:
        with open('web_server.log', 'a') as log:
            print(f"An error occurred: {e}", file=log)
        

@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func:
        shutdown_func()
    return 'Server shutting down...'