import json
import os

# 目标文件
JSON_FILE = 'tools.json'

def clean_tags():
    print(f"🧹 正在读取 {JSON_FILE} ...")
    
    if not os.path.exists(JSON_FILE):
        print("❌ 找不到 tools.json 文件！")
        return

    # 读取数据
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    dirty_tags = set()

    # 遍历每一个工具
    for tool in data:
        # 获取当前的分类
        original_cat = tool.get('category', '').strip()
        
        # 转小写用于判断
        lower_cat = original_cat.lower()

        # 🎯 核心逻辑：只要看见 date 或 time，一律强行改名
        if 'date' in lower_cat or 'time' in lower_cat:
            # 如果它现在不是标准的 date-time，就改掉它
            if original_cat != 'date-time':
                tool['category'] = 'date-time'
                dirty_tags.add(original_cat)
                count += 1
        
        # 顺便把 math 这种也统一成小写 (可选)
        elif original_cat == 'Math':
             tool['category'] = 'math'
             count += 1

    # 如果有修改，就保存回去
    if count > 0:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 清洗完成！")
        print(f"共修正了 {count} 个工具的分类。")
        print(f"被清理掉的乱标签有: {dirty_tags}")
        print(f"现在的统一标签是: date-time")
    else:
        print("✅ 数据很干净，没有发现需要修复的标签。")

if __name__ == '__main__':
    clean_tags()