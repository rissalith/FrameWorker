"""
历史记录API路由
处理用户生成历史记录的CRUD操作
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_session, GenerationHistory, User
from routes.auth import require_auth

# 创建蓝图
history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('', methods=['POST'])
@require_auth
def create_history():
    """
    保存生成历史记录
    
    POST /api/history
    Headers: Authorization: Bearer <token>
    {
        "prompt": "魔法少女...",
        "model": "gemini-3-pro-image-preview",
        "frame_count": 16,
        "loop_consistency": true,
        "tolerance": 50,
        "sprite_url": "data:image/png;base64,...",
        "raw_image_url": "data:image/png;base64,...",
        "frames_data": "[...]",
        "rows": 4,
        "cols": 4
    }
    """
    try:
        user_id = g.current_user_id
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['prompt', 'model', 'frame_count']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': '参数错误',
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        db = get_db_session()
        try:
            # 创建历史记录
            history = GenerationHistory(
                user_id=user_id,
                prompt=data['prompt'],
                model=data['model'],
                frame_count=data['frame_count'],
                loop_consistency=data.get('loop_consistency', False),
                tolerance=data.get('tolerance', 50),
                sprite_url=data.get('sprite_url'),
                raw_image_url=data.get('raw_image_url'),
                frames_data=data.get('frames_data'),
                rows=data.get('rows'),
                cols=data.get('cols'),
                file_size=data.get('file_size'),
                generation_time=data.get('generation_time')
            )
            
            db.add(history)
            db.commit()
            db.refresh(history)
            
            return jsonify({
                'success': True,
                'record_id': history.id,
                'message': '记录已保存'
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'保存历史记录错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@history_bp.route('', methods=['GET'])
@require_auth
def get_history_list():
    """
    获取历史记录列表（分页）
    
    GET /api/history?page=1&limit=20
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = g.current_user_id
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # 限制每页数量
        if limit > 100:
            limit = 100
        
        db = get_db_session()
        try:
            # 查询总数
            total = db.query(GenerationHistory).filter(
                GenerationHistory.user_id == user_id
            ).count()
            
            # 分页查询
            offset = (page - 1) * limit
            records = db.query(GenerationHistory).filter(
                GenerationHistory.user_id == user_id
            ).order_by(
                GenerationHistory.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            # 转换为字典列表（不包含大数据字段）
            records_list = []
            for record in records:
                record_dict = {
                    'id': record.id,
                    'prompt': record.prompt,
                    'model': record.model,
                    'frame_count': record.frame_count,
                    'loop_consistency': record.loop_consistency,
                    'tolerance': record.tolerance,
                    'rows': record.rows,
                    'cols': record.cols,
                    'file_size': record.file_size,
                    'generation_time': record.generation_time,
                    'created_at': record.created_at.isoformat() if record.created_at else None,
                    # 缩略图URL（只返回前100个字符）
                    'thumbnail_url': record.sprite_url[:100] + '...' if record.sprite_url and len(record.sprite_url) > 100 else record.sprite_url
                }
                records_list.append(record_dict)
            
            return jsonify({
                'success': True,
                'records': records_list,
                'total': total,
                'page': page,
                'limit': limit,
                'pages': (total + limit - 1) // limit
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取历史记录列表错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@history_bp.route('/<int:record_id>', methods=['GET'])
@require_auth
def get_history_detail(record_id):
    """
    获取单条历史记录详情
    
    GET /api/history/:id
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = g.current_user_id
        
        db = get_db_session()
        try:
            record = db.query(GenerationHistory).filter(
                GenerationHistory.id == record_id,
                GenerationHistory.user_id == user_id
            ).first()
            
            if not record:
                return jsonify({
                    'success': False,
                    'error': '记录不存在',
                    'message': '未找到该记录或无权访问'
                }), 404
            
            return jsonify({
                'success': True,
                'record': record.to_dict()
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'获取历史记录详情错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@history_bp.route('/<int:record_id>', methods=['DELETE'])
@require_auth
def delete_history(record_id):
    """
    删除历史记录
    
    DELETE /api/history/:id
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = g.current_user_id
        
        db = get_db_session()
        try:
            record = db.query(GenerationHistory).filter(
                GenerationHistory.id == record_id,
                GenerationHistory.user_id == user_id
            ).first()
            
            if not record:
                return jsonify({
                    'success': False,
                    'error': '记录不存在',
                    'message': '未找到该记录或无权访问'
                }), 404
            
            db.delete(record)
            db.commit()
            
            return jsonify({
                'success': True,
                'message': '记录已删除'
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'删除历史记录错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


@history_bp.route('/migrate', methods=['POST'])
@require_auth
def migrate_local_history():
    """
    迁移本地历史记录到服务器
    
    POST /api/history/migrate
    Headers: Authorization: Bearer <token>
    {
        "records": [
            {
                "prompt": "...",
                "model": "...",
                ...
            }
        ]
    }
    """
    try:
        user_id = g.current_user_id
        data = request.get_json()
        
        records = data.get('records', [])
        if not isinstance(records, list):
            return jsonify({
                'success': False,
                'error': '参数错误',
                'message': 'records必须是数组'
            }), 400
        
        db = get_db_session()
        try:
            migrated_count = 0
            failed_count = 0
            
            for record_data in records:
                try:
                    # 验证必需字段
                    if not all(k in record_data for k in ['prompt', 'model', 'frame_count']):
                        failed_count += 1
                        continue
                    
                    # 创建历史记录
                    history = GenerationHistory(
                        user_id=user_id,
                        prompt=record_data['prompt'],
                        model=record_data['model'],
                        frame_count=record_data['frame_count'],
                        loop_consistency=record_data.get('loop_consistency', False),
                        tolerance=record_data.get('tolerance', 50),
                        sprite_url=record_data.get('sprite_url'),
                        raw_image_url=record_data.get('raw_image_url'),
                        frames_data=record_data.get('frames_data'),
                        rows=record_data.get('rows'),
                        cols=record_data.get('cols'),
                        file_size=record_data.get('file_size'),
                        generation_time=record_data.get('generation_time')
                    )
                    
                    db.add(history)
                    migrated_count += 1
                    
                except Exception as e:
                    print(f'迁移单条记录失败: {e}')
                    failed_count += 1
                    continue
            
            db.commit()
            
            return jsonify({
                'success': True,
                'migrated_count': migrated_count,
                'failed_count': failed_count,
                'message': f'成功迁移{migrated_count}条记录'
            })
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'迁移历史记录错误: {e}')
        return jsonify({
            'success': False,
            'error': '服务器错误',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print('历史记录路由模块')
    print('可用端点:')
    print('  POST   /api/history - 保存历史记录')
    print('  GET    /api/history - 获取历史记录列表')
    print('  GET    /api/history/:id - 获取单条记录详情')
    print('  DELETE /api/history/:id - 删除历史记录')
    print('  POST   /api/history/migrate - 迁移本地历史记录')