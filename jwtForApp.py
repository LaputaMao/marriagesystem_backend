from flask import g, request, Flask, current_app, jsonify
import jwt
from jwt import exceptions
import functools

# 构造header
headers = {
    'typ': 'jwt',
    'alg': 'HS256'
}

# 密钥
SALT = 'marriage_system'


def create_token(username, password):
    # 构造payload
    payload = {
        'username': username,
        'password': password,  # 自定义用户ID
        # 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # 超时时间
    }
    # python3中Python3的str 默认不是bytes，所以不能decode，只能先encode转为bytes，再decode
    # python2的str 默认是bytes，所以能decode
    result = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers)
    return result


def verify_jwt(token, secret=None):
    """
    检验jwt
    :param token: jwt
    :param secret: 密钥
    :return: dict: payload
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']

    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except exceptions.ExpiredSignatureError:  # 'token已失效'
        return 1
    except jwt.DecodeError:  # 'token认证失败'
        return 2
    except jwt.InvalidTokenError:  # '非法的token'
        return 3


def login_required(f):
    '让装饰器装饰的函数属性不会变 -- name属性'
    '使用functools模块的wraps装饰内部函数'

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if g.username == 1:
                return {'code': 6401, 'message': 'token已失效'}, 401
            elif g.username == 2:
                return {'code': 6401, 'message': 'token认证失败'}, 401
            elif g.username == 3:
                return {'code': 6401, 'message': '非法的token'}, 401
            else:
                return f(*args, **kwargs)
        except BaseException as e:
            # 通过e.args可以了解异常详情
            return {'code': 6402, 'message': e.args}, 401

    return wrapper


def jwt_authentication():
    """
    1.获取请求头Authorization中的token
    2.判断是否以 Bearer开头
    3.使用jwt模块进行校验
    4.判断校验结果,成功就提取token中的载荷信息,赋值给g对象保存
    """
    _token = request.headers.get('token')
    # if auth and auth.startswith('Bearer '):
    #     "提取token 0-6 被Bearer和空格占用 取下标7以后的所有字符"
    #     token = auth[7:]
    #     "校验token"
    g.username = None
    try:
        "判断token的校验结果"
        payload = jwt.decode(_token, SALT, algorithms=['HS256'])
        "获取载荷中的信息赋值给g对象"
        g.username = payload.get('username')
    except exceptions.ExpiredSignatureError:  # 'token已失效'
        g.username = 1
    except jwt.DecodeError:  # 'token认证失败'
        g.username = 2
    except jwt.InvalidTokenError:  # '非法的token'
        g.username = 3
