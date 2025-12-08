"""
商品管理API路由
处理商品查询、购买等操作
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
from sqlalchemy import desc, and_
import sys
import os
import uuid
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session, User, Wallet, Transaction, Product, License
from utils.jwt_helper import verify_access_token

# 创建蓝图
products_bp = Blueprint('products', __name__, url_prefix='/api/products')


# ==================== 辅助函数 ====================

def get_client_ip():
    """获取客户端IP地址"""
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0]
    return request.remote_addr or ''


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
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_access_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': '认证失败',
                'message': '令牌无效或已过期'
            }), 401
        
        g.current_user_id = payload['user_id']
        
        return f(*args, **kwargs)
    
    return decorated_function


def generate_order_id():
    """生成订单号"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:8].upper()
    return f'ORD{timestamp}{random_str}'


# ==================== API端点 ====================

@products_bp.route('', methods=['GET'])
def get_products():
    """
    获取商品列表
    
    GET /api/products?category=game&game_id=fortune-game&is_active=true
    """
    try:
        # 获取查询参数
        category = request.args.get('category')
        game_id = request.args.get('game_id')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        db = get_db_session()
        try:
            # 构建查询
            query = db.query(Product)
            
            if category:
                query = query.filter(Product.category == category)
            
            if game_id:
                query = query.filter(Product.game_id == game_id)
            
            if is_active:
                query = query.filter(Product.is_active == True)
            
            # 按排序字段排序
            products = query.order_by(Product.sort_order, Product.id).all()
            
            return jsonify({
                'success': True,
                'products': [p.to_dict() for p in products],
                'total': len(products)
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取商品列表错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    获取商品详情
    
    GET /api/products/<product_id>
    """
    try:
        db = get_db_session()
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                return jsonify({
                    'success': False,
                    'error': '商品不存在',
                    'message': '未找到该商品'
                }), 404
            
            return jsonify({
                'success': True,
                'product': product.to_dict()
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取商品详情错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@products_bp.route('/purchase', methods=['POST'])
@require_auth
def purchase_product():
    """
    购买商品
    
    POST /api/products/purchase
    Headers: Authorization: Bearer <token>
    Body: {
        "product_id": "fortune_30d"
    }
    """
    try:
        user_id = g.current_user_id
        data = request.get_json()
        
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({
                'success': False,
                'error': '参数错误',
                'message': '缺少商品ID'
            }), 400
        
        db = get_db_session()
        try:
            # 开始事务
            db.begin()

            # 查询商品
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.is_active == True
            ).first()

            # 如果商品不存在，尝试解析动态游戏套餐ID (格式: game_id_duration)
            # 例如: fortune-game-tiktok_30d, fortune-game_365d
            dynamic_product = None
            if not product and '_' in product_id:
                # 解析格式: {game_id}_{duration}
                parts = product_id.rsplit('_', 1)
                if len(parts) == 2:
                    game_id, duration_str = parts

                    # 定义支持的时长和价格倍率
                    duration_config = {
                        '30d': {'days': 30, 'multiplier': 1, 'name_zh': '1个月', 'name_en': '1 Month'},
                        '90d': {'days': 90, 'multiplier': 2.7, 'name_zh': '3个月', 'name_en': '3 Months'},
                        '365d': {'days': 365, 'multiplier': 8.4, 'name_zh': '12个月', 'name_en': '12 Months'},
                        'forever': {'days': None, 'multiplier': 20, 'name_zh': '永久', 'name_en': 'Lifetime'}
                    }

                    if duration_str in duration_config:
                        config = duration_config[duration_str]
                        base_price = 500  # 基础月租价格

                        # 检查是否是TikTok版（用于英文名称）
                        is_tiktok = 'tiktok' in game_id.lower()
                        game_name = 'Miko Fortune' if is_tiktok else '巫女上上签'
                        plan_name = config['name_en'] if is_tiktok else config['name_zh']

                        # 创建动态商品对象
                        dynamic_product = type('DynamicProduct', (), {
                            'id': product_id,
                            'name': f'{game_name} - {plan_name}',
                            'price': int(base_price * config['multiplier']),
                            'duration_days': config['days'],
                            'category': 'game',
                            'game_id': game_id
                        })()

            # 使用动态商品或返回错误
            if not product and not dynamic_product:
                return jsonify({
                    'success': False,
                    'error': '商品不存在',
                    'message': '商品不存在或已下架'
                }), 404

            # 优先使用数据库商品，否则用动态商品
            product = product or dynamic_product
            
            # 充值套餐不能通过此接口购买
            if product.category == 'recharge':
                return jsonify({
                    'success': False,
                    'error': '商品类型错误',
                    'message': '充值套餐请使用充值接口'
                }), 400
            
            # 锁定用户钱包
            wallet = db.query(Wallet).filter(
                Wallet.user_id == user_id
            ).with_for_update().first()
            
            if not wallet:
                return jsonify({
                    'success': False,
                    'error': '钱包不存在',
                    'message': '请先创建钱包'
                }), 404
            
            # 检查余额
            if wallet.balance < product.price:
                return jsonify({
                    'success': False,
                    'error': '余额不足',
                    'message': f'余额不足，需要 {product.price} 点，当前余额 {wallet.balance} 点'
                }), 400
            
            # 扣减余额
            balance_before = wallet.balance
            wallet.balance -= product.price
            wallet.total_consumed += product.price
            balance_after = wallet.balance
            
            # 同步用户表余额
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.balance = balance_after
            
            # 生成订单号
            order_id = generate_order_id()
            
            # 插入交易流水
            transaction = Transaction(
                user_id=user_id,
                amount=-product.price,
                type='PURCHASE',
                status='completed',
                product_id=product_id,
                product_name=product.name,
                order_id=order_id,
                balance_before=balance_before,
                balance_after=balance_after,
                description=f'购买 {product.name}',
                ip_address=get_client_ip(),
                completed_at=datetime.utcnow()
            )
            db.add(transaction)
            db.flush()  # 获取 transaction.id
            
            # 处理授权
            license_data = None
            
            if product.category == 'game':
                # 游戏授权
                license = db.query(License).filter(
                    License.user_id == user_id,
                    License.game_id == product.game_id
                ).first()
                
                if license:
                    # 续费：延长过期时间
                    license_type_val: str = license.license_type  # type: ignore
                    expires_at_val = license.expires_at
                    duration_days_val = product.duration_days
                    
                    if license_type_val == 'rental' and expires_at_val is not None:
                        # 如果已过期，从当前时间开始计算
                        if expires_at_val < datetime.utcnow():
                            license.expires_at = datetime.utcnow() + timedelta(days=duration_days_val)  # type: ignore
                        else:
                            # 未过期，在原有基础上延长
                            license.expires_at = expires_at_val + timedelta(days=duration_days_val)  # type: ignore
                    elif duration_days_val is None:
                        # 升级为永久版
                        license.license_type = 'permanent'  # type: ignore
                        license.expires_at = None  # type: ignore
                    
                    license.transaction_id = transaction.id  # type: ignore
                    license.status = 'active'  # type: ignore
                    license.updated_at = datetime.utcnow()  # type: ignore
                else:
                    # 新购买
                    license_type = 'permanent' if product.duration_days is None else 'rental'
                    expires_at = None if product.duration_days is None else datetime.utcnow() + timedelta(days=product.duration_days)
                    
                    license = License(
                        user_id=user_id,
                        game_id=product.game_id,
                        license_type=license_type,
                        plan='basic',
                        features='[]',
                        expires_at=expires_at,
                        transaction_id=transaction.id,
                        status='active'
                    )
                    db.add(license)
                
                db.flush()
                license_data = license.to_dict()
                
            elif product.category == 'feature':
                # 功能授权：更新现有授权的features
                license = db.query(License).filter(
                    License.user_id == user_id,
                    License.game_id == product.game_id
                ).first()
                
                if not license:
                    return jsonify({
                        'success': False,
                        'error': '未购买游戏',
                        'message': '请先购买游戏主体'
                    }), 400
                
                # 合并功能
                existing_features = json.loads(license.features) if license.features else []
                new_features = json.loads(product.features) if product.features else []
                
                for feature in new_features:
                    if feature not in existing_features:
                        existing_features.append(feature)
                
                license.features = json.dumps(existing_features)
                license.updated_at = datetime.utcnow()
                
                db.flush()
                license_data = license.to_dict()
            
            # 提交事务
            db.commit()
            
            print(f'[OK] 用户 {user_id} 购买商品: {product.name}, 花费: {product.price}点, 余额: {balance_after}')
            
            return jsonify({
                'success': True,
                'transaction_id': transaction.id,
                'order_id': order_id,
                'balance': balance_after,
                'license': license_data,
                'message': '购买成功'
            })
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    except Exception as e:
        print(f'购买商品错误: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@products_bp.route('/my-licenses', methods=['GET'])
@require_auth
def get_my_licenses():
    """
    获取我的授权列表
    
    GET /api/products/my-licenses?game_id=fortune-game
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = g.current_user_id
        game_id = request.args.get('game_id')
        
        print(f'[my-licenses] 请求用户 ID: {user_id}')
        
        db = get_db_session()
        try:
            query = db.query(License).filter(License.user_id == user_id)
            
            # 调试: 查看所有 licenses
            all_licenses = db.query(License).all()
            print(f'[my-licenses] 数据库中总共 {len(all_licenses)} 条授权')
            for lic in all_licenses:
                print(f'[my-licenses]   License ID={lic.id}, user_id={lic.user_id}, game_id={lic.game_id}')
            
            if game_id:
                query = query.filter(License.game_id == game_id)
            
            licenses = query.order_by(desc(License.created_at)).all()
            
            # 更新过期状态
            now = datetime.utcnow()
            for license in licenses:
                if license.expires_at and license.expires_at < now and license.status == 'active':
                    license.status = 'expired'
            
            db.commit()
            
            return jsonify({
                'success': True,
                'licenses': [lic.to_dict() for lic in licenses],
                'total': len(licenses)
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


@products_bp.route('/license/<int:license_id>/config', methods=['PUT'])
@require_auth
def update_license_config(license_id):
    """
    更新授权配置
    
    PUT /api/products/license/<id>/config
    Body: { config: { ... } }
    """
    try:
        user_id = g.current_user_id
        data = request.get_json()
        config = data.get('config', {})
        
        db = get_db_session()
        try:
            # 查找授权记录
            license = db.query(License).filter(
                License.id == license_id,
                License.user_id == user_id
            ).first()
            
            if not license:
                return jsonify({
                    'success': False,
                    'error': '授权不存在或无权限'
                }), 404
            
            # 更新配置
            license.config_json = json.dumps(config)
            license.updated_at = datetime.utcnow()
            
            db.commit()
            
            return jsonify({
                'success': True,
                'message': '配置已保存',
                'license': license.to_dict()
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'更新授权配置错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@products_bp.route('/license/<int:license_id>', methods=['DELETE'])
@require_auth
def delete_license(license_id):
    """
    删除授权（仅允许删除已过期的授权）

    DELETE /api/products/license/<id>
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = g.current_user_id

        db = get_db_session()
        try:
            # 查找授权记录
            license = db.query(License).filter(
                License.id == license_id,
                License.user_id == user_id
            ).first()

            if not license:
                return jsonify({
                    'success': False,
                    'error': '授权不存在',
                    'message': '未找到该授权或无权限删除'
                }), 404

            # 检查是否已过期
            now = datetime.utcnow()
            is_expired = license.expires_at and license.expires_at < now

            if not is_expired and license.status == 'active':
                return jsonify({
                    'success': False,
                    'error': '无法删除',
                    'message': '只能删除已过期的授权，有效授权无法删除'
                }), 400

            # 删除授权
            db.delete(license)
            db.commit()

            print(f'[OK] 用户 {user_id} 删除授权: license_id={license_id}')

            return jsonify({
                'success': True,
                'message': '授权已删除'
            })

        finally:
            db.close()

    except Exception as e:
        print(f'删除授权错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print('商品管理路由模块')
    print('可用端点:')
    print('  GET    /api/products - 获取商品列表')
    print('  GET    /api/products/<id> - 获取商品详情')
    print('  POST   /api/products/purchase - 购买商品')
    print('  GET    /api/products/my-licenses - 获取我的授权')
    print('  PUT    /api/products/license/<id>/config - 更新授权配置')
    print('  DELETE /api/products/license/<id> - 删除授权')