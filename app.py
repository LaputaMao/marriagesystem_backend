from flask import Flask, request, g, Flask, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwtForApp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:626626@127.0.0.1:3306/marriagesystem'
app.config["SQLALCHEMY_TRACE_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "marriage_system"
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class CipherTable(db.Model):
    __tablename__ = 'ciphertable'
    uuid = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True)
    password = db.Column(db.Integer, index=True)

    # __table_args__ = (
    #     db.UniqueConstraint("username", name='unique_username'),
    # )

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    # def verify_password(self, password) -> bool:
    #     if self.password == password:
    #         return True
    #     else:
    #         return False


# 装饰器-在处理请求之前验证token
@app.before_request
def authentication():
    jwtForApp.jwt_authentication()


# 登录
@app.route('/login', methods=['get', 'post'])
def login():  # put application's code here

    # cipher1 = CipherTable('周行云', 232523)
    # db.session.add(cipher1)
    # db.session.commit()
    if request.method == 'GET':  # 请求方式是get
        return "use method POST"
    elif request.method == 'POST':
        _username = request.form.get('username', type=str)  # form取post方式参数
        _password = request.form.get('password', type=str)

        _user = CipherTable.query.filter_by(username=_username).first()
        if _user is not None:
            if _user.password == _password:
                _token = jwtForApp.create_token(_username, _password)
                return {"code": 200, "message": "success", "data": {"token": _token}}
            else:
                return {"code": 501, "message": "密码错误"}
        else:
            return {"code": 501, "message": "用户不存在"}


# 注册
@app.route('/signup', methods=['get', 'post'])
def sign_up():
    if request.method == 'GET':  # 请求方式是get
        return "use method POST"
    elif request.method == 'POST':
        _username = request.form.get('username', type=str)  # form取post方式参数
        _password = request.form.get('password', type=str)

        _user = CipherTable.query.filter_by(username=_username).first()
        # 添加新用户
        if _user is None:
            _add_user = CipherTable(_username, _password)
            db.session.add(_add_user)
            db.session.commit()
            return {"code": 200, "message": "注册成功"}
        else:
            return {"code": 501, "message": "用户名已存在"}


# 在需要登陆权限的页面启用token验证-login_requried
@app.route('/main', methods=['get', 'post'])
@jwtForApp.login_required
def main():
    username = g.username
    return username


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
