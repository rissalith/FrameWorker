"""
游戏验证器服务
用于验证上传的游戏包是否符合平台标准
"""
import os
import json
import zipfile
import re
from typing import Dict, List, Tuple
from PIL import Image
import io

class GameValidator:
    """游戏验证器"""
    
    # 错误代码
    ERROR_CODES = {
        'E001': '缺少manifest.json',
        'E002': 'manifest.json格式错误',
        'E003': '缺少必需字段',
        'E004': '缺少游戏图标',
        'E005': '图标尺寸不符合要求',
        'E006': '缺少入口文件',
        'E007': '文件大小超限',
        'E008': '包含不允许的文件类型',
        'E009': '代码包含危险函数',
        'E010': '未实现必需接口',
    }
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {
        '.html', '.htm', '.css', '.js', '.json',
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg',
        '.mp3', '.ogg', '.wav',
        '.txt', '.md'
    }
    
    # 禁止的文件扩展名
    FORBIDDEN_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib', '.bat', '.sh', '.cmd'
    }
    
    # 危险函数列表
    DANGEROUS_FUNCTIONS = [
        'eval(',
        'Function(',
        'setTimeout(',
        'setInterval(',
        'document.write(',
        'innerHTML =',
        'outerHTML =',
    ]
    
    # 必需的manifest字段
    REQUIRED_MANIFEST_FIELDS = ['name', 'version', 'entry', 'type']
    
    # 最大文件大小限制
    MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_zip(self, zip_path: str) -> Tuple[bool, Dict]:
        """
        验证ZIP文件
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            (是否通过, 验证结果)
        """
        self.errors = []
        self.warnings = []
        
        try:
            # 检查文件大小
            if not self._check_zip_size(zip_path):
                return False, self._get_result()
            
            # 打开ZIP文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 获取文件列表
                file_list = zip_ref.namelist()
                
                # 验证文件结构
                if not self._validate_structure(file_list):
                    return False, self._get_result()
                
                # 验证manifest.json
                manifest = self._validate_manifest(zip_ref)
                if not manifest:
                    return False, self._get_result()
                
                # 验证入口文件
                if not self._validate_entry(zip_ref, manifest.get('entry')):
                    return False, self._get_result()
                
                # 验证图标
                if not self._validate_icon(zip_ref):
                    return False, self._get_result()
                
                # 验证文件类型
                if not self._validate_file_types(file_list):
                    return False, self._get_result()
                
                # 验证文件大小
                if not self._validate_file_sizes(zip_ref):
                    return False, self._get_result()
                
                # 验证代码安全性
                if not self._validate_code_safety(zip_ref, file_list):
                    return False, self._get_result()
                
                # 验证游戏接口
                if not self._validate_game_interface(zip_ref, file_list):
                    return False, self._get_result()
            
            return True, self._get_result()
            
        except zipfile.BadZipFile:
            self._add_error('E002', 'ZIP文件损坏或格式错误')
            return False, self._get_result()
        except Exception as e:
            self._add_error('E002', f'验证过程出错: {str(e)}')
            return False, self._get_result()
    
    def _check_zip_size(self, zip_path: str) -> bool:
        """检查ZIP文件大小"""
        size = os.path.getsize(zip_path)
        if size > self.MAX_ZIP_SIZE:
            self._add_error('E007', f'ZIP文件大小超限 ({size / 1024 / 1024:.2f}MB > {self.MAX_ZIP_SIZE / 1024 / 1024}MB)')
            return False
        return True
    
    def _validate_structure(self, file_list: List[str]) -> bool:
        """验证文件结构"""
        # 检查是否包含manifest.json
        if 'manifest.json' not in file_list:
            self._add_error('E001', '缺少manifest.json')
            return False
        
        # icon.png 不再要求在ZIP包中，而是通过上传表单单独上传
        # 如果ZIP包中包含icon.png，给出警告
        if 'icon.png' in file_list:
            self._add_warning('ZIP包中包含icon.png，建议通过上传表单单独上传图标')
        
        return True
    
    def _validate_manifest(self, zip_ref: zipfile.ZipFile) -> Dict:
        """验证manifest.json"""
        try:
            manifest_data = zip_ref.read('manifest.json')
            manifest = json.loads(manifest_data.decode('utf-8'))
            
            # 检查必需字段
            missing_fields = []
            for field in self.REQUIRED_MANIFEST_FIELDS:
                if field not in manifest:
                    missing_fields.append(field)
            
            if missing_fields:
                self._add_error('E003', f'缺少必需字段: {", ".join(missing_fields)}')
                return None
            
            # 验证name长度
            if len(manifest['name']) < 1 or len(manifest['name']) > 50:
                self._add_error('E003', 'name字段长度必须在1-50字符之间')
                return None
            
            # 验证version格式
            if not re.match(r'^\d+\.\d+\.\d+$', manifest['version']):
                self._add_error('E003', 'version格式必须为x.y.z')
                return None
            
            # 验证type
            if manifest['type'] not in ['html5', 'webgl', 'canvas']:
                self._add_error('E003', 'type必须是html5、webgl或canvas')
                return None
            
            return manifest
            
        except json.JSONDecodeError:
            self._add_error('E002', 'manifest.json格式错误')
            return None
        except Exception as e:
            self._add_error('E002', f'读取manifest.json失败: {str(e)}')
            return None
    
    def _validate_entry(self, zip_ref: zipfile.ZipFile, entry: str) -> bool:
        """验证入口文件"""
        if not entry:
            self._add_error('E006', '未指定入口文件')
            return False
        
        if entry not in zip_ref.namelist():
            self._add_error('E006', f'入口文件不存在: {entry}')
            return False
        
        return True
    
    def _validate_icon(self, zip_ref: zipfile.ZipFile) -> bool:
        """验证图标（可选，因为图标通过表单单独上传）"""
        # 如果ZIP包中包含icon.png，进行验证
        if 'icon.png' in zip_ref.namelist():
            try:
                icon_data = zip_ref.read('icon.png')
                image = Image.open(io.BytesIO(icon_data))
                
                # 检查尺寸
                width, height = image.size
                if width != 512 or height != 512:
                    self._add_warning(f'ZIP包中的图标尺寸为{width}x{height}px，建议512x512px')
                
                # 检查格式
                if image.format != 'PNG':
                    self._add_warning('图标建议使用PNG格式')
                
            except Exception as e:
                self._add_warning(f'ZIP包中的图标验证失败: {str(e)}')
        
        # 图标验证总是返回True，因为图标通过表单单独上传
        return True
    
    def _validate_file_types(self, file_list: List[str]) -> bool:
        """验证文件类型"""
        for file_path in file_list:
            # 跳过目录
            if file_path.endswith('/'):
                continue
            
            ext = os.path.splitext(file_path)[1].lower()
            
            # 检查禁止的文件类型
            if ext in self.FORBIDDEN_EXTENSIONS:
                self._add_error('E008', f'包含不允许的文件类型: {file_path}')
                return False
            
            # 检查允许的文件类型
            if ext and ext not in self.ALLOWED_EXTENSIONS:
                self._add_warning(f'未知文件类型: {file_path}')
        
        return True
    
    def _validate_file_sizes(self, zip_ref: zipfile.ZipFile) -> bool:
        """验证文件大小"""
        for file_info in zip_ref.filelist:
            if file_info.file_size > self.MAX_FILE_SIZE:
                self._add_error('E007', f'文件大小超限: {file_info.filename} ({file_info.file_size / 1024 / 1024:.2f}MB)')
                return False
        return True
    
    def _validate_code_safety(self, zip_ref: zipfile.ZipFile, file_list: List[str]) -> bool:
        """验证代码安全性"""
        js_files = [f for f in file_list if f.endswith('.js')]
        
        for js_file in js_files:
            try:
                content = zip_ref.read(js_file).decode('utf-8')
                
                # 检查危险函数
                for dangerous_func in self.DANGEROUS_FUNCTIONS:
                    if dangerous_func in content:
                        self._add_error('E009', f'代码包含危险函数: {js_file} - {dangerous_func}')
                        return False
                
            except Exception as e:
                self._add_warning(f'无法读取JS文件: {js_file} - {str(e)}')
        
        return True
    
    def _validate_game_interface(self, zip_ref: zipfile.ZipFile, file_list: List[str]) -> bool:
        """验证游戏接口"""
        js_files = [f for f in file_list if f.endswith('.js')]
        
        # 查找游戏主类
        found_game_class = False
        found_init = False
        found_on_event = False
        found_destroy = False
        
        for js_file in js_files:
            try:
                content = zip_ref.read(js_file).decode('utf-8')
                
                # 检查是否包含Game类
                if 'class Game' in content or 'class game' in content:
                    found_game_class = True
                    
                    # 检查必需方法
                    if 'init(' in content or 'init (' in content:
                        found_init = True
                    if 'onEvent(' in content or 'onEvent (' in content:
                        found_on_event = True
                    if 'destroy(' in content or 'destroy (' in content:
                        found_destroy = True
                
            except Exception:
                continue
        
        if not found_game_class:
            self._add_error('E010', '未找到Game类')
            return False
        
        if not found_init:
            self._add_error('E010', '未实现init()方法')
            return False
        
        if not found_on_event:
            self._add_error('E010', '未实现onEvent()方法')
            return False
        
        if not found_destroy:
            self._add_error('E010', '未实现destroy()方法')
            return False
        
        return True
    
    def _add_error(self, code: str, message: str):
        """添加错误"""
        self.errors.append({
            'code': code,
            'message': message,
            'description': self.ERROR_CODES.get(code, '')
        })
    
    def _add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)
    
    def _get_result(self) -> Dict:
        """获取验证结果"""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }