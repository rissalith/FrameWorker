"""
游戏管理API路由
处理游戏启动、授权验证等操作
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
import hashlib
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session, User, GameLicense, GameLaunch
from utils.jwt_helper import create_access_token, verify_access_token

# 创建蓝图
games_bp = Blueprint('games', __name__, url_prefix='/api/games')


# ==================== 辅助函数 ====================

def get_client_ip():
    """获取客户端IP地址"""
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0]
    return request.remote_addr or ''


def get_user_agent():
    """获取User-Agent"""
    return request.headers.get('User-Agent', '')


def require_auth(f):
    """认证装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '未授权',
                'message': '请提供认证令牌'
            }), 401
        
        # 移除 "Bearer " 前缀
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_access_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': '认证失败',
                'message': '令牌无效或已过期'
            }), 401
        
        # 将用户信息添加到请求上下文
        g.current_user_id = payload['user_id']
        g.current_user_phone = payload.get('phone', '')
        
        return f(*args, **kwargs)
    
    return decorated_function


def create_game_token(user_id, game_id, plan='free', expires_hours=12):
    """
    创建游戏专用Token
    
    Args:
        user_id: 用户ID
        game_id: 游戏ID
        plan: 用户计划 (free/pro/premium)
        expires_hours: 过期时间（小时）
    
    Returns:
        str: JWT Token
    """
    payload = {
        'user_id': user_id,
        'game_id': game_id,
        'plan': plan,
        'type': 'game_token',
        'exp': datetime.utcnow() + timedelta(hours=expires_hours)
    }
    
    # 使用JWT helper创建token，传入timedelta对象
    return create_access_token(user_id, game_id, timedelta(seconds=expires_hours * 3600))


def verify_game_token(token):
    """
    验证游戏Token
    
    Args:
        token: JWT Token
    
    Returns:
        dict: Token payload 或 None
    """
    payload = verify_access_token(token)
    
    if not payload:
        return None
    
    # 检查是否是游戏token
    if payload.get('type') != 'game_token':
        return None
    
    return payload


# ==================== API端点 ====================

@games_bp.route('', methods=['GET'])
def list_games():
    """
    获取公开的游戏列表
    
    GET /api/games
    """
    try:
        from database import Game
        
        db = get_db_session()
        try:
            # 只返回已发布的游戏
            games = db.query(Game).filter(Game.status == 'published').order_by(Game.sort_order).all()
            
            return jsonify({
                'success': True,
                'games': [g.to_dict() for g in games],
                'total': len(games)
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取游戏列表错误: {e}')
        return jsonify({
            'success': True,
            'games': [],
            'total': 0
        })


@games_bp.route('/<game_id>', methods=['GET'])
def get_game(game_id):
    """
    获取单个游戏详情
    
    GET /api/games/<game_id>
    """
    try:
        from database import Game
        
        db = get_db_session()
        try:
            game = db.query(Game).filter(Game.id == game_id).first()
            
            if not game:
                return jsonify({
                    'success': False,
                    'error': '游戏不存在'
                }), 404
            
            return jsonify({
                'success': True,
                'game': game.to_dict()
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取游戏详情错误: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@games_bp.route('/launch', methods=['POST'])
@require_auth
def launch_game():
    """
    启动游戏 - 生成游戏启动链接
    
    POST /api/games/launch
    Headers: Authorization: Bearer <user_token>
    {
        "game_id": "fortune-game"
    }
    """
    try:
        user_id = g.current_user_id
        data = request.get_json()
        game_id = data.get('game_id')
        
        if not game_id:
            return jsonify({
                'success': False,
                'error': '参数错误',
                'message': '缺少游戏ID'
            }), 400
        
        db = get_db_session()
        try:
            # 查询用户
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在',
                    'message': '用户信息未找到'
                }), 404
            
            # 查询或创建游戏授权
            license = db.query(GameLicense).filter(
                GameLicense.user_id == user_id,
                GameLicense.game_id == game_id
            ).first()
            
            if not license:
                # 自动创建免费授权
                license = GameLicense(
                    user_id=user_id,
                    game_id=game_id,
                    plan='free'
                )
                db.add(license)
                db.commit()
                db.refresh(license)
                print(f'[OK] 为用户 {user_id} 创建游戏授权: {game_id}')
            
            # 检查授权是否过期
            expires_at_value = license.expires_at
            if expires_at_value is not None and expires_at_value < datetime.utcnow():
                return jsonify({
                    'success': False,
                    'error': '授权已过期',
                    'message': '您的游戏授权已过期，请续费'
                }), 403
            
            # 生成游戏Token
            plan_value: str = license.plan  # type: ignore
            game_token = create_game_token(
                user_id=user_id,
                game_id=game_id,
                plan=plan_value,
                expires_hours=12
            )
            
            # 计算Token哈希
            token_hash = hashlib.sha256(game_token.encode()).hexdigest()
            
            # 记录启动日志
            launch_record = GameLaunch(
                user_id=user_id,
                game_id=game_id,
                token_hash=token_hash,
                ip_address=get_client_ip(),
                user_agent=get_user_agent()
            )
            db.add(launch_record)
            db.commit()
            
            # 生成游戏URL
            base_url = request.host_url.rstrip('/')
            launch_url = f"{base_url}/fortune-game/index.html?ticket={game_token}"
            
            print(f'[OK] 用户 {user_id} 启动游戏: {game_id}')
            
            return jsonify({
                'success': True,
                'launch_url': launch_url,
                'game_id': game_id,
                'plan': license.plan,
                'expires_in': 43200,  # 12小时
                'message': '游戏启动链接已生成'
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'启动游戏错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@games_bp.route('/verify', methods=['GET'])
def verify_ticket():
    """
    验证游戏Token
    
    GET /api/games/verify?ticket=<game_token>
    """
    try:
        ticket = request.args.get('ticket')
        
        if not ticket:
            return jsonify({
                'valid': False,
                'error': '缺少ticket参数'
            }), 400
        
        # 验证Token
        payload = verify_game_token(ticket)
        
        if not payload:
            return jsonify({
                'valid': False,
                'error': 'Token无效或已过期'
            }), 401
        
        db = get_db_session()
        try:
            # 查询用户信息
            user = db.query(User).filter(User.id == payload['user_id']).first()
            if not user:
                return jsonify({
                    'valid': False,
                    'error': '用户不存在'
                }), 404
            
            # 查询授权信息
            license = db.query(GameLicense).filter(
                GameLicense.user_id == payload['user_id'],
                GameLicense.game_id == payload['game_id']
            ).first()
            
            if not license:
                return jsonify({
                    'valid': False,
                    'error': '未找到游戏授权'
                }), 404
            
            # 检查授权是否过期
            expires_at_value = license.expires_at
            if expires_at_value is not None and expires_at_value < datetime.utcnow():
                return jsonify({
                    'valid': False,
                    'error': '授权已过期'
                }), 403
            
            return jsonify({
                'valid': True,
                'user_id': payload['user_id'],
                'game_id': payload['game_id'],
                'plan': license.plan,
                'nickname': user.nickname,
                'avatar_url': user.avatar_url,
                'expires_at': payload.get('exp')
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'验证Token错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500


@games_bp.route('/licenses', methods=['GET'])
@require_auth
def get_user_licenses():
    """
    获取用户的游戏授权列表
    
    GET /api/games/licenses
    Headers: Authorization: Bearer <user_token>
    """
    try:
        user_id = g.current_user_id
        
        db = get_db_session()
        try:
            licenses = db.query(GameLicense).filter(
                GameLicense.user_id == user_id
            ).all()
            
            return jsonify({
                'success': True,
                'licenses': [license.to_dict() for license in licenses]
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取授权列表错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@games_bp.route('/history', methods=['GET'])
@require_auth
def get_launch_history():
    """
    获取用户的游戏启动历史
    
    GET /api/games/history?limit=10
    Headers: Authorization: Bearer <user_token>
    """
    try:
        user_id = g.current_user_id
        limit = int(request.args.get('limit', 10))
        
        db = get_db_session()
        try:
            launches = db.query(GameLaunch).filter(
                GameLaunch.user_id == user_id
            ).order_by(GameLaunch.launched_at.desc()).limit(limit).all()
            
            return jsonify({
                'success': True,
                'history': [launch.to_dict() for launch in launches]
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取启动历史错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print('游戏管理路由模块')
    print('可用端点:')
    print('  POST /api/games/launch - 启动游戏')
    print('  GET  /api/games/verify - 验证游戏Token')
    print('  GET  /api/games/licenses - 获取授权列表')
    print('  GET  /api/games/history - 获取启动历史')