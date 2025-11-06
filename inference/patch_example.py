#!/usr/bin/env python3
"""
使用上下文管理器的运行时补丁示例
提供更安全和便捷的补丁管理
"""

import sys
import os
from contextlib import contextmanager
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advanced_patch import TransformersRuntimePatcher

@contextmanager
def patched_mllama_processor(custom_file_path=None):
    """
    上下文管理器：自动应用和清理 MllamaProcessor 补丁
    
    使用示例:
        with patched_mllama_processor():
            # 在这里使用补丁后的处理器
            from transformers import AutoProcessor
            processor = AutoProcessor.from_pretrained("model_path")
            # ... 进行推理
        # 退出时自动恢复原始处理器
    
    Args:
        custom_file_path: 自定义处理器文件路径
    """
    patcher = TransformersRuntimePatcher()
    patch_applied = False
    
    try:
        # 应用补丁
        print("🔧 正在应用 MllamaProcessor 补丁...")
        patch_applied = patcher.patch_mllama_processor(custom_file_path)
        
        if patch_applied:
            print("✅ 补丁应用成功")
        else:
            print("❌ 补丁应用失败")
        
        yield patch_applied
        
    finally:
        # 自动清理补丁
        if patch_applied:
            print("🧹 正在清理补丁...")
            if patcher.restore_module("transformers.models.mllama.processing_mllama"):
                print("✅ 补丁清理成功")
            else:
                print("⚠️  补丁清理失败")

def example_inference_with_patch():
    """
    示例：使用补丁进行推理的完整流程
    """
    import torch
    from PIL import Image
    
    # 使用上下文管理器确保补丁的正确应用和清理
    with patched_mllama_processor() as patch_success:
        if not patch_success:
            print("❌ 无法应用补丁，退出")
            return
        
        # 现在可以安全地导入和使用 transformers
        from transformers import MllamaForConditionalGeneration, AutoProcessor
        
        print("🚀 正在加载模型...")
        model_name = "Xkev/Llama-3.2V-11B-cot"
        
        # 加载模型和处理器（使用补丁后的版本）
        model = MllamaForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map='cpu',
        ).cuda().eval()
        
        processor = AutoProcessor.from_pretrained(model_name)
        
        print("✅ 模型加载完成，使用自定义处理器")
        
        # 进行推理
        # image = Image.open("your_image.jpg")
        # prompt = "Your question here"
        # ... 推理代码
        
        print("🎯 推理完成")
    
    print("🏁 程序结束，补丁已自动清理")

def create_simple_patch_script():
    """
    创建一个简单的补丁应用脚本
    """
    script_content = '''#!/usr/bin/env python3
"""
简单的补丁应用脚本
在导入 transformers 之前运行此脚本
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from advanced_patch import patch_mllama_processor
    
    print("🔧 正在应用 MllamaProcessor 补丁...")
    
    # 应用补丁
    success = patch_mllama_processor()
    
    if success:
        print("✅ 补丁应用成功！")
        print("💡 现在可以正常导入和使用 transformers 库")
        print("📝 示例代码:")
        print("    from transformers import AutoProcessor")
        print("    processor = AutoProcessor.from_pretrained('model_name')")
    else:
        print("❌ 补丁应用失败")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ 导入补丁模块失败: {e}")
    print("💡 请确保 advanced_patch.py 和 processing_mllama.py 在当前目录")
    sys.exit(1)
except Exception as e:
    print(f"❌ 应用补丁时出错: {e}")
    sys.exit(1)
'''
    
    script_path = Path(__file__).parent / "apply_patch.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 创建补丁脚本: {script_path}")
    return script_path

if __name__ == "__main__":
    print("🎯 运行时补丁示例")
    print("=" * 50)
    
    # 创建简单的补丁脚本
    create_simple_patch_script()
    
    print("\n📖 使用方法:")
    print("1. 上下文管理器方式:")
    print("   with patched_mllama_processor():")
    print("       # 使用补丁后的处理器")
    print("       pass")
    
    print("\n2. 手动应用方式:")
    print("   from advanced_patch import patch_mllama_processor")
    print("   patch_mllama_processor()")
    
    print("\n3. 脚本方式:")
    print("   python apply_patch.py")
    print("   # 然后在同一个 Python 会话中使用 transformers")
    
    print("\n🔧 运行示例推理...")
    # example_inference_with_patch()  # 取消注释以运行示例