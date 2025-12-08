#!/usr/bin/python
# coding:utf-8

"""
映射配置服务层 - 处理映射配置相关业务逻辑
"""

from datetime import datetime
from .. import db
from ..models.mapping import MappingConfig, ChatRule, GiftRule


class MappingService:
    """映射配置服务"""
    
    @staticmethod
    def get_all_config():
        """
        获取所有映射配置
        
        Returns:
            dict: 包含所有配置的字典
        """
        try:
            # 获取基础配置
            configs = {}
            for config_type in ['member', 'like', 'follow']:
                config = MappingConfig.query.filter_by(type=config_type).first()
                if config:
                    configs[config_type] = {
                        'enabled': config.enabled,
                        'action': config.action,
                        'key': config.key
                    }
                else:
                    configs[config_type] = {'enabled': False, 'action': '', 'key': ''}
            
            # 获取聊天规则
            chat_rules = ChatRule.query.order_by(ChatRule.sort_order).all()
            configs['chat'] = {
                'enabled': True,
                'rules': [{
                    'id': rule.id,
                    'pattern': rule.pattern,
                    'matchType': rule.match_type,
                    'action': rule.action,
                    'key': rule.key,
                    'enabled': rule.enabled
                } for rule in chat_rules]
            }
            
            # 获取礼物规则
            gift_rules = GiftRule.query.order_by(GiftRule.sort_order).all()
            configs['gift'] = {
                'enabled': True,
                'rules': [{
                    'id': rule.id,
                    'giftName': rule.gift_name,
                    'giftIcon': rule.gift_icon,
                    'minValue': rule.min_value,
                    'minCount': rule.min_count,
                    'action': rule.action,
                    'key': rule.key,
                    'enabled': rule.enabled
                } for rule in gift_rules]
            }
            
            return {'success': True, 'data': configs}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def save_basic_mapping(config_type, enabled, action, key):
        """
        保存基础映射配置（进场、点赞、关注）
        
        Args:
            config_type: 配置类型 (member/like/follow)
            enabled: 是否启用
            action: 游戏动作
            key: 按键
            
        Returns:
            dict: 操作结果
        """
        try:
            if config_type not in ['member', 'like', 'follow']:
                return {'success': False, 'message': '无效的配置类型'}
            
            # 查找或创建配置
            config = MappingConfig.query.filter_by(type=config_type).first()
            if not config:
                config = MappingConfig(type=config_type)
                db.session.add(config)
            
            config.enabled = enabled
            config.action = action
            config.key = key
            config.updated_at = datetime.utcnow()
            
            db.session.commit()
            return {'success': True, 'message': '保存成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def save_chat_rules(rules):
        """
        保存聊天规则
        
        Args:
            rules: 规则列表
            
        Returns:
            dict: 操作结果
        """
        try:
            # 删除所有现有规则
            ChatRule.query.delete()
            
            # 添加新规则
            for index, rule in enumerate(rules):
                new_rule = ChatRule(
                    pattern=rule.get('pattern', ''),
                    match_type=rule.get('matchType', 'exact'),
                    action=rule.get('action', ''),
                    key=rule.get('key', ''),
                    enabled=rule.get('enabled', True),
                    sort_order=index
                )
                db.session.add(new_rule)
            
            db.session.commit()
            return {'success': True, 'message': '聊天规则保存成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def save_gift_rules(rules):
        """
        保存礼物规则
        
        Args:
            rules: 规则列表
            
        Returns:
            dict: 操作结果
        """
        try:
            # 删除所有现有规则
            GiftRule.query.delete()
            
            # 添加新规则
            for index, rule in enumerate(rules):
                new_rule = GiftRule(
                    gift_name=rule.get('giftName', ''),
                    gift_icon=rule.get('giftIcon', ''),
                    min_value=rule.get('minValue', 0),
                    min_count=rule.get('minCount', 1),
                    action=rule.get('action', ''),
                    key=rule.get('key', ''),
                    enabled=rule.get('enabled', True),
                    sort_order=index
                )
                db.session.add(new_rule)
            
            db.session.commit()
            return {'success': True, 'message': '礼物规则保存成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def delete_rule(rule_id, rule_type):
        """
        删除规则
        
        Args:
            rule_id: 规则ID
            rule_type: 规则类型 (chat/gift)
            
        Returns:
            dict: 操作结果
        """
        try:
            if rule_type == 'chat':
                rule = ChatRule.query.get(rule_id)
            elif rule_type == 'gift':
                rule = GiftRule.query.get(rule_id)
            else:
                return {'success': False, 'message': '无效的规则类型'}
            
            if not rule:
                return {'success': False, 'message': '规则不存在'}
            
            db.session.delete(rule)
            db.session.commit()
            return {'success': True, 'message': '删除成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}