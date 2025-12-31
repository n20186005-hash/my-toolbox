import datetime
import json
import os
import re
import shutil

# ================= 配置区域 =================
MODULES_DIR = 'modules'
TOOLS_JSON_FILE = 'tools.json'
SITE_DOMAIN = "https://toolboxpro.top"
ADSENSE_ID = "ca-pub-9279583389810634"

ADSENSE_SCRIPT = f'''<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>'''

IGNORE_DIRS = {'.git', '.github', '__pycache__', 'scripts', 'node_modules', 'venv'}

# --- 关键词分类配置 (保持原样) ---
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

# 图标库补全
BACKUP_ICONS = {
    'resistor': '🔌', 'ohm': 'Ω', 'voltage': '⚡', 'circuit': '🔌', 'capacitor': '🔋', 'drop': '💧', 'zener': '⚡', 'current': '〰️', 'electricity': '💡', 'induct': '🌀', 'dbm': '📶', 'frequency': '📻', 'pcb': '📟', 'solder': '🔥', 'battery': '🔋', 'physic': '⚛️', 'force': '💪', 'velocity': '🏎️', 'gravity': '🍎', 'acceleration': '🚀', 'density': '🧱', 'power': '⚡', 'pressure': '🌡️', 'torque': '🔧', 'energy': '🔋', 'kinematic': '🏃', 'thermodynamic': '🔥', 'optics': '🔦', 'quantum': '🌌', 'chem': '🧪', 'periodic': '📑', 'molar': '⚖️', 'atom': '⚛️', 'molecule': '⚗️', 'ph': '💧', 'reaction': '💥', 'solution': '🥃', 'gas': '⛽', 'acid': '🍋', 'calculator': '🧮', 'math': '➕', 'algebra': '✖️', 'geometry': '📐', 'stat': '📊', 'average': '📉', 'prime': '🔢', 'factor': '➗', 'number': '1️⃣', 'percent': '％', 'fraction': '½', 'shape': '🔷', 'area': '🟥', 'volume': '🧊', 'surface': '🎨', 'matrix': '▦', 'vector': '↗️', 'logarithm': '🪵', 'trigonometry': '📐', 'circle': '⭕', 'triangle': '🔺', 'square': '🟥', 'cube': '🎲', 'root': '🌱', 'derivative': '∂', 'integral': '∫', '401k': '💰', 'loan': '💸', 'mortgage': '🏠', 'salary': '💵', 'tax': '🧾', 'invest': '📈', 'currency': '💱', 'interest': '℅', 'retirement': '🏖️', 'deposit': '🏦', 'bank': '🏛️', 'budget': '📝', 'gdp': '🌏', 'inflation': '🎈', 'roi': '💹', 'cagr': '📈', 'profit': '💰', 'margin': '📊', 'vat': '🧾', 'gst': '🧾', 'stock': '📉', 'crypto': '₿', 'bitcoin': '₿', 'exchange': '💱', 'check': '✅', 'payment': '💳', 'debt': '📉', 'compound': '📈', 'discount': '🏷️', 'code': '👨‍💻', 'json': '📋', 'xml': '📜', 'html': '🌐', 'css': '🎨', 'base64': '📦', 'dev': '🛠️', 'minify': '🤏', 'formatter': '✨', 'hash': '#️⃣', 'encrypt': '🔒', 'decrypt': '🔓', 'language': '🗣️', 'regex': '🔍', 'sql': '🗄️', 'dns': '🌍', 'whois': '❓', 'cron': '⏰', 'uuid': '🆔', 'guid': '🆔', 'ip': '📍', 'subnet': '🕸️', 'diff': '↔️', 'markdown': '⬇️', 'url': '🔗', 'javascript': '☕', 'python': '🐍', 'java': '☕', 'git': '🌲', 'docker': '🐳', 'linux': '🐧', 'terminal': '💻', 'api': '🔌', 'unicode': '🔣', 'ascii': '🔡', 'date': '📅', 'time': '⏰', 'clock': '🕰️', 'calendar': '🗓️', 'stopwatch': '⏱️', 'timer': '⏲️', 'zone': '🌍', 'runyue': '🌒', 'countdown': '⏳', 'timestamp': '⌚', 'daylight': '☀️', 'duration': '⌛', 'meeting': '🤝', 'world': '🌏', 'age': '🎂', 'birthday': '🍰', 'year': '📅', 'month': '📆', 'week': '🗓️', 'day': '☀️', 'amazon': '📦', 'ebay': '🛍️', 'shopify': '👜', 'sales': '📈', 'shipping': '🚚', 'asoch': '🔍', 'fba': '📦', 'pricing': '🏷️', 'commission': '💰', 'inventory': '📦', 'image': '🖼️', 'photo': '📷', 'resize': '📏', 'crop': '✂️', 'png': '🎨', 'jpg': '📸', 'svg': '✒️', 'compress': '🗜️', 'watermark': '©️', 'convert-to-image': '🖼️', 'favicon': '🔖', 'ico': '🔖', 'pixel': '👾', 'blur': '🌫️', 'filter': '🎨', 'text': '📄', 'word': '🔤', 'count': '🔢', 'lorem': '📝', 'string': '🧵', 'case': 'Aa', 'editor': '✍️', 'font': '🅰️', 'pinyin': '🇨🇳', 'slug': '🐌', 'upper': '⬆️', 'lower': '⬇️', 'camel': '🐫', 'snake': '🐍', 'kebab': '🍢', 'color': '🎨', 'rgb': '🌈', 'hex': '#️⃣', 'palette': '🎨', 'picker': '🖌️', 'contrast': '🌗', 'gradient': '🌈', 'cmyk': '🖨️', 'hcl': '🎨', 'convert': '🔄', 'unit': '📏', 'farenheit': '🌡️', 'celsius': '🌡️', 'weight': '⚖️', 'length': '📏', 'speed': '🚀', 'area-convert': '🟥', 'pressure-convert': '🎈', 'volume-convert': '🧊', 'mass': '⚖️', 'metric': '📏', 'imperial': '🦶', 'bmi': '⚖️', 'calorie': '🍎', 'fat': '🥓', 'health': '🏥', 'heart': '❤️', 'pregnancy': '🤰', 'bac': '🍺', 'bmr': '🔥', 'tdee': '🏃', 'macro': '🥗', 'body': '🧍', 'ovulation': '🥚', 'period': '🩸', 'sleep': '😴', 'water-intake': '💧', 'bra-size': '👙', 'shoe-size': '👟', 'ideal-weight': '⚖️', 'protein': '🥩', 'carb': '🍞', 'life': '🌱', 'habit': '✅', 'goal': '🎯', 'wedding': '💍', 'event': '🎉', 'shengxiao': '🐉', 'zodiac': '♈', 'chinese-zodiac': '🐉', 'decision': '⚖️', 'car': '🚗', 'fuel': '⛽', 'mpg': '⛽', 'gas': '⛽', 'vehicle': '🚙', 'plate': '🆔', 'vin': '🔍', 'tire': '🍩', 'horsepower': '🐎', 'engine': '⚙️', 'grade': '💯', 'gpa': '🎓', 'study': '📚', 'student': '🎒', 'school': '🏫', 'exam': '📝', 'quiz': '❓', 'college': '🏛️', 'university': '🎓', 'course': '📘', 'game': '🎮', 'joke': '🤡', 'meme': '😂', 'random': '🎲', 'dice': '🎲', 'love': '❤️', 'solitaire': '🃏', 'flames': '🔥', 'compatibility': '💑', 'puzzle': '🧩', 'sudoku': '🔢', 'chess': '♟️', 'password': '🔑', 'generator': '⚙️', 'security': '🛡️', '2fa': '📱', 'totp': '🔐', 'md5': '#️⃣', 'sha': '#️⃣', 'safe': '🔐', 'lock': '🔒', 'key': '🗝️', 'concrete': '🏗️', 'brick': '🧱', 'tile': '🔲', 'paint': '🖌️', 'roof': '🏠', 'flooring': '🪵', 'wallpaper': '🖼️', 'gravel': '🪨', 'sand': '⏳', 'garden': '🏡', 'plant': '🌿', 'seed': '🌰', 'soil': '🟤', 'water': '🚿', 'fertilizer': '💩', 'mulch': '🍂', 'flower': '🌸', 'tree': '🌳', 'pet': '🐾', 'dog': '🐶', 'cat': '🐱', 'food': '🍖', 'animal': '🦁', 'fish': '🐟', 'aquarium': '🐠', 'bird': '🐦', 'hamster': '🐹', 'sport': '⚽', 'running': '🏃', 'pace': '⏱️', 'score': '🏆', 'team': '👕', 'golf': '⛳', 'cricket': '🏏', 'football': '🏈', 'basketball': '🏀', 'tennis': '🎾', 'probability': '🎲', 'mean': 'µ', 'median': '📊', 'mode': '📊', 'deviation': 'σ', 'sample': '📉', 'permutation': '🔄', 'combination': '🎲', 'z-score': '📊', 'weather': '☁️', 'air': '💨', 'quality': '😷', 'aqi': '🌫️', 'humidity': '💧', 'sun': '☀️', 'moon': '🌙', 'rain': '🌧️', 'snow': '❄️', 'wind': '🌬️', 'search': '🔍', 'find': '🔎', 'list': '📝', 'map': '🗺️', 'guide': '📖', 'tutorial': '📚', 'info': 'ℹ️', 'about': 'ℹ️', 'contact': '📧', 'home': '🏠', 'user': '👤', 'setting': '⚙️', 'config': '🛠️', 'tool': '🔧', 'app': '📱'
}
WEAK_ICONS = ['🔧', '🌐', '🧮', '1️⃣', '❓', '📄', '📝', '✅']

# ================= 辅助函数 (核心逻辑) =================

def write_if_changed(file_path, new_content):
    new_content_norm = new_content.replace('\r\n', '\n').strip()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content_norm = f.read().replace('\r\n', '\n').strip()
            if old_content_norm == new_content_norm:
                return False
        except: pass
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    return True

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
    if existing_icon not in WEAK_ICONS:
        return existing_icon
    fname_lower = filename.lower()
    for key, icon in BACKUP_ICONS.items():
        if key in fname_lower: return icon
    return existing_icon

def get_category_from_content(file_path, filename):
    tool_id = filename.lower().replace('.html', '')
    if tool_id in SPECIFIC_FIXES: return SPECIFIC_FIXES[tool_id]
    for cat_folder, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            if kw in tool_id: return cat_folder
    return 'others'

# ================= 任务执行 =================

def run_task_organize():
    print(">>> 🛠️ 正在整理分类并更新 tools.json...")
    if not os.path.exists(MODULES_DIR): return

    # 1. 加载旧图标
    existing_icon_map = {}
    if os.path.exists(TOOLS_JSON_FILE):
        try:
            with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for item in old_data: existing_icon_map[item['id']] = item.get('icon', '🔧')
        except: pass

    # 2. 移动与归类 (由于要避免误操作，此处仅在文件名不规范时移动)
    for root, dirs, files in os.walk(MODULES_DIR):
        for filename in files:
            if filename.endswith('.html'):
                original_path = os.path.join(root, filename)
                category = get_category_from_content(original_path, filename)
                new_filename = to_kebab_case(filename)
                target_dir = os.path.join(MODULES_DIR, category)
                target_path = os.path.join(target_dir, new_filename)
                
                if os.path.abspath(original_path) != os.path.abspath(target_path):
                    if not os.path.exists(target_dir): os.makedirs(target_dir)
                    shutil.move(original_path, target_path)

    # 3. 重新扫描并生成 tools.json
    tools_data = []
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                tool_id = file[:-5]
                folder = os.path.basename(root)
                display_title = tool_id.replace('-', ' ').title()
                tools_data.append({
                    "id": tool_id,
                    "title": display_title,
                    "category": folder,
                    "path": f"modules/{folder}/{file}",
                    "description": f"Free online {display_title} tool.",
                    "icon": get_icon(tool_id, file, existing_icon_map)
                })
    
    tools_data.sort(key=lambda x: (x['category'], x['id']))
    if write_if_changed(TOOLS_JSON_FILE, json.dumps(tools_data, indent=2, ensure_ascii=False)):
        print("✅ tools.json 已同步 (含图标)")

def run_task_canonical():
    print(">>> 🔍 检查 SEO 标签...")
    root_dir = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            if filename.endswith('.html'):
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
                canonical_url = f"{SITE_DOMAIN}/{rel_path}" if rel_path != 'index.html' else f"{SITE_DOMAIN}/"
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if f'rel="canonical"' in content and canonical_url in content: continue

                if 'rel="canonical"' in content:
                    new_content = re.sub(r'<link rel="canonical".*?>', f'<link rel="canonical" href="{canonical_url}" />', content)
                else:
                    new_content = content.replace('</title>', f'</title>\n    <link rel="canonical" href="{canonical_url}" />', 1)
                
                write_if_changed(file_path, new_content)

def run_task_adsense():
    print(">>> 💰 检查 AdSense...")
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if ADSENSE_ID in content: continue
                if '</head>' in content:
                    new_content = content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>')
                    write_if_changed(file_path, new_content)

def run_task_sitemap():
    print(">>> 🗺️ 检查 Sitemap...")
    if not os.path.exists(TOOLS_JSON_FILE): return
    today = datetime.date.today().isoformat()
    with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f: tools = json.load(f)
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f'  <url><loc>{SITE_DOMAIN}/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>\n'
    for t in tools:
        loc = f"{SITE_DOMAIN}/{t['path']}".replace("&", "&amp;")
        xml += f'  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>\n'
    xml += '</urlset>'
    write_if_changed('sitemap.xml', xml)

if __name__ == '__main__':
    run_task_organize()
    run_task_canonical()
    run_task_adsense()
    run_task_sitemap()
    print("\n🎉 维护任务完成。Git 仅会显示真正有变动的文件。")