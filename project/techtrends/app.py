import sqlite3
import os
import logging
from datetime import datetime
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

now = datetime.now()
timestamp = now.strftime("%m/%d/%Y, %H:%M:%S")

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone() 
    if post:
        app.logger.info('%s, Article "%s" retrieved!', timestamp, post['title'])
    else:
        app.logger.error('%s, Article does not exist!', timestamp)
    connection.close()
    
    return post      
 
# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()    
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)   
    
    if post is None:        
        return render_template('404.html'), 404
    else:        
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('%s, About Us page retrieved!', timestamp)
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit() 
            app.logger.info('%s, Article "%s" created!', timestamp, title)            
            connection.close()

            return redirect(url_for('index'))
            
    return render_template('create.html')

@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('%s, Health Check request successful', timestamp)
    return response

@app.route('/metrics')
def metrics():
    conn = get_db_connection()
    db_conn = 0
    if conn:
        db_conn +=1        
        
    posts = conn.execute('SELECT * FROM posts').fetchall()
    num_posts = len(posts)        
    
    response = app.response_class(
            response=json.dumps({"status":"success", "data": {"db_connection_count": db_conn , "post_count": num_posts}}),
            status=200,
            mimetype='application/json'
    )    
    app.logger.info('%s, Metrics request successful', timestamp)
    return response

# start the application on port 3111
if __name__ == "__main__":  
     
    # stream logs to app.log file
    # logging.basicConfig(filename='app.log',level=logging.DEBUG)

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    
    app.run(host='0.0.0.0', port='3111')
                     