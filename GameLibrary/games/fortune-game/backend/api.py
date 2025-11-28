"""
巫女占卜游戏 - 后端API
提供占卜聊天、直播集成、AI Agent等完整功能
支持按需启动和用户级服务隔离
"""

from flask import Blueprint, jsonify, request
from flask_socketio import emit
from functools import wraps
import random
import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 添加GameLibrary到路径
game_library_path = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, game_library_path)

# 导入会话管理器
try:
    from game_session_manager import game_session_manager
    SESSION_MANAGER_AVAILABLE = True
    print('[Fortune-Game] 会话管理器已加载')
except ImportError as e:
    SESSION_MANAGER_AVAILABLE = False
    print(f'[Fortune-Game] 会话管理器不可用: {e}')

# 导入游戏服务类（不立即实例化）
try:
    from services.fortune_agent_llmx import FortuneAgentLLMX
    from services.live_service import LiveService
    from services.gift_mapping import GIFT_FORTUNE_MAPPING
    AI_AVAILABLE = True
    print('[Fortune-Game] AI Agent服务类已加载')
except ImportError as e:
    AI_AVAILABLE = False
    FortuneAgentLLMX = None
    LiveService = None
    print(f'[Fortune-Game] AI Agent服务类不可用: {e}')

try:
    from services.douyin.live_monitor import DouyinLiveMonitor
    LIVE_AVAILABLE = True
    print('[Fortune-Game] 直播服务类已加载')
except ImportError as e:
    LIVE_AVAILABLE = False
    DouyinLiveMonitor = None
    print(f'[Fortune-Game] 直播服务类不可用: {e}')

# 创建游戏蓝图
fortune_bp = Blueprint('fortune_game', __name__, url_prefix='/api/fortune')


def get_user_id_from_token():
    """从令牌中提取用户ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    
    # TODO: 实际应该解析JWT令牌获取用户ID
    # 这里简化处理，使用token作为user_id
    # 在生产环境中应该使用jwt.decode()
    return token[:32] if len(token) > 32 else token


def verify_token(f):
    """简单的令牌验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({
                'success': False,
                'message': '未提供认证令牌'
            }), 401
        # 这里应该验证JWT令牌，简化处理
        return f(*args, **kwargs)
    return decorated_function


def get_or_create_user_session(user_id: str):
    """获取或创建用户的游戏会话"""
    if not SESSION_MANAGER_AVAILABLE:
        return None
    
    try:
        session = game_session_manager.create_session(user_id, 'fortune-game')
        return session
    except Exception as e:
        print(f'[Fortune-Game] 创建会话失败: {e}')
        return None


def get_user_fortune_agent(user_id: str):
    """获取用户的AI Agent实例（按需创建）"""
    if not AI_AVAILABLE or not FortuneAgentLLMX:
        return None
    
    session = get_or_create_user_session(user_id)
    if not session:
        return None
    
    # 检查会话中是否已有AI Agent
    agent = session.get_service('fortune_agent')
    if agent:
        return agent
    
    # 创建新的AI Agent实例
    try:
        agent = FortuneAgentLLMX()
        session.set_service('fortune_agent', agent)
        print(f'[Fortune-Game] 为用户 {user_id} 创建AI Agent')
        return agent
    except Exception as e:
        print(f'[Fortune-Game] 创建AI Agent失败: {e}')
        return None


def get_user_live_service(user_id: str):
    """获取用户的直播服务实例（按需创建）"""
    if not LIVE_AVAILABLE or not LiveService:
        return None
    
    session = get_or_create_user_session(user_id)
    if not session:
        return None
    
    # 检查会话中是否已有直播服务
    service = session.get_service('live_service')
    if service:
        return service
    
    # 创建新的直播服务实例
    try:
        service = LiveService(socketio=None)  # socketio参数将在需要时传入
        session.set_service('live_service', service)
        print(f'[Fortune-Game] 为用户 {user_id} 创建直播服务')
        return service
    except Exception as e:
        print(f'[Fortune-Game] 创建直播服务失败: {e}')
        return None


@fortune_bp.route('/chat', methods=['POST', 'OPTIONS'])
@verify_token
def fortune_chat():
    """占卜Agent聊天接口 - 支持AI（按需启动）"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        username = data.get('username', '观众')
        grade = data.get('grade')
        topic = data.get('topic')
        
        if not user_input:
            return jsonify({
                'success': False,
                'message': '消息不能为空'
            }), 400
        
        # 获取用户ID
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '无效的用户令牌'
            }), 401
        
        # 如果AI可用，获取用户的AI Agent实例
        fortune_agent = None
        if AI_AVAILABLE:
            fortune_agent = get_user_fortune_agent(user_id)
        
        # 使用AI生成回复
        if fortune_agent:
            try:
                response_text = fortune_agent.chat(user_input=user_input)
            except Exception as e:
                print(f'AI回复失败，使用默认回复: {e}')
                response_text = f"感谢 {username} 的提问！{user_input}"
        else:
            # 使用默认回复
            responses = [
                f"感谢 {username} 的提问！根据你抽到的{grade}，{user_input}",
                f"巫女莉莉为 {username} 解读：{user_input}",
                f"命运的指引告诉我，{username}，{user_input}",
            ]
            response_text = random.choice(responses)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'username': username,
            'grade': grade,
            'topic': topic,
            'ai_enabled': fortune_agent is not None,
            'session_mode': 'on-demand' if SESSION_MANAGER_AVAILABLE else 'global'
        })
        
    except Exception as e:
        print(f"占卜Agent处理失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@fortune_bp.route('/live/start', methods=['POST', 'OPTIONS'])
@verify_token
def start_live():
    """开始监听直播间（按需启动）"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        live_id = data.get('live_id')
        
        if not live_id:
            return jsonify({
                'success': False,
                'message': '缺少直播间ID'
            }), 400
        
        # 获取用户ID
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '无效的用户令牌'
            }), 401
        
        # 如果直播服务可用，获取用户的直播服务实例
        if LIVE_AVAILABLE and DouyinLiveMonitor:
            try:
                live_service = get_user_live_service(user_id)
                if not live_service:
                    return jsonify({
                        'success': False,
                        'message': '无法创建直播服务'
                    }), 500
                
                # 使用LiveService的start_live方法
                result = live_service.start_live(live_id)
                
                if result.get('success'):
                    return jsonify({
                        'success': True,
                        'message': f'已连接到直播间 {live_id}',
                        'live_id': live_id,
                        'live_enabled': True,
                        'user_id': user_id,
                        'session_mode': 'on-demand' if SESSION_MANAGER_AVAILABLE else 'global'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': result.get('message', '启动直播监听失败')
                    }), 500
            except Exception as e:
                print(f'启动直播监听失败: {e}')
                return jsonify({
                    'success': False,
                    'message': f'启动失败: {str(e)}'
                }), 500
        else:
            # 直播服务不可用，返回模拟成功
            return jsonify({
                'success': True,
                'message': f'已连接到直播间 {live_id} (模拟模式)',
                'live_id': live_id,
                'live_enabled': False,
                'session_mode': 'simulation'
            })
            
    except Exception as e:
        print(f"启动直播间监听失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@fortune_bp.route('/live/stop', methods=['POST', 'OPTIONS'])
@verify_token
def stop_live():
    """停止监听直播间（清理用户会话）"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        live_id = data.get('live_id')
        
        if not live_id:
            return jsonify({
                'success': False,
                'message': '缺少直播间ID'
            }), 400
        
        # 获取用户ID
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '无效的用户令牌'
            }), 401
        
        # 如果直播服务可用，停止监听
        if LIVE_AVAILABLE:
            try:
                live_service = get_user_live_service(user_id)
                if live_service:
                    live_service.stop_live(live_id)
                
                # 清理用户的直播会话（可选：保留会话但清理直播服务）
                if SESSION_MANAGER_AVAILABLE and game_session_manager:
                    session = game_session_manager.get_user_session(user_id, 'fortune-game')
                    if session:
                        # 只清理直播相关服务，保留其他服务
                        session.set_service('live_service', None)
                        session.set_service('live_monitor', None)
                
                return jsonify({
                    'success': True,
                    'message': f'已断开直播间 {live_id}',
                    'live_id': live_id,
                    'user_id': user_id
                })
            except Exception as e:
                print(f'停止直播监听失败: {e}')
                return jsonify({
                    'success': False,
                    'message': f'停止失败: {str(e)}'
                }), 500
        else:
            return jsonify({
                'success': True,
                'message': f'已断开直播间 {live_id} (模拟模式)',
                'live_id': live_id
            })
            
    except Exception as e:
        print(f"停止直播间监听失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@fortune_bp.route('/live/status', methods=['GET'])
@verify_token
def get_live_status():
    """获取当前监听状态（用户级）"""
    try:
        # 获取用户ID
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '无效的用户令牌'
            }), 401
        
        if LIVE_AVAILABLE:
            live_service = get_user_live_service(user_id)
            if live_service:
                status = live_service.get_status()
                return jsonify({
                    'success': True,
                    'is_running': status.get('is_running', False),
                    'live_id': status.get('live_id'),
                    'connected_at': status.get('connected_at'),
                    'live_enabled': True,
                    'user_id': user_id,
                    'session_mode': 'on-demand' if SESSION_MANAGER_AVAILABLE else 'global'
                })
        
        return jsonify({
            'success': True,
            'is_running': False,
            'live_id': None,
            'connected_at': None,
            'live_enabled': False,
            'user_id': user_id
        })
    except Exception as e:
        print(f"获取状态失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@fortune_bp.route('/fortune/random', methods=['GET'])
@verify_token
def get_random_fortune():
    """获取随机占卜结果"""
    try:
        fortune_type = request.args.get('type', 'daily')
        
        # 签级和对应的权重
        levels = ['excellent', 'good', 'medium', 'bad', 'worst']
        weights = [5, 35, 40, 15, 5]
        
        # 根据权重随机选择签级
        level = random.choices(levels, weights=weights)[0]
        
        # 签级对应的中文名称
        level_names = {
            'excellent': '上上签',
            'good': '上签',
            'medium': '中签',
            'bad': '下签',
            'worst': '下下签'
        }
        
        return jsonify({
            'success': True,
            'type': fortune_type,
            'level': level,
            'levelText': level_names[level]
        })
    except Exception as e:
        print(f"获取随机占卜失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@fortune_bp.route('/gift/mapping', methods=['GET'])
def get_gift_mapping():
    """获取礼物到占卜类型的映射"""
    try:
        return jsonify({
            'success': True,
            'mapping': GIFT_FORTUNE_MAPPING if AI_AVAILABLE and 'GIFT_FORTUNE_MAPPING' in globals() else {}
        })
    except Exception as e:
        print(f"获取礼物映射失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@fortune_bp.route('/config', methods=['GET'])
def get_config():
    """获取游戏配置信息"""
    return jsonify({
        'success': True,
        'config': {
            'ai_enabled': AI_AVAILABLE,
            'live_enabled': LIVE_AVAILABLE,
            'features': {
                'chat': True,
                'live_stream': LIVE_AVAILABLE,
                'ai_agent': AI_AVAILABLE,
                'gift_mapping': True
            }
        }
    })


# 导出蓝图
def get_blueprint():
    """获取游戏蓝图"""
    return fortune_bp


# 会话清理端点
@fortune_bp.route('/session/close', methods=['POST', 'OPTIONS'])
@verify_token
def close_session():
    """关闭用户的游戏会话"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # 获取用户ID
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '无效的用户令牌'
            }), 401
        
        if SESSION_MANAGER_AVAILABLE and game_session_manager:
            game_session_manager.close_user_session(user_id, 'fortune-game')
            return jsonify({
                'success': True,
                'message': '会话已关闭',
                'user_id': user_id
            })
        else:
            return jsonify({
                'success': True,
                'message': '会话管理不可用'
            })
    except Exception as e:
        print(f"关闭会话失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@fortune_bp.route('/session/status', methods=['GET'])
@verify_token
def get_session_status():
    """获取用户的会话状态"""
    try:
        # 获取用户ID
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '无效的用户令牌'
            }), 401
        
        if SESSION_MANAGER_AVAILABLE and game_session_manager:
            session = game_session_manager.get_user_session(user_id, 'fortune-game')
            if session:
                return jsonify({
                    'success': True,
                    'has_session': True,
                    'session_id': session.session_id,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'services': list(session.services.keys()),
                    'user_id': user_id
                })
            else:
                return jsonify({
                    'success': True,
                    'has_session': False,
                    'user_id': user_id
                })
        else:
            return jsonify({
                'success': True,
                'session_manager_available': False
            })
    except Exception as e:
        print(f"获取会话状态失败: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


# SocketIO事件处理（如果需要）
def register_socketio_events(socketio):
    """注册SocketIO事件（支持用户级服务隔离）"""
    
    @socketio.on('fortune_chat')
    def handle_fortune_chat(data):
        """处理占卜Agent实时聊天"""
        try:
            user_input = data.get('message', '')
            username = data.get('username', '观众')
            grade = data.get('grade')
            topic = data.get('topic')
            user_id = data.get('user_id', 'anonymous')
            
            if not user_input:
                emit('fortune_response', {
                    'success': False,
                    'message': '消息不能为空'
                })
                return
            
            # 获取用户的AI Agent
            fortune_agent = None
            if AI_AVAILABLE:
                fortune_agent = get_user_fortune_agent(user_id)
            
            # 使用AI生成回复
            if fortune_agent:
                try:
                    response_text = fortune_agent.chat(user_input=user_input)
                except Exception as e:
                    response_text = f"感谢 {username} 的提问！{user_input}"
            else:
                response_text = f"感谢 {username} 的提问！{user_input}"
            
            emit('fortune_response', {
                'success': True,
                'response': response_text,
                'username': username,
                'session_mode': 'on-demand' if SESSION_MANAGER_AVAILABLE else 'global'
            })
            
        except Exception as e:
            print(f"占卜Agent实时聊天失败: {e}")
            emit('fortune_response', {
                'success': False,
                'message': f'处理失败: {str(e)}'
            })