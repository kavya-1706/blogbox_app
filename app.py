import bottle
from bottle import route, run, request, template, redirect
from pymongo import MongoClient
from bson import ObjectId
import os

client = MongoClient('mongodb://localhost:27017/')
db = client.blogdb
users_collection = db.users
blogs_collection = db.blogs

@route('/')
def index():
    return template('index')

@route('/signup', method='GET')
def signup():
    return template('signup')

@route('/signup', method='POST')
def do_signup():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if users_collection.find_one({'username': username}):
        return template('user_exist')
    else:
        users_collection.insert_one({'username': username, 'password': password})
        return template('signup_success')

@route('/login', method='GET')
def login():
    return template('login')

@route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    user = users_collection.find_one({'username': username, 'password': password})
    if user:
        return template('login_success')
    else:
        return template('login_fail')

from bottle import route, request, template

@route('/addpost', method=['GET', 'POST'])
def add_post():
    if request.method == 'GET':
    
        return template('add_post.html')
    elif request.method == 'POST':
        title = request.forms.get('title')
        content = request.forms.get('content')
        
        image = request.files.get('image')
        if image:
            try:
               
                filename = image.filename
                image.save('uploads', overwrite=True)
               
                image_url = f"/uploads/{filename}"
            except Exception as e:
                return f"Error uploading image: {e}"
        else:
            image_url = None

        blogs_collection.insert_one({'title': title, 'content': content, 'image_url': image_url})
        return template('post_added')

@route('/search', method='GET')
def search():
    query = request.query.get('query')
   
    results = blogs_collection.find({
        '$or': [
            {'title': {'$regex': query, '$options': 'i'}},
            {'content': {'$regex': query, '$options': 'i'}}
        ]
    })
    search_results = list(results)
    return template('search_results', search_results=search_results)



@route('/blog')
def blog():
    blogs = blogs_collection.find()
    blog_posts=list(blogs)
    return template('blog', blog_posts=blog_posts)

@route('/updatepost/<post_id>', method=['GET', 'POST'])
def update_post(post_id):
    if request.method == 'GET':
        post = blogs_collection.find_one({'_id': ObjectId(post_id)})
        if post:
            return template('update_post', post=post)
        else:
            return template('post_not_found')
    elif request.method == 'POST':
        title = request.forms.get('title')
        content = request.forms.get('content')
        blogs_collection.update_one({'_id': ObjectId(post_id)}, {'$set': {'title': title, 'content': content}})
        return template('post_update')



@route('/deletepost/<post_id>', method='GET')
def delete_post(post_id):
    result = blogs_collection.delete_one({'_id': ObjectId(post_id)})
    if result.deleted_count > 0:
        return template('post_delete')
    else:
        return template('post_not_found')


@route('/static/<filename:path>')
def send_static(filename):
    return bottle.static_file(filename, root='./static')

@route('/uploads/<filename:path>')
def serve_image(filename):
    return bottle.static_file(filename, root='uploads')

if __name__ == '__main__':
    bottle.run(host='localhost', port=8080, debug=True)
