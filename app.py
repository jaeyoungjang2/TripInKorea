from flask import Flask, render_template, request, jsonify,redirect
from flask import session, escape

from pymongo import MongoClient

client = MongoClient('')

db = client.dbch

app = Flask(__name__)

@app.route('/mainpage',methods=['GET'])
def mainpage_list():
    return

@app.route('/writepage',methods=['POST'])
def mainpage_list():

    return

@app.route('/detail/<idx>/<page>',methods=['GET'])
def detail(idx,page):
    if db.boards.find_one({'_id':ObjectId(idx)}):
        boards_data = db.boards.find_one({'_id': ObjectId(idx)})
        view = boards_data.get('view_cnt')
        view += 1
        db.boards.update_one({'_id': ObjectId(idx)},{'$set':{'view_cnt':view}})
        if boards_data != "":
            doc = {
                'id':boards_data.get('_id'),
                'title':boards_data.get('title'),
                'writer' : boards_data.get('writer'),
                'comment' : boards_data.get('comment'),
                'content' : boards_data.get('content'),
                'noTagCon' : boards_data.get('noTagCon'),
                'view_cnt' : boards_data.get('view_cnt'),
                'likey' : boards_data.get('likey'),
                'pubdate' : boards_data.get('pubdate'),
                'uptdate': boards_data.get('uptdate'),
                'file' : boards_data.get('file'),
                'map': boards_data.get('map'),
                'category':boards_data.get('category')
            }
        if boards_data.get('rid'):
            reply_list=list(db.replies.find({'_id':{'$in': boards_data.get('rid')}}))
            print(reply_list)
            return render_template('detail.html', doc=doc, page=page, replies=reply_list)
        return render_template('detail.html', doc=doc, page=page)
    if not request.args.get("idx"):
        msg='게시물 정보 오류로 페이지 전환 이상 발생'
        return render_template('result.html',msg=msg)