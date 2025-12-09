"""
注册游戏到数据库
将 GameLibrary 中的游戏注册到数据库的 games 表中
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from database import get_db_session, Game


def register_game_to_database(game_path, game_json_data, status='published'):
    """
    将单个游戏注册到数据库

    Args:
        game_path: 游戏目录路径 (相对于 GameLibrary)
        game_json_data: game.json 数据
        status: 游戏状态 ('draft', 'published', 'offline')
    """
    db = get_db_session()

    try:
        game_id = game_json_data.get('id')

        if not game_id:
            print(f'[WARNING] 游戏缺少ID: {game_path}')
            return False

        # 检查是否已存在
        existing_game = db.query(Game).filter(Game.id == game_id).first()

        if existing_game:
            print(f'[游戏已存在] {game_id} - 更新状态为 {status}')
            existing_game.status = status
            existing_game.name = game_json_data.get('name', existing_game.name)
            existing_game.name_display = game_json_data.get('name', existing_game.name)
            existing_game.description = game_json_data.get('description', existing_game.description)
            existing_game.version = game_json_data.get('version', existing_game.version)
            existing_game.updated_at = datetime.utcnow()

            db.commit()
            print(f'   更新完成!')

        else:
            print(f'[新建游戏] {game_id}')

            # 创建新游戏记录
            new_game = Game(
                id=game_id,
                name=game_json_data.get('name', game_id),
                name_display=game_json_data.get('name', game_id),
                description=game_json_data.get('description', ''),
                version=game_json_data.get('version', '1.0.0'),
                status=status,
                price=0,  # 暂时设为免费
                duration_days=365,  # 永久授权
                category=game_json_data.get('category', '互动游戏'),
                tags=json.dumps(game_json_data.get('tags', [])),
                sort_order=0,
                index_url=f'/{game_id}/index.html',  # 游戏入口
                icon_url=game_json_data.get('thumbnail', f'/{game_id}/icon.png'),
                engine='HTML5',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(new_game)
            db.commit()

            print(f'   游戏注册成功!')
            print(f'   名称: {new_game.name}')
            print(f'   状态: {new_game.status}')
            print(f'   入口: {new_game.index_url}')

        return True

    except Exception as e:
        print(f'[ERROR] 注册游戏失败: {e}')
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


def scan_and_register_games(game_library_path='../../GameLibrary'):
    """
    扫描 GameLibrary 目录并注册所有游戏到数据库

    Args:
        game_library_path: GameLibrary 目录路径
    """
    game_library = Path(__file__).parent.parent.parent / 'GameLibrary'

    if not game_library.exists():
        print(f'[ERROR] GameLibrary 目录不存在: {game_library}')
        return

    print('=== MaxGamer 游戏注册工具 ===\n')
    print(f'扫描目录: {game_library}\n')

    registered_count = 0
    failed_count = 0

    # 遍历所有平台目录
    for platform_dir in game_library.iterdir():
        if not platform_dir.is_dir() or platform_dir.name.startswith('.'):
            continue

        print(f'[平台] {platform_dir.name}')

        # 遍历平台下的所有游戏目录
        for game_dir in platform_dir.iterdir():
            if not game_dir.is_dir() or game_dir.name.startswith('.'):
                continue

            game_json_file = game_dir / 'game.json'

            if not game_json_file.exists():
                print(f'  [SKIP] {game_dir.name} - 缺少 game.json')
                continue

            try:
                # 读取 game.json
                with open(game_json_file, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)

                # 注册游戏
                game_path = f'{platform_dir.name}/{game_dir.name}'
                success = register_game_to_database(game_path, game_data, status='published')

                if success:
                    registered_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                print(f'  [ERROR] {game_dir.name} - 读取失败: {e}')
                failed_count += 1

        print()  # 空行分隔

    print(f'=== 注册完成 ===')
    print(f'成功: {registered_count} 个')
    print(f'失败: {failed_count} 个')
    print(f'总计: {registered_count + failed_count} 个')


if __name__ == '__main__':
    scan_and_register_games()
