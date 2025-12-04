"""
游戏管理器 - 后端
负责游戏的注册、加载和API路由管理
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from flask import Blueprint, jsonify, request


class GameManager:
    """游戏管理器"""
    
    def __init__(self, game_library_path: str = 'GameLibrary'):
        self.game_library_path = Path(game_library_path)
        self.games_path = self.game_library_path / 'games'
        self.registry_path = self.game_library_path / 'game-registry.json'
        self.registry: Dict = {}
        self.games: Dict = {}
        self.game_blueprints: Dict = {}
        
    def init(self, app=None):
        """初始化游戏管理器"""
        try:
            # 确保目录存在
            self.games_path.mkdir(parents=True, exist_ok=True)
            
            # 加载游戏注册表
            self.load_registry()
            
            # 扫描并加载所有游戏
            self.scan_games()
            
            # 如果提供了app，注册游戏的后端API
            if app:
                self.register_game_apis(app)
            
            print(f'[GameManager] 初始化成功，已加载 {len(self.games)} 个游戏')
            return True
        except Exception as e:
            print(f'[GameManager] 初始化失败: {e}')
            return False
    
    def load_registry(self):
        """加载游戏注册表"""
        try:
            if self.registry_path.exists():
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
            else:
                # 创建默认注册表
                self.registry = {
                    'version': '1.0.0',
                    'lastUpdated': datetime.utcnow().isoformat() + 'Z',
                    'games': []
                }
                self.save_registry()
            
            print(f'[GameManager] 游戏注册表加载成功')
        except Exception as e:
            print(f'[GameManager] 加载游戏注册表失败: {e}')
            self.registry = {'version': '1.0.0', 'games': []}
    
    def save_registry(self):
        """保存游戏注册表"""
        try:
            self.registry['lastUpdated'] = datetime.utcnow().isoformat() + 'Z'
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
            print(f'[GameManager] 游戏注册表保存成功')
        except Exception as e:
            print(f'[GameManager] 保存游戏注册表失败: {e}')
    
    def scan_games(self):
        """扫描游戏目录"""
        if not self.games_path.exists():
            return
        
        for game_dir in self.games_path.iterdir():
            if game_dir.is_dir():
                game_config_path = game_dir / 'game.json'
                if game_config_path.exists():
                    try:
                        game_config = self.load_game_config(game_dir.name)
                        if game_config:
                            self.games[game_config['id']] = game_config
                            # 尝试加载游戏后端模块
                            self.load_game_backend(game_dir.name, game_config)
                            print(f'[GameManager] 发现游戏: {game_config["name"]} ({game_config["id"]})')
                    except Exception as e:
                        print(f'[GameManager] 加载游戏失败 {game_dir.name}: {e}')
    
    def load_game_config(self, game_id: str) -> Optional[Dict]:
        """加载游戏配置"""
        try:
            game_dir = self.games_path / game_id
            config_path = game_dir / 'game.json'
            
            if not config_path.exists():
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
        except Exception as e:
            print(f'[GameManager] 加载游戏配置失败 {game_id}: {e}')
            return None
    
    def load_game_backend(self, game_id: str, game_config: Dict):
        """加载游戏后端模块"""
        try:
            backend_path = self.games_path / game_id / 'backend'
            if not backend_path.exists():
                return
            
            # 检查是否有api.py文件
            api_file = backend_path / 'api.py'
            if not api_file.exists():
                return
            
            # 动态导入游戏后端模块
            spec = importlib.util.spec_from_file_location(
                f'game_{game_id}_backend',
                api_file
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                
                # 获取蓝图
                if hasattr(module, 'get_blueprint'):
                    blueprint = module.get_blueprint()
                    self.game_blueprints[game_id] = blueprint
                    print(f'[GameManager] 加载游戏后端: {game_id}')
                elif hasattr(module, 'fortune_bp'):
                    # 兼容旧的命名方式
                    self.game_blueprints[game_id] = module.fortune_bp
                    print(f'[GameManager] 加载游戏后端: {game_id}')
        except Exception as e:
            print(f'[GameManager] 加载游戏后端失败 {game_id}: {e}')
    
    def register_game_apis(self, app):
        """注册所有游戏的API到Flask应用"""
        for game_id, blueprint in self.game_blueprints.items():
            try:
                app.register_blueprint(blueprint)
                print(f'[GameManager] 注册游戏API: {game_id}')
            except Exception as e:
                print(f'[GameManager] 注册游戏API失败 {game_id}: {e}')
    
    def register_game(self, game_id: str) -> bool:
        """注册游戏到注册表"""
        try:
            game_config = self.games.get(game_id)
            if not game_config:
                print(f'[GameManager] 游戏不存在: {game_id}')
                return False
            
            # 检查是否已注册
            existing = next((g for g in self.registry['games'] if g['id'] == game_id), None)
            if existing:
                print(f'[GameManager] 游戏已注册: {game_id}')
                return True
            
            # 添加到注册表
            game_info = {
                'id': game_config['id'],
                'name': game_config['name'],
                'version': game_config['version'],
                'path': f'games/{game_id}',
                'enabled': True,
                'installedAt': datetime.utcnow().isoformat() + 'Z',
                'lastUpdated': datetime.utcnow().isoformat() + 'Z'
            }
            
            self.registry['games'].append(game_info)
            self.save_registry()
            
            print(f'[GameManager] 游戏注册成功: {game_config["name"]}')
            return True
        except Exception as e:
            print(f'[GameManager] 注册游戏失败 {game_id}: {e}')
            return False
    
    def unregister_game(self, game_id: str) -> bool:
        """从注册表移除游戏"""
        try:
            self.registry['games'] = [g for g in self.registry['games'] if g['id'] != game_id]
            self.save_registry()
            print(f'[GameManager] 游戏已移除: {game_id}')
            return True
        except Exception as e:
            print(f'[GameManager] 移除游戏失败 {game_id}: {e}')
            return False
    
    def enable_game(self, game_id: str) -> bool:
        """启用游戏"""
        try:
            game_info = next((g for g in self.registry['games'] if g['id'] == game_id), None)
            if game_info:
                game_info['enabled'] = True
                self.save_registry()
                print(f'[GameManager] 游戏已启用: {game_id}')
                return True
            return False
        except Exception as e:
            print(f'[GameManager] 启用游戏失败 {game_id}: {e}')
            return False
    
    def disable_game(self, game_id: str) -> bool:
        """禁用游戏"""
        try:
            game_info = next((g for g in self.registry['games'] if g['id'] == game_id), None)
            if game_info:
                game_info['enabled'] = False
                self.save_registry()
                print(f'[GameManager] 游戏已禁用: {game_id}')
                return True
            return False
        except Exception as e:
            print(f'[GameManager] 禁用游戏失败 {game_id}: {e}')
            return False
    
    def get_all_games(self) -> List[Dict]:
        """获取所有游戏"""
        return [
            {**game_info, **self.games.get(game_info['id'], {})}
            for game_info in self.registry['games']
            if game_info['enabled']
        ]
    
    def get_game(self, game_id: str) -> Optional[Dict]:
        """获取指定游戏"""
        game_info = next((g for g in self.registry['games'] if g['id'] == game_id), None)
        if game_info and game_info['enabled']:
            return {**game_info, **self.games.get(game_id, {})}
        return None
    
    def create_api_blueprint(self) -> Blueprint:
        """创建游戏管理API蓝图"""
        bp = Blueprint('game_manager', __name__, url_prefix='/api/games')
        
        @bp.route('', methods=['GET'])
        def get_games():
            """获取所有游戏列表"""
            try:
                games = self.get_all_games()
                return jsonify({
                    'success': True,
                    'games': games,
                    'count': len(games)
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
        
        @bp.route('/<game_id>', methods=['GET'])
        def get_game(game_id):
            """获取指定游戏信息"""
            try:
                game = self.get_game(game_id)
                if game:
                    return jsonify({
                        'success': True,
                        'game': game
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '游戏不存在或已禁用'
                    }), 404
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
        
        @bp.route('/<game_id>/enable', methods=['POST'])
        def enable_game_route(game_id):
            """启用游戏"""
            try:
                if self.enable_game(game_id):
                    return jsonify({
                        'success': True,
                        'message': f'游戏 {game_id} 已启用'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '游戏不存在'
                    }), 404
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
        
        @bp.route('/<game_id>/disable', methods=['POST'])
        def disable_game_route(game_id):
            """禁用游戏"""
            try:
                if self.disable_game(game_id):
                    return jsonify({
                        'success': True,
                        'message': f'游戏 {game_id} 已禁用'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '游戏不存在'
                    }), 404
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
        
        return bp


# 创建全局游戏管理器实例
game_manager = GameManager()