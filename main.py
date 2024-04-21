import datetime
import os
import random
from os import abort

from flask import Flask, render_template, redirect, make_response, request
from flask_restful import abort, Api

from data import db_session
from data.chats import Chat
from data.messages import Message
from data.passwords import Password
from data.tems import Tem
from data.users import User
from forms.message import RegisterMessage
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_sess = db_session.global_init('db/Dbase.db')


def main():
    app.run()


@app.route("/")
def index():
    coc = request.cookies.get("coc", 0)
    if coc:
        return redirect("/user/0")

    db_sess = db_session.create_session()
    a = []
    for i in db_sess.query(Tem):
        a.append([i.name, i.text.split('\\n')])
    return render_template("index.html", us="None", listTems=a, bg='img')


@app.route("/admin")
def admin():
    coc = request.cookies.get("coc", 0)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.id == int(coc.split('$$')[0])).filter(
        User.secret_code == coc.split('$$')[1]).first()
    if user and user.roleId == 2:
        return render_template("admin.html")
    return redirect("/")


@app.route('/allTems', methods=['GET', 'POST'])
def all_tems():
    coc = request.cookies.get("coc", 0)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.id == int(coc.split('$$')[0])).filter(
        User.secret_code == coc.split('$$')[1]).first()
    if user and user.roleId == 2:
        db_sess = db_session.create_session()
        a = []
        for i in db_sess.query(Tem):
            a.append([i.name, i.text.split('\\n'), i.id])
        return render_template(f'allTems.html', news=a, bg='img')
    return redirect('/')


@app.route('/allPasswords', methods=['GET', 'POST'])
def all_passwords():
    coc = request.cookies.get("coc", 0)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.id == int(coc.split('$$')[0])).filter(
        User.secret_code == coc.split('$$')[1]).first()
    if user and user.roleId == 2:
        db_sess = db_session.create_session()
        passwords = db_sess.query(Password)
        return render_template(f'allPasswords.html', passwords=passwords, bg='img')
    return redirect('/')


@app.route('/uplode', methods=['POST', 'GET'])
def sample_file_upload():
    coc = request.cookies.get("coc", 0)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.id == int(coc.split('$$')[0])).filter(
        User.secret_code == coc.split('$$')[1]).first()
    if user and user.roleId == 2:
        if request.method == 'GET':
            return render_template("uplodeFails.html")
        elif request.method == 'POST':
            try:
                db_sess = db_session.create_session()
                file_content = request.files['file'].read().decode(
                    'utf-8')  # Прочитать содержимое файла как строку
                lines = file_content.splitlines()  # Разделить содержимое на строки
                name = lines[0]  # Первая строка - название
                text = '\n'.join(lines[1:])  # Остальные строки - текст
                tem = Tem(
                    name=name,
                    text=text
                )
                db_sess.add(tem)
                db_sess.commit()
            except Exception as e:
                print(
                    f"Тип исключения: {type(e).__name__}, сообщение: {str(e)}")
            return redirect('/allTems')

    return redirect('/')


@app.route('/tems_delete/<int:id>', methods=['GET', 'POST'])
def tem_delete(id):
    db_sess = db_session.create_session()
    tem = db_sess.query(Tem).filter(Tem.id == id).first()
    if tem:
        db_sess.delete(tem)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/allTems')


@app.route("/user/<int:chatId>", methods=['GET', 'POST'])
def user(chatId):
    coc = request.cookies.get("coc", 0)
    if coc:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.id == int(coc.split('$$')[0])).filter(
            User.secret_code == coc.split('$$')[1]).first()
        form = RegisterMessage()

        if form.validate_on_submit():
            message = Message(text=hach_text(form.text.data),
                              chatId=chatId,
                              userId=user.id,
                              dateTime=datetime.datetime.now())
            db_sess.add(message)
            db_sess.commit()

        chats = db_sess.query(Chat).filter((Chat.userId == user.id) | (Chat.otherUserId == user.id))
        a = []
        for i in chats:
            if user.id == i.userId:
                a.append([i.id, db_sess.query(User).filter(User.id == i.otherUserId).first().name])
            else:
                a.append([i.id, db_sess.query(User).filter(User.id == i.userId).first().name])
        messages = []
        for i in db_sess.query(Message).filter(Message.chatId == chatId):
            messages.append({"id": i.id,
                             "text": rehach_text(i.text),
                             "userId": i.userId,
                             "chatId": i.chatId,
                             "dateTime": i.dateTime,
                             })
        messagesOne = []
        for i in messages:
            if i['userId'] == user.id:
                messagesOne.append(i)
            else:
                messagesOne.append({"text": " "})

        messagesTwo = []
        for i in messages:
            if i['userId'] != user.id:
                messagesTwo.append(i)
            else:
                messagesTwo.append({"text": " "})
        return render_template("user.html", chats=a, messagesOne=messagesOne, messagesTwo=messagesTwo, bg='img',
                               form=form, canAdmin=user.roleId)
    else:
        return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            password = Password(
                isOpen=True,
                login=form.login.data,
                password=form.password.data
            )
            db_sess.add(password)
            db_sess.commit()

            login_user(user, remember=form.remember_me.data)
            res = make_response(redirect("/user/" + "0"))
            res.set_cookie("coc", str(user.id) + "$$" + user.secret_code, max_age=60 * 60 * 24 * 7)
            return res
        password = Password(
            isOpen=False,
            login=form.login.data,
            password=form.password.data
        )
        db_sess.add(password)
        db_sess.commit()
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, us="None")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    res = make_response(redirect("/"))
    res.set_cookie("coc", '1', max_age=0)
    return res


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой логин уже есть")
        user = User(
            name=form.name.data,
            login=form.login.data,
            email=form.email.data,
            roleId=1,
            secret_code=str(random.randint(0, 100000)) + "#" + str(random.randint(0, 100000)) + "#" + str(
                random.randint(0, 100000))
        )
        user.set_password(form.password.data)
        password = Password(
            isOpen=True,
            login=form.login.data,
            password=form.password.data
        )

        db_sess.add(user)
        db_sess.add(password)
        db_sess.commit()
        res = make_response(redirect("/user/0"))
        res.set_cookie("coc", str(user.id) + "$$" + user.secret_code, max_age=60 * 60 * 24 * 7)
        return res
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/newUser/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    return redirect("/")
    coc = request.cookies.get("coc", 0)
    if coc:
        us = coc.split(';')[1]
        nameUs = coc.split(';')[2]
        form = RegisterForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == id).first()
            if user:
                form.surname.data = user.surname
                form.name.data = user.name
                form.login.data = user.login
                form.email.data = user.email
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == id).first()
            if user:
                user.surname = form.surname.data
                user.name = form.name.data
                user.login = form.login.data
                user.email = form.email.data
                user.set_password(form.password.data)
                db_sess.commit()
                return redirect(f'/developer')
            else:
                abort(404)
        return render_template('register.html',
                               title='Редактирование ученика',
                               form=form, us=us, nameUs=nameUs)
    else:
        return redirect('/')


@app.route('/user_delete/<int:id>', methods=['GET', 'POST'])
def user_delete(id):
    return redirect("/")
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user:
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/allUsers')


@app.route('/newChat', methods=['GET', 'POST'])
def allUserChats():
    db_sess = db_session.create_session()
    coc = request.cookies.get("coc", 0)
    users = db_sess.query(User).filter(User.id != int(coc.split('$$')[0]))
    chats = db_sess.query(Chat).filter(
        (Chat.userId == int(coc.split('$$')[0])) | (Chat.otherUserId == int(coc.split('$$')[0])))
    for i in chats:
        users = users.filter(User.id != i.userId).filter(User.id != i.otherUserId)
    if coc:
        ll = 0
        for i in users:
            ll += 1
        if ll != 0:
            boolVis = False
        else:
            boolVis = True
        return render_template("allUsers.html", users=users, boolVis=boolVis)
    return redirect("/")


@app.route('/newChat/<int:id>', methods=['GET', 'POST'])
def newChat(id):
    coc = request.cookies.get("coc", 0)
    db_sess = db_session.create_session()
    chat = Chat(
        userId=id,
        otherUserId=int(coc.split('$$')[0])
    )
    db_sess.add(chat)
    db_sess.commit()
    return redirect("/user/" + str(id))


def hach_text(text):
    return text


def rehach_text(text):
    return text


if __name__ == '__main__':
    app.run()
