# ==========================================
# 修复版 organize.py
# 同步了 manage_all.py 的最新逻辑与图标库
# ==========================================

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

# --- 2. 完整图标库 ---
BACKUP_ICONS = {
    # Electronics
    'resistor': '🔌', 'ohm': 'Ω', 'voltage': '⚡', 'circuit': '🔌', 'capacitor': '🔋', 
    'drop': '💧', 'zener': '⚡', 'current': '〰️', 'electricity': '💡', 'induct': '🌀',
    'dbm': '📶', 'frequency': '📻', 'pcb': '📟', 'solder': '🔥', 'battery': '🔋',
    # Physics
    'physic': '⚛️', 'force': '💪', 'velocity': '🏎️', 'gravity': '🍎', 'acceleration': '🚀', 
    'density': '🧱', 'power': '⚡', 'pressure': '🌡️', 'torque': '🔧', 'energy': '🔋',
    'kinematic': '🏃', 'thermodynamic': '🔥', 'optics': '🔦', 'quantum': '🌌',
    # Chemistry
    'chem': '🧪', 'periodic': '📑', 'molar': '⚖️', 'atom': '⚛️', 'molecule': '⚗️', 
    'ph': '💧', 'reaction': '💥', 'solution': '🥃', 'gas': '⛽', 'acid': '🍋',
    # Math
    'calculator': '🧮', 'math': '➕', 'algebra': '✖️', 'geometry': '📐', 'stat': '📊', 
    'average': '📉', 'prime': '🔢', 'factor': '➗', 'number': '1️⃣', 'percent': '％', 
    'fraction': '½', 'shape': '🔷', 'area': '🟥', 'volume': '🧊', 'surface': '🎨',
    'matrix': '▦', 'vector': '↗️', 'logarithm': '🪵', 'trigonometry': '📐', 'circle': '⭕',
    'triangle': '🔺', 'square': '🟥', 'cube': '🎲', 'root': '🌱', 'derivative': '∂', 'integral': '∫',
    # Finance
    '401k': '💰', 'loan': '💸', 'mortgage': '🏠', 'salary': '💵', 'tax': '🧾', 
    'invest': '📈', 'currency': '💱', 'interest': '℅', 'retirement': '🏖️', 'deposit': '🏦', 
    'bank': '🏛️', 'budget': '📝', 'gdp': '🌏', 'inflation': '🎈', 'roi': '💹',
    'cagr': '📈', 'profit': '💰', 'margin': '📊', 'vat': '🧾', 'gst': '🧾', 
    'stock': '📉', 'crypto': '₿', 'bitcoin': '₿', 'exchange': '💱', 'check': '✅',
    'payment': '💳', 'debt': '📉', 'compound': '📈', 'discount': '🏷️',
    # Development
    'code': '👨‍💻', 'json': '📋', 'xml': '📜', 'html': '🌐', 'css': '🎨', 
    'base64': '📦', 'dev': '🛠️', 'minify': '🤏', 'formatter': '✨', 'hash': '#️⃣', 
    'encrypt': '🔒', 'decrypt': '🔓', 'language': '🗣️', 'regex': '🔍', 'sql': '🗄️', 
    'dns': '🌍', 'whois': '❓', 'cron': '⏰', 'uuid': '🆔', 'guid': '🆔', 
    'ip': '📍', 'subnet': '🕸️', 'diff': '↔️', 'markdown': '⬇️', 'url': '🔗',
    'javascript': '☕', 'python': '🐍', 'java': '☕', 'git': '🌲', 'docker': '🐳',
    'linux': '🐧', 'terminal': '💻', 'api': '🔌', 'unicode': '🔣', 'ascii': '🔡',
    # Date & Time
    'date': '📅', 'time': '⏰', 'clock': '🕰️', 'calendar': '🗓️', 'stopwatch': '⏱️', 
    'timer': '⏲️', 'zone': '🌍', 'runyue': '🌒', 'countdown': '⏳', 'timestamp': '⌚', 
    'daylight': '☀️', 'duration': '⌛', 'meeting': '🤝', 'world': '🌏', 'age': '🎂',
    'birthday': '🍰', 'year': '📅', 'month': '📆', 'week': '🗓️', 'day': '☀️',
    # E-commerce
    'amazon': '📦', 'ebay': '🛍️', 'shopify': '👜', 'sales': '📈', 'shipping': '🚚', 
    'asoch': '🔍', 'fba': '📦', 'pricing': '🏷️', 'commission': '💰', 'inventory': '📦',
    # Image
    'image': '🖼️', 'photo': '📷', 'resize': '📏', 'crop': '✂️', 'png': '🎨', 
    'jpg': '📸', 'svg': '✒️', 'compress': '🗜️', 'watermark': '©️', 'convert-to-image': '🖼️',
    'favicon': '🔖', 'ico': '🔖', 'pixel': '👾', 'blur': '🌫️', 'filter': '🎨',
    # Text
    'text': '📄', 'word': '🔤', 'count': '🔢', 'lorem': '📝', 'string': '🧵', 
    'case': 'Aa', 'editor': '✍️', 'font': '🅰️', 'pinyin': '🇨🇳', 'slug': '🐌',
    'upper': '⬆️', 'lower': '⬇️', 'camel': '🐫', 'snake': '🐍', 'kebab': '🍢',
    # Color
    'color': '🎨', 'rgb': '🌈', 'hex': '#️⃣', 'palette': '🎨', 'picker': '🖌️', 
    'contrast': '🌗', 'gradient': '🌈', 'cmyk': '🖨️', 'hcl': '🎨',
    # Conversion
    'convert': '🔄', 'unit': '📏', 'farenheit': '🌡️', 'celsius': '🌡️', 'weight': '⚖️', 
    'length': '📏', 'speed': '🚀', 'area-convert': '🟥', 'pressure-convert': '🎈',
    'volume-convert': '🧊', 'mass': '⚖️', 'metric': '📏', 'imperial': '🦶',
    # Health
    'bmi': '⚖️', 'calorie': '🍎', 'fat': '🥓', 'health': '🏥', 'heart': '❤️', 
    'pregnancy': '🤰', 'bac': '🍺', 'bmr': '🔥', 'tdee': '🏃', 'macro': '🥗', 
    'body': '🧍', 'ovulation': '🥚', 'period': '🩸', 'sleep': '😴', 'water-intake': '💧',
    'bra-size': '👙', 'shoe-size': '👟', 'ideal-weight': '⚖️', 'protein': '🥩', 'carb': '🍞',
    # Life
    'life': '🌱', 'habit': '✅', 'goal': '🎯', 'wedding': '💍', 'event': '🎉', 
    'shengxiao': '🐉', 'zodiac': '♈', 'chinese-zodiac': '🐉', 'decision': '⚖️',
    # Auto
    'car': '🚗', 'fuel': '⛽', 'mpg': '⛽', 'gas': '⛽', 'vehicle': '🚙', 
    'plate': '🆔', 'vin': '🔍', 'tire': '🍩', 'horsepower': '🐎', 'engine': '⚙️',
    # Education
    'grade': '💯', 'gpa': '🎓', 'study': '📚', 'student': '🎒', 'school': '🏫', 
    'exam': '📝', 'quiz': '❓', 'college': '🏛️', 'university': '🎓', 'course': '📘',
    # Fun
    'game': '🎮', 'joke': '🤡', 'meme': '😂', 'random': '🎲', 'dice': '🎲', 
    'love': '❤️', 'solitaire': '🃏', 'flames': '🔥', 'compatibility': '💑', 'puzzle': '🧩',
    'sudoku': '🔢', 'chess': '♟️',
    # Security
    'password': '🔑', 'generator': '⚙️', 'security': '🛡️', '2fa': '📱', 'totp': '🔐', 
    'md5': '#️⃣', 'sha': '#️⃣', 'safe': '🔐', 'lock': '🔒', 'key': '🗝️',
    # Construction
    'concrete': '🏗️', 'brick': '🧱', 'tile': '🔲', 'paint': '🖌️', 'roof': '🏠', 
    'flooring': '🪵', 'wallpaper': '🖼️', 'gravel': '🪨', 'sand': '⏳',
    # Gardening
    'garden': '🏡', 'plant': '🌿', 'seed': '🌰', 'soil': '🟤', 'water': '🚿', 
    'fertilizer': '💩', 'mulch': '🍂', 'flower': '🌸', 'tree': '🌳',
    # Pets
    'pet': '🐾', 'dog': '🐶', 'cat': '🐱', 'food': '🍖', 'animal': '🦁', 
    'fish': '🐟', 'aquarium': '🐠', 'bird': '🐦', 'hamster': '🐹',
    # Sports
    'sport': '⚽', 'running': '🏃', 'pace': '⏱️', 'score': '🏆', 'team': '👕', 
    'golf': '⛳', 'cricket': '🏏', 'football': '🏈', 'basketball': '🏀', 'tennis': '🎾',
    # Statistics
    'probability': '🎲', 'mean': 'µ', 'median': '📊', 'mode': '📊', 'deviation': 'σ', 
    'sample': '📉', 'permutation': '🔄', 'combination': '🎲', 'z-score': '📊',
    # Weather
    'weather': '☁️', 'air': '💨', 'quality': '😷', 'aqi': '🌫️', 'humidity': '💧', 
    'sun': '☀️', 'moon': '🌙', 'rain': '🌧️', 'snow': '❄️', 'wind': '🌬️',
    # Generic & Common
    'search': '🔍', 'find': '🔎', 'list': '📝', 'map': '🗺️', 'guide': '📖',
    'tutorial': '📚', 'info': 'ℹ️', 'about': 'ℹ️', 'contact': '📧', 'home': '🏠',
    'user': '👤', 'setting': '⚙️', 'config': '🛠️', 'tool': '🔧', 'app': '📱'
}

# 需要被覆盖的弱图标
WEAK_ICONS = ['🔧', '🌐', '🧮', '1️⃣', '❓', '📄', '📝', '✅', '🔍', '']

# --- 3. 辅助函数 ---

def write_if_changed(file_path, new_content):
    """智能写入：只有内容变化才写入，避免Git红一片"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if f.read() == new_content: return False
        except: pass
    
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.write(new_content)
    return True

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
        if 'ca-pub-9279583389810634' in content: return
        if '</head>' in content:
            new_content = content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>')
            if write_if_changed(file_path, new_content):
                print(f"  [广告] 已注入: {os.path.basename(file_path)}")
    except: pass

def get_category_by_name(filename):
    tid = filename.lower().replace('.html', '')
    
    # 关键词匹配
    for cat, kws in KEYWORD_CATEGORIES.items():
        for kw in kws:
            if kw in tid: return cat
            
    # Meta 标签兜底 (与 manage_all 保持一致)
    # 这里只保留了文件名判断，简化逻辑，如有需要可加回读取文件内容判断
    return 'others'

def get_icon(tool_id, existing_icon_map):
    # 优先用已有的强图标
    existing_icon = existing_icon_map.get(tool_id, '🔧')
    if existing_icon not in WEAK_ICONS:
        return existing_icon
    
    # 尝试用备份库匹配
    tool_id_lower = tool_id.lower()
    # 优先匹配长词
    sorted_keys = sorted(BACKUP_ICONS.keys(), key=len, reverse=True)
    for kw in sorted_keys:
        if kw in tool_id_lower:
            return BACKUP_ICONS[kw]
            
    return existing_icon

def main():
    print("\n🚀 启动 Organize (整理 & 修复)...")
    
    if not os.path.exists(MODULES_DIR):
        print(f"❌ 错误：找不到 {MODULES_DIR} 目录")
        return

    # A. 预加载旧数据 (保留图标设置)
    existing_icon_map = {}
    if os.path.exists(TOOLS_JSON_FILE):
        try:
            with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for item in old_data:
                    if 'icon' in item:
                        existing_icon_map[item['id']] = item['icon']
        except: pass

    # B. 文件整理与广告
    print(">>> 正在归档文件...")
    for root, dirs, files in os.walk(MODULES_DIR):
        # 修复：移除 if root == MODULES_DIR: continue，允许处理根目录文件
        for filename in files:
            if filename.endswith('.html'):
                current_path = os.path.join(root, filename)
                
                # 计算目标路径
                new_filename = to_kebab_case(filename)
                target_cat = get_category_by_name(new_filename)
                
                # 特殊分类修正
                if 'date' in target_cat or 'time' in target_cat: target_cat = 'date-time'
                
                target_dir = os.path.join(MODULES_DIR, target_cat)
                target_path = os.path.join(target_dir, new_filename)
                
                # 移动文件
                if os.path.abspath(current_path) != os.path.abspath(target_path):
                    if not os.path.exists(target_dir): os.makedirs(target_dir)
                    try:
                        shutil.move(current_path, target_path)
                        print(f"  [移动] {filename} -> {target_cat}/{new_filename}")
                        # 更新当前路径以便后续处理
                        current_path = target_path
                    except Exception as e:
                        print(f"  [错误] 移动失败: {filename} ({e})")
                
                # 注入广告 (智能写入)
                inject_ads_to_file(current_path)

    # C. 清理空目录
    for root, dirs, files in os.walk(MODULES_DIR, topdown=False):
        for name in dirs:
            try: os.rmdir(os.path.join(root, name))
            except: pass

    # D. 生成 JSON (Schema 修复: path, description)
    print(">>> 正在生成 tools.json...")
    new_tools_data = []
    
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                tid = file[:-5]
                cat = os.path.basename(root)
                if 'date' in cat or 'time' in cat: cat = 'date-time'
                
                display_title = tid.replace('-', ' ').title()
                
                # 关键修复：使用 path 而不是 file
                web_path = f"modules/{cat}/{file}".replace('\\', '/')
                
                icon = get_icon(tid, existing_icon_map)
                
                entry = {
                    "id": tid,
                    "title": display_title,
                    "category": cat,
                    "path": web_path,  # 修复为 path
                    "description": f"Free online {display_title} tool.", # 修复为 description
                    "icon": icon
                }
                new_tools_data.append(entry)

    new_tools_data.sort(key=lambda x: (x['category'], x['id']))
    
    new_json_content = json.dumps(new_tools_data, indent=2, ensure_ascii=False)
    if write_if_changed(TOOLS_JSON_FILE, new_json_content):
        print(f"✅ tools.json 已更新 (共 {len(new_tools_data)} 个工具)")
    else:
        print("⏩ tools.json 无需更新")

if __name__ == '__main__':
    main()