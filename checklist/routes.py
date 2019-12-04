
from flask import render_template, url_for, flash, redirect, request
from checklist import app, db, bcrypt, mail
from checklist.forms import SignUpForm, LoginForm, TaskForm, RequestResetForm, ResetPasswordForm
from checklist.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('tasks'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('index.html', title='Login', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. You are now able to log in.','success')
        return redirect(url_for('index'))
    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/tasks')
@login_required
def tasks():
    posts = Post.query.filter_by(author=current_user)
    return render_template('tasks.html', title='Tasks',posts=posts)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def task_add():
    form = TaskForm()
    if form.validate_on_submit():
        post = Post(task=form.task.data, description=form.description.data, due_date=form.due_date.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Task has been added','success')
        return redirect(url_for('tasks'))
    return render_template('add.html', title='Add Task', form=form, legend='New Task')

@app.route('/tasks/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def task_update(post_id):
    post = Post.query.get(post_id)
    form = TaskForm()
    if form.validate_on_submit():
        post.task = form.task.data
        post.description = form.description.data
        post.due_date = form.due_date.data
        db.session.commit()
        flash('Your task has been updated.', 'success')
        return redirect(url_for('tasks'))
    elif request.method == 'GET':
        form.task.data = post.task
        form.description.data = post.description
        form.due_date.data = post.due_date
    return render_template('add.html', title='Update Task', form=form, legend='Update Task')

@app.route('/tasks/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def task_delete(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Your task has been deleted.', 'success')
    return redirect(url_for('tasks'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='email', recipients=[user.email])
    msg.body = f'''Please visit the following link to reset your password: {url_for('reset_token', token=token, _external=True)}
    
If you did not make the request. Please ignore this email.
    '''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('index'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    user = User.verify_reset_token(token)
    if user is None:
        flask('This is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been successfully changed.','success')
        return redirect(url_for('index'))
    return render_template('reset_token.html', title='Reset Password', form=form)
