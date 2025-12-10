import os
import shutil
import re
import json

# 配置路径
MODULES_DIR = 'modules'
TOOLS_JSON_FILE = 'tools.json'

# --- 核心修改：基于你提供的最新分类列表 ---
# 键(Key)是分类名称(我们会把它转成文件夹名)，值(Value)是文件名中可能包含的关键词
# 如果文件里没有 meta category 标签，脚本会尝试用这些词来归类
KEYWORD_CATEGORIES = {
    'color-tool': ['color', 'rgb', 'hex', 'palette', 'picker', 'contrast'],
    'crypto-tools': ['crypto', 'hash', 'bitcoin', 'eth', 'aes', 'md5', 'sha', 'encryption'],
    'date-time': ['date', 'time', 'clock', 'calendar', 'stopwatch', 'timer', 'zone', 'age'],
    'development-tools': ['code', 'json', 'xml', 'html', 'css', 'base64', 'dev', 'minify', 'formatter'],
    'e-commerce-operations': ['profit', 'margin', 'amazon', 'ebay', 'shopify', 'discount', 'sales'],
    'image-tools': ['image', 'photo', 'resize', 'crop', 'png', 'jpg', 'svg', 'compress', 'converter'],
    'math': ['calculator', 'math', 'algebra', 'geometry', 'stat', 'average', 'prime', 'factor'],
    'text-tools': ['text', 'word', 'count', 'lorem', 'string', 'case', 'editor', 'markdown'],
    'astrology': ['zodiac', 'horoscope', 'astro', 'sign', 'birth', 'star'],
    'auto': ['car', 'fuel', 'mpg', 'gas', 'vehicle', 'loan'],
    'chemistry': ['chem', 'periodic', 'molar', 'atom', 'molecule', 'ph'],
    'construction': ['concrete', 'brick', 'tile', 'paint', 'construction', 'roof'],
    'conversion': ['convert', 'unit', 'farenheit', 'celsius', 'weight', 'length', 'volume'],
    'education': ['grade', 'gpa', 'study', 'student', 'school'],
    'electronics': ['resistor', 'ohm', 'voltage', 'circuit', 'capactior'],
    'finance': ['401k', 'loan', 'mortgage', 'salary', 'tax', 'invest', 'currency', 'interest', 'retirement'],
    'fun': ['game', 'joke', 'meme', 'random', 'decision'],
    'gardening': ['garden', 'plant', 'seed', 'soil', 'water'],
    'health': ['bmi', 'calorie', 'fat', 'health', 'heart', 'pregnancy', 'bac', 'bmr', 'tdee', 'macro'],
    'life': ['life', 'habit', 'goal', 'wedding', 'event'],
    'pets': ['pet', 'dog', 'cat', 'food', 'animal'],
    'physics': ['physic', 'force', 'velocity', 'gravity', 'acceleration'],
    'security': ['password', 'generator', 'security', '2fa', 'totp'],
    'sports': ['sport', 'running', 'pace', 'score', 'team'],
    'statistics': ['probability', 'mean', 'median', 'mode', 'deviation'],
    'weather-health': ['weather', 'air', 'quality', 'aqi', 'humidity']
}

def to_kebab_case(name):
    """将文件名转换为 kebab-case (例如: AgeCalculator.html -> age-calculator.html)"""
    name_no_ext = os.path.splitext(name)[0]
    # 1. 在大写字母前加连字符
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name_no_ext)
    s1 = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1)
    # 2. 转小写，替换空格和下划线
    clean_name = s1.lower().replace(' ', '-').replace('_', '-')
    # 3. 避免连续的连字符 (例如 --)
    clean_name = re.sub(r'-+', '-', clean_name)
    return clean_name + '.html'

def clean_category_name(raw_cat):
    """
    规范化分类名称：
    'Date & Time' -> 'date-time'
    'E Commerce Operations' -> 'e-commerce-operations'
    """
    if not raw_cat:
        return 'others'
    
    # 转小写
    cat = raw_cat.lower().strip()
    # 替换 & 为 'and' 或者直接去除，这里选择直接去除符号保留单词
    cat = cat.replace('&', '')
    # 替换空格为连字符
    cat = cat.replace(' ', '-')
    # 去除多余连字符
    cat = re.sub(r'-+', '-', cat)
    return cat

def get_category_from_content(file_path, filename):
    """优先从文件 meta 标签读取，其次用关键词匹配"""
    
    # 1. 尝试从文件内容读取 meta category
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            match = re.search(r'<meta\s+name=["\']category["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
            if match:
                raw_cat = match.group(1).strip()
                if raw_cat:
                    # 即使 meta 标签里写的是 "Date & Time"，我们也把它转成 "date-time"
                    return clean_category_name(raw_cat)
    except Exception as e:
        print(f"Error reading {filename}: {e}")

    # 2. 如果没找到 tag，用文件名关键词匹配
    lower_name = filename.lower()
    for cat_folder, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            # 如果文件名包含关键词 (例如文件名含 401k，匹配到 finance)
            if kw in lower_name:
                return cat_folder
                
    return 'others'

def main():
    if not os.path.exists(MODULES_DIR):
        print(f"错误：找不到 {MODULES_DIR} 文件夹。请确保脚本在 my-toolbox 根目录！")
        return

    # 只处理根目录下的 .html 文件，不重复处理已经在子文件夹里的
    files = [f for f in os.listdir(MODULES_DIR) if f.endswith('.html') and os.path.isfile(os.path.join(MODULES_DIR, f))]
    
    print(f"找到 {len(files)} 个待处理文件...")
    
    tools_data = []

    for filename in files:
        original_path = os.path.join(MODULES_DIR, filename)
        
        # A. 确定分类 (文件夹名)
        category_folder = get_category_from_content(original_path, filename)
        
        # B. 确定新文件名
        new_filename = to_kebab_case(filename)
        
        # C. 创建目标文件夹
        target_dir = os.path.join(MODULES_DIR, category_folder)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        target_path = os.path.join(target_dir, new_filename)
        
        # D. 移动文件
        if os.path.exists(target_path) and target_path != original_path:
             print(f"警告：{category_folder}/{new_filename} 已存在，跳过。")
        else:
            shutil.move(original_path, target_path)
            print(f"Move: {filename} -> {category_folder}/{new_filename}")

        # E. 生成数据供 json 使用
        # 简单的 Title 处理：把连字符变成空格，首字母大写
        display_title = new_filename.replace('.html', '').replace('-', ' ').title()
        
        # 特殊处理：如果是 'bmi' 这种词，最好全大写，这里简单处理先用 Title Case
        tools_data.append({
            "id": new_filename.replace('.html', ''),
            "title": display_title,
            "category": category_folder, # 这里记录的是 normalized 的分类名 (e.g. date-time)
            "path": f"modules/{category_folder}/{new_filename}",
            "description": f"Free online {display_title} tool." 
        })

    # 写入 tools.json
    with open(TOOLS_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(tools_data, f, indent=2, ensure_ascii=False)

    print("-" * 30)
    print(f"处理完成！tools.json 已更新。")
    print(f"分类文件夹已采用 SEO 友好的 URL 格式 (如 date-time, e-commerce-operations)")

if __name__ == '__main__':
    main()