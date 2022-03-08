#app.py
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
from pytz import timezone
from werkzeug.utils import secure_filename, redirect

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.okxdx.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

# @app.route('/home', methods=['GET'])
# def home_get():
#     user_info = db.test1.find_one({"userid": "test"})
#     # lists=list(db.test1.find({})) #test1 db에 저장돼있는 모든 내용 추출
#     # return render_template("mainpage.html",lists=lists) #추출한 내용 보여주기 위해 html파일로 정보 넘김
#     return render_template("home.html", user_info=user_info)
@app.route('/home', methods=['GET'])
def home_get():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = payload["id"]
        user_info = db.test1.find_one({"userid": userid})
        return render_template("home.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/user/<username>', methods=['GET'])
def user_get(username): #마이페이지에 게시물 표현하는 메소드
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = payload["id"]
        docs = list(db.doc.find({'userid': userid}, {'_id': False}))
        return render_template("user.html", docs=docs, username=username)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

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

    result = db.test1.find_one({"userid" : userid_receive, "userpassword" : pw_hash})

    # 회원 정보가 db에 존재하지 않을 경우
    if result is None:
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
    db.test1.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/members/new', methods=['GET'])
def createAccount_get():
    return render_template("createAccount.html")


@app.route('/members/new/check_dup', methods=['POST'])
def check_duplicate_userId():
    userid_receive = request.form['userid_give']
    exists = bool(db.test1.find_one({"userid": userid_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/write')
def write():
    return render_template('writing.html')
@app.route('/writepage', methods=['GET', 'POST'])
def write_post():
    img_receive = request.files["chooseFile"]
    area_receive = request.form['area']
    comment_receive = request.form['comment_box']
    img_name = secure_filename(img_receive.filename)
    file_path = 'static/upload'

    # 파일 업로드
    img_receive.save(file_path + img_name)

    doc = {
        "img": img_name,
        "area": area_receive,
        "comment": comment_receive,
        'pubdate': datetime.now(timezone('Asia/Seoul')).strftime('%y%m%d_%H:%M:%S')
    }
    db.test1.insert_one(doc)
    return redirect(url_for('home_get'))  # 게시글 추가 후 자연스럽게 메인페이지 이동

# @app.route('/upload',methods=["POST"])
# def upload():
#     area=request.form['area']
#     comment=request.form['comment_box']
#     print(area, comment)
#     doc={ #지역정보와 코멘트내용 발행시간을 데이터베이스에 저장
#         'area':area,
#         'comment':comment,
#         'pubdate': datetime.now(timezone('Asia/Seoul')).strftime('%y%m%d_%H:%M:%S')
#     }
#     db.test1.insert_one(doc) #몽고db에 insert하는 동작
#     return redirect(url_for('home_get')) #게시글 추가 후 자연스럽게 메인페이지 이동

@app.route('/sort')
def sortByArea():
    area=request.args.get('area') #GET방식으로 보낸 정보를 가져오는 코드
    print('area:',area)
    lists=list(db.test1.find({'area':area})) #db에서 지역 이름을 기준으로 해당 지역 전부 추출
    return render_template('mainpage.html',lists=lists) #메인페이지에 진자2 문법 활용을 위한 리스트변수 제공

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)