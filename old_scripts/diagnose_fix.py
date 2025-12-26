import json
import ast
import os

INPUT_FILE = 'seo-data.json'
OUTPUT_FILE = 'seo-data-fixed.json'

def try_fix_json():
    print(f"🔍 正在诊断文件: {INPUT_FILE} ...")
    
    if not os.path.exists(INPUT_FILE):
        print("❌ 找不到文件！")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- 尝试 1: 标准 JSON 解析 ---
    try:
        data = json.loads(content)
        print("✅ 文件竟然是完好的！无需修复。")
        save_json(data)
        return
    except json.JSONDecodeError as e:
        print(f"⚠️ 标准解析失败: {e}")
        print_error_context(content, e.pos)

    # --- 尝试 2: Python AST 解析 (容错率更高) ---
    # 很多时候 JSON 格式错误（如单引号、尾部逗号），Python 字典是可以识别的
    print("\n🛠️ 尝试使用 Python AST 暴力解析...")
    try:
        # 替换 JSON 的 true/false/null 为 Python 的 True/False/None
        py_content = content.replace('true', 'True').replace('false', 'False').replace('null', 'None')
        data = ast.literal_eval(py_content)
        print("✅ AST 解析成功！已自动修正语法错误。")
        save_json(data)
        return
    except Exception as e:
        print(f"❌ AST 解析也失败了: {e}")

    # --- 尝试 3: 暴力截断 (针对文件末尾乱码) ---
    print("\n🛠️ 尝试查找最后一个闭合的 ] 或 } ...")
    last_bracket = content.rfind(']')
    last_brace = content.rfind('}')
    cutoff = max(last_bracket, last_brace)
    
    if cutoff > 0:
        truncated_content = content[:cutoff+1]
        try:
            data = json.loads(truncated_content)
            print("✅ 截断修复成功！丢弃了末尾的垃圾数据。")
            save_json(data)
            return
        except:
            pass

    print("\n😭 所有自动修复手段都失败了。请查看上方的错误上下文手动修改。")

def print_error_context(content, pos, radius=50):
    """打印错误位置前后的字符，方便人工肉眼 debug"""
    start = max(0, pos - radius)
    end = min(len(content), pos + radius)
    snippet = content[start:end]
    
    print("\n--- 错误位置上下文 ---")
    print(f"...{snippet}...")
    print(" " * (3 + (pos - start)) + "⬆️ 这里错了")
    print("--------------------")

def save_json(data):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 已保存修复后的文件到: {OUTPUT_FILE}")

if __name__ == '__main__':
    try_fix_json()