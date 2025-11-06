#!/usr/bin/env python3
"""
运行时替换 transformers 库中的 processing_mllama.py 模块
使用 monkey patching 技术，无需修改原始文件
"""

import sys
import os
import importlib.util
from pathlib import Path

def patch_mllama_processor():
    """
    运行时替换 transformers.models.mllama.processing_mllama 模块
    """
    try:
        # 获取当前文件所在目录
        current_dir = Path(__file__).parent
        custom_processor_path = current_dir / "processing_mllama.py"
        
        if not custom_processor_path.exists():
            raise FileNotFoundError(f"自定义处理器文件不存在: {custom_processor_path}")
        
        # 动态加载自定义的 processing_mllama 模块
        spec = importlib.util.spec_from_file_location(
            "custom_processing_mllama", 
            custom_processor_path
        )
        custom_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_module)
        
        # 导入 transformers 并替换模块
        import transformers.models.mllama.processing_mllama as original_module
        
        # 保存原始模块的引用（如果需要恢复）
        original_module._original_backup = {}
        
        # 获取自定义模块中的所有公共属性
        custom_attrs = [attr for attr in dir(custom_module) 
                       if not attr.startswith('_')]
        
        # 替换原始模块中的属性
        for attr_name in custom_attrs:
            if hasattr(original_module, attr_name):
                # 备份原始属性
                original_module._original_backup[attr_name] = getattr(original_module, attr_name)
            
            # 设置新的属性
            setattr(original_module, attr_name, getattr(custom_module, attr_name))
        
        # 同时更新 sys.modules 中的引用
        sys.modules['transformers.models.mllama.processing_mllama'] = original_module
        
        print("✅ 成功替换 transformers.models.mllama.processing_mllama 模块")
        return True
        
    except Exception as e:
        print(f"❌ 替换模块失败: {e}")
        return False

def restore_original_processor():
    """
    恢复原始的 processing_mllama 模块
    """
    try:
        import transformers.models.mllama.processing_mllama as module
        
        if hasattr(module, '_original_backup'):
            # 恢复所有备份的属性
            for attr_name, original_value in module._original_backup.items():
                setattr(module, attr_name, original_value)
            
            # 清理备份
            delattr(module, '_original_backup')
            
            print("✅ 成功恢复原始 processing_mllama 模块")
            return True
        else:
            print("⚠️  没有找到备份，可能模块未被替换过")
            return False
            
    except Exception as e:
        print(f"❌ 恢复模块失败: {e}")
        return False

def verify_patch():
    """
    验证补丁是否成功应用
    """
    try:
        from transformers.models.mllama.processing_mllama import MllamaProcessor
        
        # 检查是否有我们的自定义标记
        if hasattr(MllamaProcessor, '_is_custom_patched'):
            print("✅ 自定义补丁已成功应用")
            return True
        else:
            print("⚠️  使用的是原始模块")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

# 自动应用补丁的装饰器
def with_custom_processor(func):
    """
    装饰器：自动应用和清理处理器补丁
    """
    def wrapper(*args, **kwargs):
        # 应用补丁
        patch_success = patch_mllama_processor()
        
        try:
            # 执行原函数
            result = func(*args, **kwargs)
            return result
        finally:
            # 清理补丁（可选）
            if patch_success:
                # restore_original_processor()  # 取消注释以自动恢复
                pass
    
    return wrapper

if __name__ == "__main__":
    # 测试补丁功能
    print("🔧 测试运行时补丁功能...")
    
    # 应用补丁
    if patch_mllama_processor():
        # 验证补丁
        verify_patch()
        
        # 可选：恢复原始模块
        # restore_original_processor()
    
    print("✨ 测试完成")