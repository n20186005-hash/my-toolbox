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
    'math': ['calculator', 'math', 'algebra', 'geometry', 'stat', 'average', 'prime', 'factor', 'number', 'percent', 'fraction', 'shape', 'area', 'volume', 'surface', 'matrix', 'vector', 'logarithm', 'trigonometry'],
    'finance': ['401k', 'loan', 'mortgage', 'salary', 'tax', 'invest', 'currency', 'interest', 'retirement', 'deposit', 'bank', 'budget', 'gdp', 'inflation', 'roi', 'cagr', 'profit', 'margin', 'vat', 'gst'],
    'development-tools': ['code', 'json', 'xml', 'html', 'css', 'base64', 'dev', 'minify', 'formatter', 'hash', 'encrypt', 'language', 'regex', 'sql', 'dns', 'whois', 'cron', 'uuid', 'guid', 'ip-', 'subnet', 'diff', 'markdown', 'url-'],
    'date-time': ['date', 'time', 'clock', 'calendar', 'stopwatch', 'timer', 'zone', 'runyue', 'countdown', 'timestamp', 'daylight', 'duration', 'meeting', 'world', 'age-'], 
    'e-commerce-operations': ['profit', 'margin', 'amazon', 'ebay', 'shopify', 'discount', 'sales', 'shipping', 'asoch', 'fba', 'pricing', 'commission'],
    'image-tools': ['image', 'photo', 'resize', 'crop', 'png', 'jpg', 'svg', 'compress', 'watermark', 'convert-to-image', 'favicon', 'ico'],
    'text-tools': ['text', 'word', 'count', 'lorem', 'string', 'case', 'editor', 'markdown', 'font', 'pinyin', 'ascii', 'slug', 'diff'],
    'color-tool': ['color', 'rgb', 'hex', 'palette', 'picker', 'contrast', 'gradient'],
    'conversion': ['convert', 'unit', 'farenheit', 'celsius', 'weight', 'length', 'volume', 'temperature', 'speed', 'area-convert', 'pressure-convert'],
    'health': ['bmi', 'calorie', 'fat', 'health', 'heart', 'pregnancy', 'bac', 'bmr', 'tdee', 'macro', 'body', 'ovulation', 'period', 'sleep', 'water-intake'],
    'life': ['life', 'habit', 'goal', 'wedding', 'event', 'shengxiao', 'zodiac', 'age-calc', 'chinese-zodiac'],
    'auto': ['car', 'fuel', 'mpg', 'gas', 'vehicle', 'loan', 'plate', 'vin', 'tire', 'horsepower'],
    'education': ['grade', 'gpa', 'study', 'student', 'school', 'exam', 'quiz'],
    'fun': ['game', 'joke', 'meme', 'random', 'decision', 'dice', 'love', 'solitaire', 'flames', 'compatibility'],
    'security': ['password', 'generator', 'security', '2fa', 'totp', 'md5', 'sha'],
    'construction': ['concrete', 'brick', 'tile', 'paint', 'roof', 'flooring', 'wallpaper'],
    'gardening': ['garden', 'plant', 'seed', 'soil', 'water', 'fertilizer'],
    'pets': ['pet', 'dog', 'cat', 'food', 'animal', 'fish', 'aquarium'],
    'sports': ['sport', 'running', 'pace', 'score', 'team', 'golf', 'cricket', 'football'],
    'statistics': ['probability', 'mean', 'median', 'mode', 'deviation', 'sample', 'permutation', 'combination'],
    'weather-health': ['weather', 'air', 'quality', 'aqi', 'humidity', 'sun', 'moon']
}

# --- 2. 强力纠错名单 ---
SPECIFIC_FIXES = {
    'voltage-drop-calculator': 'electronics', 'voltage-calculator': 'electronics', 'ohm-law-calculator': 'electronics',
    'resistor-calculator': 'electronics', 'capacitor-calculator': 'electronics',
    'age-calculator': 'date-time', 'digital-clock-stopwatch': 'date-time', 'unix-timestamp-converter': 'date-time',
    'race-time-predictor': 'date-time', 'world-clock-meeting-planner': 'date-time', 'days-between-dates': 'date-time',
    'time-zone-abbreviations-worldwide-list': 'date-time', 'worldwide-time-differences-for-any-city': 'date-time',
    'time-zone-map': 'date-time', 'daylight-saving-time': 'date-time', 'date-to-chinese-uppercase': 'date-time',
    'day-of-year-calculator': 'date-time', 'calendar-generator': 'date-time', 'countdown-timer': 'date-time',
    'stopwatch': 'date-time', 'love-marriage-calculator': 'fun', 'sudoku-solver': 'fun', 
    'mortgage-calculator-uk': 'finance', 'canadian-mortgage': 'finance', 'auto-loan-comparison': 'finance',
    'bank-deposit-calculator': 'finance', 'compound-interest': 'finance', 'debt-to-income-ratio': 'finance',
    'discount-calculator': 'finance', 'general-loan-calculator': 'finance', 'investment-calculator': 'finance',
    'shopping-calculator': 'finance', 'sales-tax-vat-calculator': 'finance', 'salary-tax-stimator': 'finance',
    'salary-converter': 'finance', 'retirement-calculator': 'finance', 'retirement-calculato': 'finance',
    'language-switcher': 'e-commerce-operations', 'currency-calculator': 'e-commerce-operations',
    'title-generator': 'e-commerce-operations', 'percentage-calculator': 'math', 'multi-language': 'math',
    'body-surface-area-calculator': 'math', 'cone-calculator': 'math', 'frustum-calculator': 'math',
    'cylinder-calculator': 'math', 'standard-calculator': 'math', 'sphere-calculator': 'math',
    'rectangular-prism-calculator': 'math', 'btu-calculator': 'math', 'pregnancy-timeline': 'health',
    'tdee-calculator': 'health', 'bmi-calculator': 'health', 'bac-calculator': 'health',
    'energy-converter': 'health', 'weight-watchers-points-calculator': 'health', 'conception-calculator': 'health',
    'fat-intake-calculator': 'health', 'comprehensive-gpa-calculator': 'education', 'exam-countdown': 'education',
    'final-grade-calculator': 'education', 'power-converter': 'conversion', 'temperature-converter': 'conversion',
    'speed-converter': 'conversion', 'pressure-converter': 'conversion', 'chinese-capital-number': 'text-tools',
    'text-case-converter': 'text-tools', 'average-calculator': 'math'
}

# --- 3. 图标库 (Massively Expanded) ---
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

# --- 4. 定义需要被覆盖的“弱/通用”图标 ---
# 如果旧图标是这些，我们将尝试用更精准的图标替换它
WEAK_ICONS = ['🔧', '🌐', '🧮', '1️⃣', '❓', '📄', '📝', '✅']

# --- 5. 工具函数 ---
def to_kebab_case(filename):
    name = filename.lower()
    while name.endswith('.html'): name = name[:-5]
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1)
    clean_name = re.sub(r'[\s_.]+', '-', name)
    clean_name = re.sub(r'-+', '-', clean_name).strip('-')
    return clean_name + '.html'

def get_icon(tool_id, filename, existing_icon_map):
    existing_icon = existing_icon_map.get(tool_id, '🔧')
    
    # 策略：如果现有图标是“强”图标（不在弱图标列表中），则直接保留，防止覆盖用户自定义
    if existing_icon not in WEAK_ICONS:
        return existing_icon
    
    # 否则（现有图标是扳手、地球、计算器等），尝试从文件名匹配更精准的图标
    fname_lower = filename.lower()
    
    # 优先匹配长关键词 (避免 'car' 匹配 'card' 这种情况)
    # 遍历备份库寻找匹配
    for key, icon in BACKUP_ICONS.items():
        if key in fname_lower:
            return icon
            
    # 如果没找到更好的，且原图标不是扳手，就还是用原图标（比如保留 '🌐'）
    # 如果原图标是扳手，就返回扳手
    return existing_icon

def inject_ads_to_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'ca-pub-9279583389810634' in content: return
        if '</head>' in content:
            new_content = content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    except: pass

def get_category_from_content(file_path, filename):
    tool_id = filename.lower().replace('.html', '')
    while tool_id.endswith('.html'): tool_id = tool_id[:-5]
    
    # 优先强力纠错
    if tool_id in SPECIFIC_FIXES: return SPECIFIC_FIXES[tool_id]
    
    # 关键词匹配
    for cat_folder, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            if kw in tool_id: return cat_folder
            
    # Meta 标签兜底
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            match = re.search(r'<meta\s+name=["\']category["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
            if match:
                raw_cat = match.group(1).lower().strip()
                if 'date' in raw_cat or 'time' in raw_cat: return 'date-time'
                return raw_cat.replace(' ', '-').replace('&', '')
    except: pass
    
    return 'others'

def main():
    print(">>> 🛠️ 开始修复文件名后缀、移除重复项并修正分类 (及图标补全)...")
    
    if not os.path.exists(MODULES_DIR):
        print(f"❌ 错误：找不到 {MODULES_DIR} 文件夹。")
        return

    existing_icon_map = {}
    if os.path.exists(TOOLS_JSON_FILE):
        try:
            with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for item in old_data:
                    # 只有当现有图标存在时才保存
                    if 'icon' in item:
                        existing_icon_map[item['id']] = item['icon']
        except: pass

    # --- 1. 遍历并移动 ---
    for root, dirs, files in os.walk(MODULES_DIR):
        for filename in files:
            if filename.endswith('.html'):
                original_path = os.path.join(root, filename)
                
                # 计算分类
                category = get_category_from_content(original_path, filename)
                
                # 特殊处理：如果分类名字里就含 date/time，强制归位
                if 'date' in category or 'time' in category: category = 'date-time'

                new_filename = to_kebab_case(filename)
                target_dir = os.path.join(MODULES_DIR, category)
                target_path = os.path.join(target_dir, new_filename)
                
                if os.path.abspath(original_path) != os.path.abspath(target_path):
                    if not os.path.exists(target_dir): os.makedirs(target_dir)
                    try:
                        shutil.move(original_path, target_path)
                        print(f"✅ 修正: {filename} -> {category}/{new_filename}")
                    except Exception as e:
                        print(f"⚠️ 失败: {filename} -> {e}")
                
                if os.path.exists(target_path):
                    inject_ads_to_file(target_path)

    # --- 2. 清理空目录 ---
    for root, dirs, files in os.walk(MODULES_DIR, topdown=False):
        for name in dirs:
            try: os.rmdir(os.path.join(root, name))
            except: pass

    # --- 3. 生成 JSON ---
    print(">>> 正在生成 tools.json...")
    tools_data = []
    
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                tool_id = file[:-5]
                current_folder = os.path.basename(root)
                final_category = current_folder
                
                if 'date' in final_category or 'time' in final_category:
                    final_category = 'date-time'

                display_title = tool_id.replace('-', ' ').title()
                web_path = f"modules/{current_folder}/{file}".replace('\\', '/')
                
                tools_data.append({
                    "id": tool_id,
                    "title": display_title,
                    "category": final_category, 
                    "path": web_path,
                    "description": f"Free online {display_title} tool.",
                    "icon": get_icon(tool_id, file, existing_icon_map)
                })
    
    tools_data.sort(key=lambda x: (x['category'], x['id']))
    
    with open(TOOLS_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(tools_data, f, indent=2, ensure_ascii=False)

    print(f"🎉 完成！图标库已扩充，工具分类与路径已修复。")

if __name__ == '__main__':
    main()