from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

import certifi

ca = certifi.where()

client = MongoClient()
db = client.dbsparta

@app.route('/home', methods=['GET'])
def home_get():
    title = "HI"
    return render_template("home.html", title = title)

@app.route('/', methods=['GET'])
def signin_get():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 토큰이 유효할 경우 main 화면으로 이동
        return render_template('home.html')
    except jwt.ExpiredSignatureError:
        return render_template("login.html")
        # return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return render_template("login.html")
        # return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/', methods=['POST'])
def signin_post():

    userid_receive = request.form['userid_give']
    userpassword_receive = request.form['userpassword_give']
    pw_hash = hashlib.sha256(userpassword_receive.encode('utf-8')).hexdigest()

    result = db.tripinkorea.find_one({"userid" : userid_receive, "userpassword" : pw_hash})

    # 회원 정보가 db에 존재하지 않을 경우
    if result is None:
        err = '아이디/비밀번호가 일치하지 않습니다.'
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

    # 회원 정보가 db에 존재할 경우
    payload = {
     'id': userid_receive,
     'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
    return jsonify({'result': 'success', 'token': token})

@app.route('/members/new', methods=['POST'])
def createAccount_post():

    userid_receive = request.form["userid_give"]
    userpassword_receive = request.form['userpassword_give']
    pw_hash = hashlib.sha256(userpassword_receive.encode('utf-8')).hexdigest()
    username_receive = request.form['username_give']

    doc = {
        "userid" : userid_receive,
        "userpassword" : pw_hash,
        "username" : username_receive
    }

    db.tripinkorea.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/members/new', methods=['GET'])
def createAccount_get():
    return render_template("createAccount.html")


@app.route('/members/new/check_dup', methods=['POST'])
def check_duplicate_userId():
    userid_receive = request.form['userid_give']
    exists = bool(db.users.find_one({"username": userid_receive}))
    return jsonify({'result': 'success', 'exists': exists})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

