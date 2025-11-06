#!/usr/bin/env python3
"""
修复版本的运行时补丁工具
解决相对导入问题
"""

import sys
import os
import importlib
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any
import warnings

class TransformersRuntimePatcher:
    """
    Transformers 库运行时补丁器
    修复了相对导入问题
    """
    
    def __init__(self):
        self.applied_patches = {}
        self.backup_modules = {}
    
    def patch_module_from_file(self, 
                              module_path: str, 
                              custom_file_path: str,
                              backup: bool = True) -> bool:
        """
        从文件加载自定义模块并替换指定的模块
        """
        try:
            custom_file = Path(custom_file_path)
            if not custom_file.exists():
                raise FileNotFoundError(f"自定义模块文件不存在: {custom_file_path}")
            
            # 确保 transformers 已经导入，这样相对导入才能工作
            try:
                import transformers
                print(f"✅ transformers 版本: {transformers.__version__}")
            except ImportError:
                raise ImportError("请先安装 transformers 库")
            
            # 先导入目标模块，确保依赖关系正确
            try:
                target_module = importlib.import_module(module_path)
                print(f"✅ 成功导入目标模块: {module_path}")
            except ImportError as e:
                raise ImportError(f"无法导入目标模块 {module_path}: {e}")
            
            # 动态加载自定义模块
            spec = importlib.util.spec_from_file_location(
                f"custom_{module_path.replace('.', '_')}", 
                custom_file
            )
            
            if spec is None or spec.loader is None:
                raise ImportError(f"无法创建模块规范: {custom_file}")
            
            custom_module = importlib.util.module_from_spec(spec)
            
            # 在执行自定义模块之前，设置必要的上下文
            # 将目标模块的父包添加到 sys.modules 中
            parent_modules = module_path.split('.')[:-1]
            for i in range(len(parent_modules)):
                parent_path = '.'.join(parent_modules[:i+1])
                if parent_path not in sys.modules:
                    try:
                        sys.modules[parent_path] = importlib.import_module(parent_path)
                    except ImportError:
                        pass
            
            # 执行自定义模块
            try:
                spec.loader.exec_module(custom_module)
                print("✅ 成功加载自定义模块")
            except Exception as e:
                raise ImportError(f"执行自定义模块失败: {e}")
            
            if backup:
                # 备份原始模块
                self.backup_modules[module_path] = {}
                for attr_name in dir(target_module):
                    if not attr_name.startswith('_'):
                        self.backup_modules[module_path][attr_name] = getattr(target_module, attr_name)
            
            # 应用补丁
            patch_count = 0
            for attr_name in dir(custom_module):
                if not attr_name.startswith('_'):
                    setattr(target_module, attr_name, getattr(custom_module, attr_name))
                    patch_count += 1
            
            # 标记模块已被补丁
            setattr(target_module, '_runtime_patched', True)
            setattr(target_module, '_patch_source', custom_file_path)
            
            # 更新 sys.modules
            sys.modules[module_path] = target_module
            
            # 记录应用的补丁
            self.applied_patches[module_path] = {
                'source_file': custom_file_path,
                'patch_count': patch_count,
                'backup_available': backup
            }
            
            print(f"✅ 成功应用补丁: {module_path} ({patch_count} 个属性)")
            return True
            
        except Exception as e:
            print(f"❌ 应用补丁失败 {module_path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def patch_mllama_processor(self, custom_file_path: Optional[str] = None) -> bool:
        """
        专门用于补丁 MllamaProcessor 的便捷方法
        """
        if custom_file_path is None:
            # 自动查找 processing_mllama.py
            current_dir = Path(__file__).parent
            custom_file_path = current_dir / "processing_mllama.py"        
        return self.patch_module_from_file(
            "transformers.models.mllama.processing_mllama",
            str(custom_file_path)
        )
    
    def restore_module(self, module_path: str) -> bool:
        """恢复指定模块到原始状态"""
        try:
            if module_path not in self.applied_patches:
                print(f"⚠️  模块 {module_path} 未被补丁过")
                return False
            
            if not self.applied_patches[module_path]['backup_available']:
                print(f"⚠️  模块 {module_path} 没有备份，无法恢复")
                return False
            
            target_module = sys.modules[module_path]
            backup = self.backup_modules[module_path]
            
            # 恢复所有备份的属性
            for attr_name, original_value in backup.items():
                setattr(target_module, attr_name, original_value)
            
            # 清理补丁标记
            if hasattr(target_module, '_runtime_patched'):
                delattr(target_module, '_runtime_patched')
            if hasattr(target_module, '_patch_source'):
                delattr(target_module, '_patch_source')
            
            # 清理记录
            del self.applied_patches[module_path]
            del self.backup_modules[module_path]
            
            print(f"✅ 成功恢复模块: {module_path}")
            return True
            
        except Exception as e:
            print(f"❌ 恢复模块失败 {module_path}: {e}")
            return False
    
    def restore_all(self) -> bool:
        """恢复所有已应用的补丁"""
        success = True
        for module_path in list(self.applied_patches.keys()):
            if not self.restore_module(module_path):
                success = False
        return success
    
    def list_patches(self) -> Dict[str, Any]:
        """列出所有已应用的补丁"""
        return self.applied_patches.copy()
    
    def verify_patch(self, module_path: str) -> bool:
        """验证指定模块是否已被补丁"""
        try:
            if module_path in sys.modules:
                module = sys.modules[module_path]
                return hasattr(module, '_runtime_patched')
            return False
        except:
            return False

# 全局补丁器实例
_global_patcher = TransformersRuntimePatcher()

# 便捷函数
def patch_mllama_processor(custom_file_path: Optional[str] = None) -> bool:
    """便捷函数：补丁 MllamaProcessor"""
    return _global_patcher.patch_mllama_processor(custom_file_path)

def restore_mllama_processor() -> bool:
    """便捷函数：恢复 MllamaProcessor"""
    return _global_patcher.restore_module("transformers.models.mllama.processing_mllama")

def with_custom_processor(custom_file_path: Optional[str] = None):
    """装饰器：自动应用和清理处理器补丁"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 应用补丁
            patch_success = patch_mllama_processor(custom_file_path)
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                return result
            finally:
                # 可选：清理补丁
                if patch_success:
                    # restore_mllama_processor()  # 取消注释以自动恢复
                    pass
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # 测试补丁功能
    print("🔧 测试运行时补丁功能...")
    
    patcher = TransformersRuntimePatcher()
    
    # 应用补丁
    if patcher.patch_mllama_processor():
        # 验证补丁
        if patcher.verify_patch("transformers.models.mllama.processing_mllama"):
            print("✅ 补丁验证成功")
        
        # 列出补丁
        patches = patcher.list_patches()
        print(f"📋 已应用的补丁: {patches}")
        
        # 可选：恢复原始模块
        # patcher.restore_all()
    
    print("✨ 测试完成")