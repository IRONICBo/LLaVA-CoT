#!/usr/bin/env python3
"""
修改后的 simple_inference.py - 使用运行时补丁替换处理器
"""

import torch
from PIL import Image
import re
import numpy as np
import copy
import argparse
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入运行时补丁模块
from runtime_patch import patch_mllama_processor, with_custom_processor

# 在导入 transformers 之前应用补丁
print("🔧 正在应用运行时补丁...")
patch_success = patch_mllama_processor()

if not patch_success:
    print("❌ 补丁应用失败，程序退出")
    sys.exit(1)

# 现在可以安全地导入 transformers
from transformers import StoppingCriteria, StoppingCriteriaList, MllamaForConditionalGeneration, AutoProcessor

parser = argparse.ArgumentParser(description="LLaVA-CoT Simple Inference with Runtime Patching")
parser.add_argument(
    "--model_name_or_path",
    type=str,
    default="Xkev/Llama-3.2V-11B-cot",
    help="Path to the model.",
)
parser.add_argument(
    "--prompt",
    type=str,
    help="Prompt to ask the model.",
)
parser.add_argument(
    "--image_path",
    type=str,
    help="Path to the image.",
)
parser.add_argument(
    "--type",
    type=str,
    default="stage",
    choices=["best_of_N", "sentence", "stage"],
    help="Type of generation to perform.",
)
parser.add_argument(
    "--beam_size",
    type=int,
    default=2,
    help="Number of candidates to generate.",
)
parser.add_argument(
    "--device",
    type=str,
    default="cuda",
    help="Device to use for inference.",
)
args = parser.parse_args()

class StopOnStrings(StoppingCriteria):
    def __init__(self, stop_strings, tokenizer):
        self.stop_strings = stop_strings
        self.tokenizer = tokenizer

    def __call__(self, input_ids, scores, **kwargs):
        generated_text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        for stop_string in self.stop_strings:
            if stop_string in generated_text:
                return True
        return False
    
class StopOnPeriod(StoppingCriteria):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, input_ids, scores, **kwargs):
        generated_text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        if generated_text.endswith('.'):
            return True
        return False

print("🚀 正在加载模型...")
model_name_or_path = args.model_name_or_path
model = MllamaForConditionalGeneration.from_pretrained(
        model_name_or_path,
        torch_dtype=torch.bfloat16,
        device_map='cpu',
    ).cuda().eval()
device = args.device
processor = AutoProcessor.from_pretrained(model_name_or_path)
kwargs = dict(do_sample=True, max_new_tokens=2048, temperature=0.6, top_p=0.9)

print("✅ 模型加载完成，使用自定义处理器")

# 这里可以继续添加原有的 judge 函数和生成函数
# 由于字符限制，我将在下一个文件中继续添加其余函数

def judge(image, prompt, outputs, type="summary"):
    # 这里是原有的 judge 函数实现
    # 为了节省空间，这里只显示函数签名
    # 完整实现请参考原始文件
    pass

def generate_inner_best_of_N(prompt, image_path, beam_size=2):
    # 原有的实现
    pass

def generate_inner_sentence_beam(prompt, image_path, beam_size=2):
    # 原有的实现
    pass

def generate_inner_stage_beam(prompt, image_path, beam_size=2):
    # 原有的实现
    pass

def generate_inner(prompt, image_path, type="stage", beam_size=2):
    if type == "best_of_N":
        return generate_inner_best_of_N(prompt, image_path, beam_size)
    elif type == "sentence":
        return generate_inner_sentence_beam(prompt, image_path, beam_size)
    elif type == "stage":
        return generate_inner_stage_beam(prompt, image_path, beam_size)
    else:
        raise ValueError("Invalid type. Choose from 'best_of_N', 'sentence', or 'stage'.")

if __name__ == "__main__":
    print("🎯 开始推理...")
    result = generate_inner(args.prompt, args.image_path, type=args.type, beam_size=args.beam_size)
    print("📝 推理结果:")
    print(result)