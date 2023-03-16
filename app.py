from flask import Flask, request, g, Flask, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwtForApp
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:626626@127.0.0.1:3306/marriagesystem'
app.config["SQLALCHEMY_TRACE_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "marriage_system"
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


# 密码表
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


# 筛选信息表
class DisplayInfo(db.Model):
    __tablename__ = 'displayinfo'
    id = db.Column(db.Integer, primary_key=True)
    # 唯一约束需要在数据库表中设置
    username = db.Column('username', db.String(32), unique=True)
    constellation = db.Column(db.String(32))
    image = db.Column(db.String(32), unique=True)
    favorbook = db.Column(db.String(32))
    favorsong = db.Column(db.String(32))
    favormovie = db.Column(db.String(32))
    monologue = db.Column(db.String(255))
    tel = db.Column(db.String(255), unique=True)

    def __init__(self, username, constellation, image, favorbook, favorsong, favormovie, monologue, tel):
        self.username = username
        self.constellation = constellation
        self.image = image
        self.favorbook = favorbook
        self.favorsong = favorsong
        self.favormovie = favormovie
        self.monologue = monologue
        self.tel = tel

    def __repr__(self):
        return '<tel %r>' % self.tel


# 展示信息表
class FilterInfo(db.Model):
    __tablename__ = 'filterinfo'
    id = db.Column(db.Integer, primary_key=True)
    # 唯一约束需要在数据库表中设置
    username = db.Column('username', db.String(32), unique=True)
    gender = db.Column(db.String(32))
    edubackground = db.Column(db.String(32))
    workprovince = db.Column(db.String(32))
    nativeprovince = db.Column(db.String(32))
    salary = db.Column(db.String(32))
    marital = db.Column(db.String(32))
    nationality = db.Column(db.String(32))
    occupation = db.Column(db.String(32))
    houseornot = db.Column(db.String(32))
    carornot = db.Column(db.String(32))
    drinkornot = db.Column(db.String(32))
    specialty = db.Column(db.String(32))

    def __init__(self, username, gender, edubackground, workprovince, nativeprovince, salary, marital, nationality,
                 occupation, houseornot, carornot, drinkornot, specialty):
        self.username = username
        self.gender = gender
        self.edubackground = edubackground
        self.workprovince = workprovince
        self.nativeprovince = nativeprovince
        self.salary = salary
        self.marital = marital
        self.nationality = nationality
        self.occupation = occupation
        self.houseornot = houseornot
        self.carornot = carornot
        self.drinkornot = drinkornot
        self.specialty = specialty

    def __repr__(self):
        return '<nationality %r>' % self.nationality

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

        # print(_username, _password)

        _user = CipherTable.query.filter_by(username=_username).first()
        if _user is not None:
            if _user.password == _password:
                _token = jwtForApp.create_token(_username, _password)
                return {"code": 200, "message": "登录成功", "data": {"token": _token}}
            else:
                return {"code": 501, "message": "密码错误"}
        else:
            return {"code": 502, "message": "用户不存在"}


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


# 个人中心


# 在需要登陆权限的页面启用token验证-login_requried
@app.route('/main', methods=['get', 'post'])
@jwtForApp.login_required
def main():
    username = g.username
    return username


# 测试新建模型类与mysql的链接
@app.route('/testsql', methods=['get', 'post'])
def testsql():
    # display = DisplayInfo("柳非烟", "双鱼", "../..", "巴黎圣母院", "难忘今宵", "《肖申克的救赎》", "独白", "13533353335")
    _filter = FilterInfo("柳非烟", "女", "本科", "北京", "江苏", "10000", "未婚", "汉族", "城市规划", "无", "无", "无",
                         "唱歌")
    db.session.add(_filter)
    db.session.commit()
    print(_filter)
    return "ok"


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
