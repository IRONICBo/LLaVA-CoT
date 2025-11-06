#!/usr/bin/env python3
"""
简化版运行时补丁 - 解决相对导入问题
直接替换模块内容而不是动态加载
"""

import sys
import importlib
from pathlib import Path

def patch_mllama_processor_simple():
    """
    简化版补丁方法 - 直接修改已导入的模块
    """
    try:
        # 首先确保 transformers 已导入
        import transformers
        print(f"✅ transformers 版本: {transformers.__version__}")
        
        # 导入目标模块
        from transformers.models.mllama import processing_mllama as target_module
        print("✅ 成功导入目标模块")
        
        # 读取自定义处理器文件内容
        current_dir = Path(__file__).parent
        custom_file = current_dir / "processing_mllama.py"
        
        if not custom_file.exists():
            raise FileNotFoundError(f"找不到自定义处理器文件: {custom_file}")
        
        # 读取并修改自定义文件内容，替换相对导入
        with open(custom_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换相对导入为绝对导入
        content = content.replace(
            "from ...feature_extraction_utils import BatchFeature",
            "from transformers.feature_extraction_utils import BatchFeature"
        )
        content = content.replace(
            "from ...image_utils import ImageInput",
            "from transformers.image_utils import ImageInput"
        )
        content = content.replace(
            "from ...processing_utils import ImagesKwargs, ProcessingKwargs, ProcessorMixin, Unpack",
            "from transformers.processing_utils import ImagesKwargs, ProcessingKwargs, ProcessorMixin, Unpack"
        )
        content = content.replace(
            "from ...tokenization_utils_base import",
            "from transformers.tokenization_utils_base import"
        )
        content = content.replace(
            "from .image_processing_mllama import make_list_of_images",
            "from transformers.models.mllama.image_processing_mllama import make_list_of_images"
        )
        
        # 创建临时模块
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # 动态加载修改后的模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("custom_processing_mllama", tmp_file_path)
            custom_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom_module)
            
            print("✅ 成功加载自定义模块")
            
            # 备份原始属性
            backup = {}
            for attr_name in dir(target_module):
                if not attr_name.startswith('_'):
                    backup[attr_name] = getattr(target_module, attr_name)
            
            # 应用补丁
            patch_count = 0
            for attr_name in dir(custom_module):
                if not attr_name.startswith('_'):
                    setattr(target_module, attr_name, getattr(custom_module, attr_name))
                    patch_count += 1
            
            # 标记已补丁
            setattr(target_module, '_runtime_patched', True)
            setattr(target_module, '_backup', backup)
            
            print(f"✅ 成功应用补丁 ({patch_count} 个属性)")
            return True
            
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_file_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ 补丁应用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def restore_mllama_processor_simple():
    """恢复原始处理器"""
    try:
        from transformers.models.mllama import processing_mllama as target_module
        
        if not hasattr(target_module, '_runtime_patched'):
            print("⚠️  模块未被补丁过")
            return False
        
        if not hasattr(target_module, '_backup'):
            print("⚠️  没有备份数据")
            return False
        
        backup = getattr(target_module, '_backup')
        
        # 恢复所有属性
        for attr_name, original_value in backup.items():
            setattr(target_module, attr_name, original_value)
        
        # 清理标记
        delattr(target_module, '_runtime_patched')
        delattr(target_module, '_backup')
        
        print("✅ 成功恢复原始模块")
        return True
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False

def verify_patch_simple():
    """验证补丁状态"""
    try:
        from transformers.models.mllama import processing_mllama as target_module
        is_patched = hasattr(target_module, '_runtime_patched')
        print(f"📊 补丁状态: {'已应用' if is_patched else '未应用'}")
        return is_patched
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 测试简化版补丁...")
    
    # 应用补丁
    if patch_mllama_processor_simple():
        # 验证补丁
        verify_patch_simple()
        
        # 测试导入
        try:
            from transformers import AutoProcessor
            print("✅ 可以正常导入 AutoProcessor")
        except Exception as e:
            print(f"❌ 导入测试失败: {e}")
    
    print("✨ 测试完成")