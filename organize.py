import os
import shutil
import re
import json

# 配置路径
MODULES_DIR = 'modules'
TOOLS_JSON_FILE = 'tools.json'

# --- 1. 核心关键词分类配置 ---
KEYWORD_CATEGORIES = {
    'date-time': ['date', 'time', 'clock', 'calendar', 'stopwatch', 'timer', 'zone', 'age', 'runyue', 'countdown', 'timestamp'],
    'math': ['calculator', 'math', 'algebra', 'geometry', 'stat', 'average', 'prime', 'factor', 'number', 'percent', 'fraction'],
    'finance': ['401k', 'loan', 'mortgage', 'salary', 'tax', 'invest', 'currency', 'interest', 'retirement', 'deposit', 'bank'],
    'development-tools': ['code', 'json', 'xml', 'html', 'css', 'base64', 'dev', 'minify', 'formatter', 'hash', 'encrypt', 'language'],
    'e-commerce-operations': ['profit', 'margin', 'amazon', 'ebay', 'shopify', 'discount', 'sales', 'shipping'],
    'image-tools': ['image', 'photo', 'resize', 'crop', 'png', 'jpg', 'svg', 'compress', 'watermark'],
    'text-tools': ['text', 'word', 'count', 'lorem', 'string', 'case', 'editor', 'markdown', 'font', 'pinyin'],
    'color-tool': ['color', 'rgb', 'hex', 'palette', 'picker', 'contrast'],
    'health': ['bmi', 'calorie', 'fat', 'health', 'heart', 'pregnancy', 'bac', 'bmr', 'tdee', 'macro', 'body'],
    'life': ['life', 'habit', 'goal', 'wedding', 'event', 'shengxiao', 'zodiac'],
    'auto': ['car', 'fuel', 'mpg', 'gas', 'vehicle', 'loan', 'plate', 'vin'],
    'physics': ['physic', 'force', 'velocity', 'gravity', 'acceleration', 'density', 'power'],
    'chemistry': ['chem', 'periodic', 'molar', 'atom', 'molecule', 'ph'],
    'conversion': ['convert', 'unit', 'farenheit', 'celsius', 'weight', 'length', 'volume', 'temperature'],
    'education': ['grade', 'gpa', 'study', 'student', 'school', 'exam'],
    'electronics': ['resistor', 'ohm', 'voltage', 'circuit', 'capactior'],
    'fun': ['game', 'joke', 'meme', 'random', 'decision', 'dice', 'love'],
    'security': ['password', 'generator', 'security', '2fa', 'totp'],
    'construction': ['concrete', 'brick', 'tile', 'paint', 'roof'],
    'gardening': ['garden', 'plant', 'seed', 'soil', 'water'],
    'pets': ['pet', 'dog', 'cat', 'food', 'animal', 'fish'],
    'sports': ['sport', 'running', 'pace', 'score', 'team', 'golf'],
    'statistics': ['probability', 'mean', 'median', 'mode', 'deviation'],
    'weather-health': ['weather', 'air', 'quality', 'aqi', 'humidity', 'sun']
}

# --- 2. 强力纠错名单 (新增) ---
# 这里专门处理那些容易分错，或者 Meta 标签写错的文件
# 格式： '文件名ID': '正确的分类'
SPECIFIC_FIXES = {
    'mortgage-calculator-uk': 'finance',      # 之前错误: date-time
    'canadian-mortgage': 'finance',           # 之前错误: date-time
    'percentage-calculator': 'math',          # 之前错误: date-time
    'language-switcher': 'development-tools', # 之前错误: date-time
    'world-clock-meeting-planner': 'date-time' # 之前有空格问题
}

def to_kebab_case(name):
    """文件名转 kebab-case"""
    name_no_ext = os.path.splitext(name)[0]
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name_no_ext)
    s1 = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1)
    clean_name = s1.lower().replace(' ', '-').replace('_', '-')
    clean_name = re.sub(r'-+', '-', clean_name)
    return clean_name + '.html'

def get_category_from_content(file_path, filename):
    """获取分类逻辑"""
    tool_id = filename.replace('.html', '')
    
    # Priority 0: 检查是否在强力纠错名单里
    if tool_id in SPECIFIC_FIXES:
        print(f"🔧 触发强制纠错: {tool_id} -> {SPECIFIC_FIXES[tool_id]}")
        return SPECIFIC_FIXES[tool_id]

    # Priority 1: 尝试从 meta 标签读取
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            match = re.search(r'<meta\s+name=["\']category["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
            if match:
                raw_cat = match.group(1).lower().strip()
                # 强制清洗逻辑
                if 'date' in raw_cat and 'time' in raw_cat: return 'date-time'
                if 'math' in raw_cat: return 'math'
                
                raw_cat = raw_cat.replace('&', '').replace(' ', '-')
                return re.sub(r'-+', '-', raw_cat)
    except Exception:
        pass

    # Priority 2: 关键词匹配
    lower_name = filename.lower()
    for cat_folder, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            if kw in lower_name:
                return cat_folder
                
    return 'others'

def generate_tools_json():
    """生成 JSON"""
    print("正在扫描所有工具生成 JSON...")
    tools_data = []
    
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                tool_id = file.replace('.html', '')
                
                # 获取当前所在的实际文件夹名
                current_folder = os.path.basename(root)
                
                # 如果文件在根目录(未分类)，或者是我们已知的错误分类，我们需要纠正 category 字段
                # 注意：这里主要决定写入 JSON 的 category 值
                category = current_folder
                
                # 再次检查纠错名单，确保 JSON 里也是对的
                if tool_id in SPECIFIC_FIXES:
                    category = SPECIFIC_FIXES[tool_id]
                elif current_folder == MODULES_DIR: # 如果还在根目录
                    category = 'others'
                
                # 强制统一名称显示
                if category == 'Date & Time' or ('date' in category and 'time' in category):
                    category = 'date-time'
                if category == 'Math':
                    category = 'math'

                display_title = tool_id.replace('-', ' ').title()
                
                tools_data.append({
                    "id": tool_id,
                    "title": display_title,
                    "category": category,
                    "path": f"modules/{category}/{file}".replace('\\', '/'), # 注意路径要对应实际位置
                    "description": f"Free online {display_title} tool.",
                    "icon": "🔧"
                })
    
    tools_data.sort(key=lambda x: x['category'])
    return tools_data

def main():
    if not os.path.exists(MODULES_DIR):
        print(f"错误：找不到 {MODULES_DIR} 文件夹。")
        return

    # --- 第一步：移动整理文件 (包含对已分类文件的再次检查) ---
    # 我们遍历整个 modules 目录，看看有没有文件放错地方了
    print("开始检查并移动文件...")
    for root, dirs, files in os.walk(MODULES_DIR):
        for filename in files:
            if filename.endswith('.html'):
                original_path = os.path.join(root, filename)
                
                # 计算它应该在哪个分类
                correct_category = get_category_from_content(original_path, filename)
                new_filename = to_kebab_case(filename)
                
                # 目标路径
                target_dir = os.path.join(MODULES_DIR, correct_category)
                target_path = os.path.join(target_dir, new_filename)
                
                # 如果当前路径和目标路径不一样，说明放错地方了，移动它！
                # (排除掉路径完全相同的情况)
                if os.path.abspath(original_path) != os.path.abspath(target_path):
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    
                    try:
                        shutil.move(original_path, target_path)
                        print(f"📦 移动/纠正: {filename} -> {correct_category}/{new_filename}")
                    except Exception as e:
                        print(f"⚠️ 移动失败: {filename} - {e}")

    # --- 第二步：生成 tools.json ---
    final_data = generate_tools_json()

    with open(TOOLS_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print("-" * 30)
    print(f"✅ 处理完成！tools.json 已更新。")
    print(f"✅ 修正了 英国房贷、百分比计算器 等特定文件的分类。")
    print(f"✅ 时间分类强制统一为: date-time")

if __name__ == '__main__':
    main()
