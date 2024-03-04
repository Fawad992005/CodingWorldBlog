from flask import Flask,render_template,url_for,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import math
#local_server = True
with open('config.json','r') as c:
    params = json.load(c)["params"]
app = Flask(__name__)
app.secret_key = 'super-secret-key'
if (params["local_uri"]):
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]
db = SQLAlchemy(app)

class Contacts(db.Model):
    # sno,name,msg,email,date,phone number
    # same order as in database table
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email_address = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    msg = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(12), nullable=True)
class Post(db.Model):
    # sno,name,msg,email,date,phone number
    # same order as in database table
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    img_file = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route('/')
def home():
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_post']))
    page = request.args.get('page')
    
    if(not str(page).isnumeric()):
        page = 1
    page=int(page)
    posts = posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    if (page==1):
        prev = '#'
        next = "/?page=" + str(page+1)
    elif(page==last):
        next = '#'
        prev = "/?page=" + str(page-1)
    else:
        next = "/?page=" + str(page+1)
        prev = "/?page=" + str(page-1)

    #params=params to include in render_template
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)
@app.route('/about')
def about():
    return render_template('about.html',params=params)
@app.route("/edit/<string:sno>", methods=['GET','POST'] )
def edit(sno):
    if ('user' in session and session['user']==params['admin_name']):
        if request.method=='POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date=datetime.now()
            if sno=='0':
                posts = Post(title=box_title,tagline=tline,slug=slug,content=content,img_file=img_file,date=date)
                db.session.add(posts)
                db.session.commit()
                return redirect("/dashboard")
            else:
                post = Post.query.filter_by(sno=sno).first()
                post.title = box_title
                post.tagline = tline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect("/dashboard")
        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post)
    #return redirect("/dashboard")
    

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user']==params['admin_name']):
        posts = Post.query.all()
        return render_template('panel.html',params=params,posts=posts)

    if request.method == "POST":
        username = request.form.get('uname')
        password = request.form.get('pass')
        if (username==params['admin_name'] and password==params['admin_password']):
            session['user'] = username
            posts = Post.query.all()
            return render_template('panel.html',params=params,posts=posts)
        
    return render_template('dashboard.html',params=params)

@app.route("/delete/<string:sno>", methods=['GET','POST'] )
def delete(sno):
    if ('user' in session and session['user']==params['admin_name']):
        post = Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')
    
@app.route('/contact', methods=['GET','POST'])
def contact():
    # Add entry to database
    if(request.method=="POST"):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name,email_address=email,phone_number=phone,msg=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
         
    return render_template('contact.html',params=params)
@app.route('/post/<string:post_slug>', methods= ['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html',params=params,post=post)

app.run(debug=True)