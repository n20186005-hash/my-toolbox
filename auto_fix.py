import json
import re

def fix_json_file():
    input_file = "seo-data.json"
    output_file = "seo-data-fixed.json"

    print(f"📖 正在读取 {input_file} ...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 找到最后一个有效的工具 "text_duplicate_remover" 的结束位置
        # 我们寻找这个工具的定义，并截取到它结束的地方
        target_key = '"text_duplicate_remover":'
        start_index = content.find(target_key)
        
        if start_index == -1:
            print("❌ 错误：未找到 'text_duplicate_remover'，请确认文件内容。")
            return

        # 找到这个 key 后面的结构
        # 简单粗暴但有效的方法：找到 text_duplicate_remover 下面的 steps, faqs 等内容
        # 我们可以利用它是倒数第二个块的特征，或者直接通过字符串截取来修复
        
        # 更安全的方法：
        # 既然我们知道 "distance_calc_backup_no_end_comma" 是错误的开始
        # 我们直接在这个错误 Key 出现之前截断文件
        
        error_key = '"distance_calc_backup_no_end_comma"'
        cutoff_index = content.find(error_key)
        
        if cutoff_index != -1:
            print(f" 发现并移除了损坏的备份数据块: {error_key}")
            # 截取到错误 key 之前的最后一个逗号之前
            valid_content = content[:cutoff_index]
            # 去掉末尾可能的空白和多余逗号
            valid_content = valid_content.rstrip().rstrip(',')
            # 补上整个 JSON 的结束大括号
            valid_content += "\n}"
        else:
            print("❓ 未找到明显的错误备份块，尝试常规解析...")
            valid_content = content

        # 2. 验证修复后的内容
        try:
            data = json.loads(valid_content)
            print(f"✅ JSON 结构验证成功！共包含 {len(data)} 个工具。")
            
            # 3. 写入新文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"🎉 修复完成！请使用新文件：{output_file}")
            
        except json.JSONDecodeError as e:
            print(f"❌ 自动修复尝试失败，语法仍然有误: {e}")
            # 如果截取失败，尝试最笨的方法：找到最后一个 }，然后往前找 text_duplicate_remover 的结束
            
    except FileNotFoundError:
        print(f"❌ 找不到文件 {input_file}，请确保脚本和 json 在同一目录下。")

if __name__ == "__main__":
    fix_json_file()