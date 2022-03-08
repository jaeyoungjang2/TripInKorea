from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def mypage():
    return render_template('mypage.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5500, debug=True)
