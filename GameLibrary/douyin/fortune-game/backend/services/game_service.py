#!/usr/bin/python
# coding:utf-8

"""
游戏管理服务层 - 处理游戏上传和管理相关业务逻辑
"""

import os
import json
import uuid
import zipfile
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from .. import db
from ..models.game import UploadedGame
from .game_validator import GameValidator


class GameService:
    """游戏管理服务"""
    
    def __init__(self, app_root_path):
        """
        初始化游戏服务
        
        Args:
            app_root_path: Flask应用根路径
        """
        self.app_root_path = app_root_path
        self.games_dir = os.path.join(app_root_path, 'static', 'games')
        if not os.path.exists(self.games_dir):
            os.makedirs(self.games_dir)
    
    def upload_game(self, game_file):
        """
        上传游戏文件（标准化ZIP包）
        
        Args:
            game_file: 游戏ZIP文件对象
            
        Returns:
            dict: 操作结果
        """
        temp_path = None
        game_dir = None
        
        try:
            # 验证游戏文件
            if not game_file or game_file.filename == '':
                return {'success': False, 'message': '未选择文件'}
            
            if not game_file.filename.lower().endswith('.zip'):
                return {'success': False, 'message': '只支持.zip格式的游戏包'}
            
            # 保存临时文件
            temp_path = os.path.join(self.games_dir, f'temp_{uuid.uuid4()}.zip')
            game_file.save(temp_path)
            
            # 使用验证器验证游戏包
            validator = GameValidator()
            is_valid, validation_result = validator.validate_zip(temp_path)
            
            if not is_valid:
                # 删除临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                # 返回验证错误
                error_messages = [f"{err['code']}: {err['message']}" for err in validation_result['errors']]
                return {
                    'success': False,
                    'message': '游戏包验证失败',
                    'errors': validation_result['errors'],
                    'warnings': validation_result['warnings']
                }
            
            # 生成唯一的游戏目录名
            game_id = str(uuid.uuid4())[:8]
            game_dir = os.path.join(self.games_dir, game_id)
            os.makedirs(game_dir)
            
            # 解压游戏包
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(game_dir)
            
            # 删除临时文件
            os.remove(temp_path)
            temp_path = None
            
            # 读取manifest.json
            manifest_path = os.path.join(game_dir, 'manifest.json')
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # 保存到数据库
            game = UploadedGame(
                name=manifest['name'],
                description=manifest.get('description', ''),
                icon=f'games/{game_id}/icon.png',
                game_type=manifest['type'],
                file_path=f'games/{game_id}',
                entry_file=manifest['entry'],
                sort_order=UploadedGame.query.count()
            )
            
            db.session.add(game)
            db.session.commit()
            
            return {
                'success': True,
                'message': '游戏上传成功',
                'data': {
                    'id': game.id,
                    'name': game.name,
                    'icon': f'/static/{game.icon}',
                    'type': game.game_type,
                    'version': manifest['version'],
                    'author': manifest.get('author', '未知')
                },
                'warnings': validation_result.get('warnings', [])
            }
            
        except Exception as e:
            # 清理临时文件和目录
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            if game_dir and os.path.exists(game_dir):
                shutil.rmtree(game_dir)
            
            db.session.rollback()
            print(f"【X】上传游戏失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'上传失败: {str(e)}'}
    
    @staticmethod
    def get_all_games(include_disabled=False):
        """
        获取所有游戏列表
        
        Args:
            include_disabled: 是否包含禁用的游戏
            
        Returns:
            dict: 包含游戏列表的结果
        """
        try:
            # 获取上传的游戏
            if include_disabled:
                uploaded_games = UploadedGame.query.order_by(UploadedGame.sort_order).all()
            else:
                uploaded_games = UploadedGame.query.filter_by(enabled=True).order_by(UploadedGame.sort_order).all()
            
            games_list = [{
                'id': game.id,
                'name': game.name,
                'description': game.description,
                'icon': f'/static/{game.icon}',
                'type': game.game_type,
                'enabled': game.enabled,
                'builtin': False,
                'path': f'/static/{game.file_path}',
                'entry': game.entry_file,
                'created_at': game.created_at.isoformat() if game.created_at else None,
                'updated_at': game.updated_at.isoformat() if game.updated_at else None
            } for game in uploaded_games]
            
            return {
                'success': True,
                'data': games_list
            }
        except Exception as e:
            print(f"【X】获取游戏列表失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_games_list():
        """
        获取所有游戏列表(简化版,用于子菜单显示)
        
        Returns:
            list: 游戏列表
        """
        try:
            games = UploadedGame.query.filter_by(enabled=True).order_by(UploadedGame.sort_order).all()
            return [{
                'id': game.id,
                'name': game.name,
                'icon': f'/static/{game.icon}',
                'type': game.game_type,
                'filePath': game.file_path,
                'entryFile': game.entry_file
            } for game in games]
        except Exception as e:
            print(f"【X】获取游戏列表失败: {e}")
            return []
    
    def delete_game(self, game_id):
        """
        删除游戏
        
        Args:
            game_id: 游戏ID
            
        Returns:
            dict: 操作结果
        """
        try:
            game = UploadedGame.query.get(game_id)
            if not game:
                return {'success': False, 'message': '游戏不存在'}
            
            # 删除游戏文件
            game_dir = os.path.join(self.app_root_path, 'static', game.file_path)
            if os.path.exists(game_dir):
                shutil.rmtree(game_dir)
            
            # 从数据库删除
            db.session.delete(game)
            db.session.commit()
            
            return {'success': True, 'message': '游戏删除成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_game_by_id(game_id):
        """
        根据ID获取游戏详情
        
        Args:
            game_id: 游戏ID
            
        Returns:
            dict: 游戏详情
        """
        try:
            game = UploadedGame.query.get(game_id)
            if not game:
                return {'success': False, 'message': '游戏不存在'}
            
            return {
                'success': True,
                'data': {
                    'id': game.id,
                    'name': game.name,
                    'description': game.description,
                    'icon': f'/static/{game.icon}',
                    'type': game.game_type,
                    'enabled': game.enabled,
                    'builtin': False,
                    'path': f'/static/{game.file_path}',
                    'entry': game.entry_file,
                    'created_at': game.created_at.isoformat() if game.created_at else None,
                    'updated_at': game.updated_at.isoformat() if game.updated_at else None
                }
            }
        except Exception as e:
            print(f"【X】获取游戏详情失败: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def update_game(game_id, name=None, description=None):
        """
        更新游戏信息
        
        Args:
            game_id: 游戏ID
            name: 新的游戏名称
            description: 新的游戏描述
            
        Returns:
            dict: 操作结果
        """
        try:
            game = UploadedGame.query.get(game_id)
            if not game:
                return {'success': False, 'message': '游戏不存在'}
            
            if name:
                game.name = name
            if description is not None:  # 允许设置为空字符串
                game.description = description
            
            game.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': '游戏更新成功',
                'data': {
                    'id': game.id,
                    'name': game.name,
                    'description': game.description
                }
            }
        except Exception as e:
            db.session.rollback()
            print(f"【X】更新游戏失败: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def toggle_game(game_id):
        """
        启用/禁用游戏
        
        Args:
            game_id: 游戏ID
            
        Returns:
            dict: 操作结果
        """
        try:
            game = UploadedGame.query.get(game_id)
            if not game:
                return {'success': False, 'message': '游戏不存在'}
            
            game.enabled = not game.enabled
            game.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': f'游戏已{"启用" if game.enabled else "禁用"}',
                'data': {
                    'id': game.id,
                    'enabled': game.enabled
                }
            }
        except Exception as e:
            db.session.rollback()
            print(f"【X】切换游戏状态失败: {e}")
            return {'success': False, 'message': str(e)}