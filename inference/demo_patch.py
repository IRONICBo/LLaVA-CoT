#!/usr/bin/env python3
"""
最简单的运行时补丁示例
使用修复后的补丁工具
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    print("🔧 LLaVA-CoT 运行时补丁示例")
    print("=" * 50)
    
    # 方法1: 使用简化版补丁
    print("\n📝 方法1: 简化版补丁")
    try:
        from simple_patch import patch_mllama_processor_simple, verify_patch_simple
        
        if patch_mllama_processor_simple():
            print("✅ 简化版补丁应用成功")
            verify_patch_simple()
            
            # 测试使用
            try:
                from transformers import AutoProcessor
                print("✅ 可以正常导入 AutoProcessor")
            except Exception as e:
                print(f"❌ 导入测试失败: {e}")
        else:
            print("❌ 简化版补丁应用失败")
            
    except Exception as e:
        print(f"❌ 简化版补丁出错: {e}")
    
    print("\n" + "=" * 50)
    
    # 方法2: 使用修复版补丁
    print("\n📝 方法2: 修复版补丁")
    try:
        from fixed_patch import patch_mllama_processor
        
        if patch_mllama_processor():
            print("✅ 修复版补丁应用成功")
            
            # 测试使用
            try:
                from transformers import AutoProcessor
                print("✅ 可以正常导入 AutoProcessor")
            except Exception as e:
                print(f"❌ 导入测试失败: {e}")
        else:
            print("❌ 修复版补丁应用失败")
            
    except Exception as e:
        print(f"❌ 修复版补丁出错: {e}")
    
    print("\n" + "=" * 50)
    print("💡 使用建议:")
    print("1. 优先使用简化版补丁 (simple_patch.py)")
    print("2. 如果简化版失败，尝试修复版补丁 (fixed_patch.py)")
    print("3. 在实际推理脚本中，在导入 transformers 之前应用补丁")
    
    print("\n📖 示例代码:")
    print("""
# 在你的推理脚本开头添加:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from simple_patch import patch_mllama_processor_simple

# 应用补丁
if patch_mllama_processor_simple():
    print("✅ 补丁应用成功")
    
    # 现在可以正常使用 transformers
    from transformers import AutoProcessor, MllamaForConditionalGeneration
    
    # 进行推理...
else:
    print("❌ 补丁应用失败")
    exit(1)
""")

if __name__ == "__main__":
    main()