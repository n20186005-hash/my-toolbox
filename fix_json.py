import json
import re

def clean_and_fix_json(file_path, output_path):
    """
    尝试读取并修复 JSON 文件中的常见语法错误，并输出格式化的 JSON 文件。
    """
    print(f"正在读取文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except FileNotFoundError:
        print("错误：文件未找到。请确认文件路径是否正确。")
        return
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return

    # --- 步骤 1: 预清理导致 JSON 库报错的常见非标准结构 ---
    # 移除文件末尾多余的逗号或结构（您的文件末尾有冗余的键和花括号）
    # 这里只是一个示范，实际复杂的重复键需要人工干预，但我们可以移除最后多余的逗号或结构
    
    # 尝试查找并移除文件末尾可能存在的 '},' ']}' 等冗余字符
    cleaned_content = raw_content.strip()
    
    # 检查并处理末尾多余的逗号或冗余键
    # 由于您的问题是键重复，我们使用正则表达式来尝试简化末尾的结构
    # 匹配并移除多余的 '}' 后面跟着 ',' 或 '}'，以及其后重复的键
    # 这是一个简化处理，如果结构复杂，可能需要更多定制规则。
    cleaned_content = re.sub(r'\},[\s\n]*"distance_calc": \{.*?\}', '}', cleaned_content, flags=re.DOTALL)
    cleaned_content = cleaned_content.strip()

    # 尝试移除最后一个有效键值对后面的逗号
    cleaned_content = re.sub(r',\s*\}', '}', cleaned_content)
    cleaned_content = re.sub(r',\s*\]', ']', cleaned_content)
    
    # --- 步骤 2: 使用 json 库解析和验证 ---
    try:
        # 使用 json.loads 尝试解析内容
        data = json.loads(cleaned_content)
        
        # --- 步骤 3: 检查并处理重复的键 (如果需要) ---
        # Python 的 json.loads 默认只会保留最后一个重复的键，
        # 如果需要更严格的检查，需要使用自定义的解析器。
        # 在这里我们信任 json.loads 的行为，它会保留有效的、唯一的结构。
        
        # --- 步骤 4: 输出修复并格式化后的 JSON ---
        # indent=2 使 JSON 结构清晰易读
        fixed_json = json.dumps(data, indent=2, ensure_ascii=False)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(fixed_json)
        
        print("\n--- 修复成功 ---")
        print(f"✅ 有效的 JSON 已保存到文件: {output_path}")
        print("您现在可以直接使用这个文件。")

    except json.JSONDecodeError as e:
        print("\n--- 修复失败 ---")
        print(f"❌ 无法自动修复所有 JSON 语法错误。错误信息:")
        print(f"位置 {e.lineno} 行, {e.colno} 列: {e.msg}")
        print("这通常意味着文件中有遗漏的双引号、多余的逗号或无效的字符。")
        
    except Exception as e:
        print(f"发生未知错误: {e}")

# --- 如何使用这个脚本 ---
# 1. 替换为您的文件路径
input_file = "seo-data.json" 
# 2. 设定修复后输出的文件名
output_file = "seo-data-fixed.json"

clean_and_fix_json(input_file, output_file)