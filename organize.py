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

# --- 2. 扩充后的图标库 (包含更多前缀匹配) ---
BACKUP_ICONS = {
    'molar': '🧪', 'chem': '🧪', 'period': '📑', 'ph-cal': '💧',
    'volt': '⚡', 'ohm': 'Ω', 'resistor': '🔌', 'circuit': '🔌', 'battery': '🔋',
    'math': '➕', 'calc': '🧮', 'algebra': '✖️', 'geom': '📐', 'stat': '📊', 'prime': '🔢',
    'loan': '💸', 'mortgage': '🏠', 'salary': '💵', 'tax': '🧾', 'invest': '📈', 'bank': '🏦',
    'code': '👨‍💻', 'json': '📋', 'xml': '📜', 'html': '🌐', 'css': '🎨', 'hash': '#️⃣', 'encrypt': '🔒',
    'date': '📅', 'time': '⏰', 'clock': '🕰️', 'calendar': '🗓️', 'stopwatch': '⏱️', 'age': '🎂',
    'image': '🖼️', 'photo': '📷', 'watermark': '©️', 'png': '🎨', 'jpg': '📸',
    'text': '📄', 'word': '🔤', 'count': '🔢', 'case': 'Aa',
    'bmi': '⚖️', 'calorie': '🔥', 'fat': '🥓', 'preg': '🤰', 'health': '🏥',
    'car': '🚗', 'fuel': '⛽', 'engine': '⚙️', 'horse': '🐎',
    'grade': '💯', 'gpa': '🎓', 'exam': '📝', 'pass': '🔑', 'secure': '🛡️',
    'weather': '☁️', 'sun': '☀️', 'moon': '🌙', 'wind': '🌬️', 'search': '🔍'
}

WEAK_ICONS = ['🔧', '🌐', '🧮', '1️⃣', '❓', '📄', '📝', '✅', '🔍', '']

# --- 3. 辅助函数 ---

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
    for cat, kws in KEYWORD_CATEGORIES.items():
        for kw in kws:
            if kw in tid: return cat
    return 'others'

def main():
    print("\n🚀 启动全功能整理 & 图标强制补全系统...")

    # A. 预加载旧数据
    old_data_map = {}
    if os.path.exists(TOOLS_JSON_FILE):
        with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for item in data: old_data_map[item['id']] = item
            except: pass

    # B. 文件整理与广告
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
                if os.path.abspath(current_path) != os.path.abspath(target_path):
                    shutil.move(current_path, target_path)
                inject_ads_to_file(target_path)

    # C. 生成 JSON (改进的图标匹配逻辑)
    new_tools_data = []
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                tid = file[:-5]
                cat = os.path.basename(root)
                old_entry = old_data_map.get(tid)
                
                if old_entry:
                    entry = old_entry.copy()
                else:
                    entry = {"id": tid, "title": tid.replace('-', ' ').title(), "desc": f"Free online {tid} tool."}

                # --- 图标强制补全逻辑改进 ---
                current_icon = entry.get('icon', '')
                if current_icon in WEAK_ICONS:
                    matched_icon = None
                    # 按关键词长度倒序排列，优先匹配长词（更精准）
                    sorted_keys = sorted(BACKUP_ICONS.keys(), key=len, reverse=True)
                    for kw in sorted_keys:
                        if kw in tid.lower():
                            matched_icon = BACKUP_ICONS[kw]
                            break
                    
                    if matched_icon:
                        entry['icon'] = matched_icon
                        print(f"  [补全图标] {tid} -> {matched_icon}")
                    else:
                        entry['icon'] = '🔧' # 实在匹配不到再用扳手

                entry['file'] = f"modules/{cat}/{file}"
                entry['category'] = cat
                new_tools_data.append(entry)

    # D. 写入
    new_tools_data.sort(key=lambda x: (x.get('category', 'others'), x['id']))
    with open(TOOLS_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_tools_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 任务完成！处理了 {len(new_tools_data)} 个工具。")

if __name__ == '__main__':
    main()
