import os
import shutil
import re
import json

# 配置路径
MODULES_DIR = 'modules'
TOOLS_JSON_FILE = 'tools.json'

# --- 0. AdSense 广告代码 ---
ADSENSE_SCRIPT = r'''
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9279583389810634"
     crossorigin="anonymous"></script>
'''

# --- 1. 核心关键词分类配置 ---
KEYWORD_CATEGORIES = {
    'electronics': ['resistor', 'ohm', 'voltage', 'circuit', 'capacitor', 'drop', 'zener', 'current', 'electricity', 'induct', 'power-factor', 'dbm', 'frequency'],
    'physics': ['physic', 'force', 'velocity', 'gravity', 'acceleration', 'density', 'power', 'pressure', 'torque', 'energy', 'work', 'kinematic'],
    'chemistry': ['chem', 'periodic', 'molar', 'atom', 'molecule', 'ph-cal', 'reaction', 'stoichiometry', 'solution'],
    'math': ['calculator', 'math', 'algebra', 'geometry', 'stat', 'average', 'prime', 'factor', 'number', 'percent', 'fraction', 'shape', 'area', 'volume', 'surface', 'matrix', 'vector', 'logarithm', 'trigonometry', 'absolute-value', 'prism', 'cone', 'torus', 'frustum'],
    'finance': ['401k', 'loan', 'mortgage', 'salary', 'tax', 'invest', 'currency', 'interest', 'retirement', 'deposit', 'bank', 'budget', 'gdp', 'inflation', 'roi', 'cagr', 'profit', 'margin', 'vat', 'gst', 'tfsa'],
    'development-tools': ['code', 'json', 'xml', 'html', 'css', 'base64', 'dev', 'minify', 'formatter', 'hash', 'encrypt', 'language', 'regex', 'sql', 'dns', 'whois', 'cron', 'uuid', 'guid', 'ip-', 'subnet', 'diff', 'markdown', 'url-', 'ua-parser'],
    'date-time': ['date', 'time', 'clock', 'calendar', 'stopwatch', 'timer', 'zone', 'runyue', 'countdown', 'timestamp', 'daylight', 'duration', 'meeting', 'world', 'age-', 'day-of-year'], 
    'e-commerce-operations': ['amazon', 'ebay', 'shopify', 'discount', 'sales', 'shipping', 'asoch', 'fba', 'pricing', 'commission', 'inventory', 'pinduoduo'],
    'image-tools': ['image', 'photo', 'resize', 'crop', 'png', 'jpg', 'svg', 'compress', 'watermark', 'convert-to-image', 'favicon', 'ico'],
    'text-tools': ['text', 'word', 'count', 'lorem', 'string', 'case', 'editor', 'markdown', 'font', 'pinyin', 'ascii', 'slug', 'abstract-talk', 'capital-number'],
    'color-tool': ['color', 'rgb', 'hex', 'palette', 'picker', 'contrast', 'gradient'],
    'conversion': ['convert', 'unit', 'farenheit', 'celsius', 'weight', 'length', 'volume', 'temperature', 'speed', 'area-convert', 'pressure-convert'],
    'health': ['bmi', 'calorie', 'fat', 'health', 'heart', 'pregnancy', 'bac', 'bmr', 'tdee', 'macro', 'body', 'ovulation', 'period', 'sleep', 'water-intake', 'creatine', 'macronutrient'],
    'life': ['life', 'habit', 'goal', 'wedding', 'event', 'shengxiao', 'zodiac', 'chinese-zodiac'],
    'auto': ['car', 'fuel', 'mpg', 'gas', 'vehicle', 'plate', 'vin', 'tire', 'horsepower', 'engine'],
    'education': ['grade', 'gpa', 'study', 'student', 'school', 'exam', 'quiz'],
    'fun': ['game', 'joke', 'meme', 'random', 'decision', 'dice', 'love', 'solitaire', 'flames', 'compatibility', 'temple', 'hollow-knight'],
    'security': ['password', 'generator', 'security', '2fa', 'totp', 'md5', 'sha'],
    'construction': ['concrete', 'brick', 'tile', 'paint', 'roof', 'flooring', 'wallpaper', 'asphalt'],
    'weather-health': ['weather', 'air', 'quality', 'aqi', 'humidity', 'sun', 'moon']
}

SPECIFIC_FIXES = {
    'voltage-drop-calculator': 'electronics', 'voltage-calculator': 'electronics', 'ohm-law-calculator': 'electronics',
    'age-calculator': 'date-time', 'digital-clock-stopwatch': 'date-time', 'unix-timestamp-converter': 'date-time',
    'love-marriage-calculator': 'fun', 'mortgage-calculator-uk': 'finance', 'canadian-mortgage': 'finance'
}

BACKUP_ICONS = {
    'resistor': '🔌', 'ohm': 'Ω', 'voltage': '⚡', 'circuit': '🔌', 'capacitor': '🔋', 
    'math': '➕', 'algebra': '✖️', 'geometry': '📐', 'stat': '📊', 'prime': '🔢',
    'loan': '💸', 'mortgage': '🏠', 'salary': '💵', 'tax': '🧾', 'invest': '📈',
    'code': '👨‍💻', 'json': '📋', 'xml': '📜', 'html': '🌐', 'css': '🎨', 
    'date': '📅', 'time': '⏰', 'clock': '🕰️', 'calendar': '🗓️', 'stopwatch': '⏱️', 
    'image': '🖼️', 'photo': '📷', 'watermark': '©️', 'text': '📄', 'word': '🔤',
    'bmi': '⚖️', 'calorie': '🔥', 'fat': '🥓', 'pregnancy': '🤰', 'love': '❤️',
    'car': '🚗', 'fuel': '⛽', 'horsepower': '🐎', 'engine': '⚙️',
    'grade': '💯', 'gpa': '🎓', 'password': '🔑', 'weather': '☁️', 'search': '🔍'
}

WEAK_ICONS = ['🔧', '🌐', '🧮', '1️⃣', '❓', '📄', '📝', '✅', '🔍', '']

# --- 2. 逻辑函数 ---

def to_kebab_case(filename):
    name = filename.lower()
    if name.endswith('.html'): name = name[:-5]
    name = re.sub(r'[\s_.]+', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name + '.html'

def inject_ads_to_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'ca-pub-9279583389810634' in content: return False
        if '</head>' in content:
            new_content = content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except: pass
    return False

def get_category_by_name(filename):
    tid = filename.lower().replace('.html', '')
    if tid in SPECIFIC_FIXES: return SPECIFIC_FIXES[tid]
    for cat, kws in KEYWORD_CATEGORIES.items():
        for kw in kws:
            if kw in tid: return cat
    return 'others'

def main():
    print("\n" + "="*50)
    print("🚀 TOOLBOX 自动化整理 & 无损数据更新系统")
    print("="*50)

    # A. 预加载旧 JSON 数据
    old_data_map = {}
    if os.path.exists(TOOLS_JSON_FILE):
        with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for item in data: old_data_map[item['id']] = item
                print(f"📦 成功读取旧 JSON，发现 {len(old_data_map)} 个现有工具条目")
            except: 
                print("⚠️ 警告：tools.json 格式错误或为空，将创建新数据")

    # B. 文件整理与广告注入
    print("\n>>> 📂 正在整理物理文件并检查广告代码...")
    for root, dirs, files in os.walk(MODULES_DIR):
        if root == MODULES_DIR: continue 
        for filename in files:
            if filename.endswith('.html'):
                current_path = os.path.join(root, filename)
                new_filename = to_kebab_case(filename)
                target_cat = get_category_by_name(new_filename)
                target_dir = os.path.join(MODULES_DIR, target_cat)
                
                if not os.path.exists(target_dir): os.makedirs(target_dir)
                target_path = os.path.join(target_dir, new_filename)

                # 物理操作日志
                if os.path.abspath(current_path) != os.path.abspath(target_path):
                    shutil.move(current_path, target_path)
                    print(f"  [移动] {filename} -> {target_cat}/{new_filename}")
                
                # 广告注入日志
                if inject_ads_to_file(target_path):
                    print(f"  [广告] 已为 {new_filename} 补全 AdSense 代码")

    # C. 生成 JSON (无损合并)
    print("\n>>> 📑 正在执行无损数据合并...")
    new_tools_data = []
    
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                tid = file[:-5]
                cat = os.path.basename(root)
                
                # 获取旧数据
                old_entry = old_data_map.get(tid)
                
                if old_entry:
                    # 无损继承
                    entry = old_entry.copy()
                    # 只有图标太弱时才尝试更新
                    if entry.get('icon', '') in WEAK_ICONS:
                        for kw, icon in BACKUP_ICONS.items():
                            if kw in tid.lower():
                                entry['icon'] = icon
                                print(f"  [图标] 工具 '{tid}' 已由默认更新为 {icon}")
                                break
                    # 更新路径和分类（以磁盘当前状态为准）
                    entry['file'] = f"modules/{cat}/{file}"
                    entry['category'] = cat
                    field_count = len(entry.keys())
                    print(f"  [继承] 工具 '{tid}' 数据已保留，包含 {field_count} 个字段")
                else:
                    # 创建新工具
                    entry = {
                        "id": tid,
                        "title": tid.replace('-', ' ').title(),
                        "category": cat,
                        "file": f"modules/{cat}/{file}",
                        "desc": f"Free online {tid} tool.",
                        "icon": "🔧"
                    }
                    print(f"  [新增] 发现新文件 '{tid}'，已创建基础条目")
                
                new_tools_data.append(entry)

    # D. 写入结果
    new_tools_data.sort(key=lambda x: (x.get('category', 'others'), x['id']))
    with open(TOOLS_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_tools_data, f, indent=2, ensure_ascii=False)

    print("\n" + "="*50)
    print(f"✅ 任务完成！")
    print(f"📊 最终工具总数：{len(new_tools_data)}")
    print(f"📄 结果已保存至：{TOOLS_JSON_FILE}")
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
