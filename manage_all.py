# ==========================================
# 修复版 manage_all.py
# 核心改进：加入“防抖”机制，只有内容变了才写入，解决 Git 全红问题
# ==========================================

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

# 广告代码
ADSENSE_SCRIPT = f'''
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}"
     crossorigin="anonymous"></script>
'''

# 忽略目录
IGNORE_DIRS = {'.git', '.github', '__pycache__', 'scripts', 'node_modules', 'venv'}

# --- 核心关键词分类配置 ---
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

BACKUP_ICONS = {
    'resistor': '🔌', 'ohm': 'Ω', 'voltage': '⚡', 'circuit': '🔌', 'capacitor': '🔋', 'drop': '💧', 'zener': '⚡', 'current': '〰️', 'electricity': '💡', 'induct': '🌀', 'dbm': '📶', 'frequency': '📻', 'pcb': '📟', 'solder': '🔥', 'battery': '🔋', 'physic': '⚛️', 'force': '💪', 'velocity': '🏎️', 'gravity': '🍎', 'acceleration': '🚀', 'density': '🧱', 'power': '⚡', 'pressure': '🌡️', 'torque': '🔧', 'energy': '🔋', 'kinematic': '🏃', 'thermodynamic': '🔥', 'optics': '🔦', 'quantum': '🌌', 'chem': '🧪', 'periodic': '📑', 'molar': '⚖️', 'atom': '⚛️', 'molecule': '⚗️', 'ph': '💧', 'reaction': '💥', 'solution': '🥃', 'gas': '⛽', 'acid': '🍋', 'calculator': '🧮', 'math': '➕', 'algebra': '✖️', 'geometry': '📐', 'stat': '📊', 'average': '📉', 'prime': '🔢', 'factor': '➗', 'number': '1️⃣', 'percent': '％', 'fraction': '½', 'shape': '🔷', 'area': '🟥', 'volume': '🧊', 'surface': '🎨', 'matrix': '▦', 'vector': '↗️', 'logarithm': '🪵', 'trigonometry': '📐', 'circle': '⭕', 'triangle': '🔺', 'square': '🟥', 'cube': '🎲', 'root': '🌱', 'derivative': '∂', 'integral': '∫', '401k': '💰', 'loan': '💸', 'mortgage': '🏠', 'salary': '💵', 'tax': '🧾', 'invest': '📈', 'currency': '💱', 'interest': '℅', 'retirement': '🏖️', 'deposit': '🏦', 'bank': '🏛️', 'budget': '📝', 'gdp': '🌏', 'inflation': '🎈', 'roi': '💹', 'cagr': '📈', 'profit': '💰', 'margin': '📊', 'vat': '🧾', 'gst': '🧾', 'stock': '📉', 'crypto': '₿', 'bitcoin': '₿', 'exchange': '💱', 'check': '✅', 'payment': '💳', 'debt': '📉', 'compound': '📈', 'discount': '🏷️', 'code': '👨‍💻', 'json': '📋', 'xml': '📜', 'html': '🌐', 'css': '🎨', 'base64': '📦', 'dev': '🛠️', 'minify': '🤏', 'formatter': '✨', 'hash': '#️⃣', 'encrypt': '🔒', 'decrypt': '🔓', 'language': '🗣️', 'regex': '🔍', 'sql': '🗄️', 'dns': '🌍', 'whois': '❓', 'cron': '⏰', 'uuid': '🆔', 'guid': '🆔', 'ip': '📍', 'subnet': '🕸️', 'diff': '↔️', 'markdown': '⬇️', 'url': '🔗', 'javascript': '☕', 'python': '🐍', 'java': '☕', 'git': '🌲', 'docker': '🐳', 'linux': '🐧', 'terminal': '💻', 'api': '🔌', 'unicode': '🔣', 'ascii': '🔡', 'date': '📅', 'time': '⏰', 'clock': '🕰️', 'calendar': '🗓️', 'stopwatch': '⏱️', 'timer': '⏲️', 'zone': '🌍', 'runyue': '🌒', 'countdown': '⏳', 'timestamp': '⌚', 'daylight': '☀️', 'duration': '⌛', 'meeting': '🤝', 'world': '🌏', 'age': '🎂', 'birthday': '🍰', 'year': '📅', 'month': '📆', 'week': '🗓️', 'day': '☀️', 'amazon': '📦', 'ebay': '🛍️', 'shopify': '👜', 'sales': '📈', 'shipping': '🚚', 'asoch': '🔍', 'fba': '📦', 'pricing': '🏷️', 'commission': '💰', 'inventory': '📦', 'image': '🖼️', 'photo': '📷', 'resize': '📏', 'crop': '✂️', 'png': '🎨', 'jpg': '📸', 'svg': '✒️', 'compress': '🗜️', 'watermark': '©️', 'convert-to-image': '🖼️', 'favicon': '🔖', 'ico': '🔖', 'pixel': '👾', 'blur': '🌫️', 'filter': '🎨', 'text': '📄', 'word': '🔤', 'count': '🔢', 'lorem': '📝', 'string': '🧵', 'case': 'Aa', 'editor': '✍️', 'font': '🅰️', 'pinyin': '🇨🇳', 'slug': '🐌', 'upper': '⬆️', 'lower': '⬇️', 'camel': '🐫', 'snake': '🐍', 'kebab': '🍢', 'color': '🎨', 'rgb': '🌈', 'hex': '#️⃣', 'palette': '🎨', 'picker': '🖌️', 'contrast': '🌗', 'gradient': '🌈', 'cmyk': '🖨️', 'hcl': '🎨', 'convert': '🔄', 'unit': '📏', 'farenheit': '🌡️', 'celsius': '🌡️', 'weight': '⚖️', 'length': '📏', 'speed': '🚀', 'area-convert': '🟥', 'pressure-convert': '🎈', 'volume-convert': '🧊', 'mass': '⚖️', 'metric': '📏', 'imperial': '🦶', 'bmi': '⚖️', 'calorie': '🍎', 'fat': '🥓', 'health': '🏥', 'heart': '❤️', 'pregnancy': '🤰', 'bac': '🍺', 'bmr': '🔥', 'tdee': '🏃', 'macro': '🥗', 'body': '🧍', 'ovulation': '🥚', 'period': '🩸', 'sleep': '😴', 'water-intake': '💧', 'bra-size': '👙', 'shoe-size': '👟', 'ideal-weight': '⚖️', 'protein': '🥩', 'carb': '🍞', 'life': '🌱', 'habit': '✅', 'goal': '🎯', 'wedding': '💍', 'event': '🎉', 'shengxiao': '🐉', 'zodiac': '♈', 'chinese-zodiac': '🐉', 'decision': '⚖️', 'car': '🚗', 'fuel': '⛽', 'mpg': '⛽', 'gas': '⛽', 'vehicle': '🚙', 'plate': '🆔', 'vin': '🔍', 'tire': '🍩', 'horsepower': '🐎', 'engine': '⚙️', 'grade': '💯', 'gpa': '🎓', 'study': '📚', 'student': '🎒', 'school': '🏫', 'exam': '📝', 'quiz': '❓', 'college': '🏛️', 'university': '🎓', 'course': '📘', 'game': '🎮', 'joke': '🤡', 'meme': '😂', 'random': '🎲', 'dice': '🎲', 'love': '❤️', 'solitaire': '🃏', 'flames': '🔥', 'compatibility': '💑', 'puzzle': '🧩', 'sudoku': '🔢', 'chess': '♟️', 'password': '🔑', 'generator': '⚙️', 'security': '🛡️', '2fa': '📱', 'totp': '🔐', 'md5': '#️⃣', 'sha': '#️⃣', 'safe': '🔐', 'lock': '🔒', 'key': '🗝️', 'concrete': '🏗️', 'brick': '🧱', 'tile': '🔲', 'paint': '🖌️', 'roof': '🏠', 'flooring': '🪵', 'wallpaper': '🖼️', 'gravel': '🪨', 'sand': '⏳', 'garden': '🏡', 'plant': '🌿', 'seed': '🌰', 'soil': '🟤', 'water': '🚿', 'fertilizer': '💩', 'mulch': '🍂', 'flower': '🌸', 'tree': '🌳', 'pet': '🐾', 'dog': '🐶', 'cat': '🐱', 'food': '🍖', 'animal': '🦁', 'fish': '🐟', 'aquarium': '🐠', 'bird': '🐦', 'hamster': '🐹', 'sport': '⚽', 'running': '🏃', 'pace': '⏱️', 'score': '🏆', 'team': '👕', 'golf': '⛳', 'cricket': '🏏', 'football': '🏈', 'basketball': '🏀', 'tennis': '🎾', 'probability': '🎲', 'mean': 'µ', 'median': '📊', 'mode': '📊', 'deviation': 'σ', 'sample': '📉', 'permutation': '🔄', 'combination': '🎲', 'z-score': '📊', 'weather': '☁️', 'air': '💨', 'quality': '😷', 'aqi': '🌫️', 'humidity': '💧', 'sun': '☀️', 'moon': '🌙', 'rain': '🌧️', 'snow': '❄️', 'wind': '🌬️', 'search': '🔍', 'find': '🔎', 'list': '📝', 'map': '🗺️', 'guide': '📖', 'tutorial': '📚', 'info': 'ℹ️', 'about': 'ℹ️', 'contact': '📧', 'home': '🏠', 'user': '👤', 'setting': '⚙️', 'config': '🛠️', 'tool': '🔧', 'app': '📱'
}

WEAK_ICONS = ['🔧', '🌐', '🧮', '1️⃣', '❓', '📄', '📝', '✅']

# ================= 辅助函数 (智能写文件) =================

def write_if_changed(file_path, new_content):
    """
    智能写入：如果文件内容没有变化，就不写入。
    防止 Git 检测到大量未修改文件的'修改'（通常是由于换行符或时间戳）。
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            if old_content == new_content:
                # 内容完全一致，直接跳过
                return False
        except:
            pass # 读取失败则视为需要写入

    # 使用 newline='' 保持 Python 内部换行符，避免 Windows 下自动转 CRLF
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
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
        if key in fname_lower:
            return icon
    return existing_icon

def get_category_from_content(file_path, filename):
    tool_id = filename.lower().replace('.html', '')
    while tool_id.endswith('.html'): tool_id = tool_id[:-5]
    
    if tool_id in SPECIFIC_FIXES: return SPECIFIC_FIXES[tool_id]
    
    for cat_folder, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            if kw in tool_id: return cat_folder
            
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

# ================= 任务 1: Organize (整理分类) =================

def run_task_organize():
    print(">>> 🛠️ 正在整理文件结构...")
    if not os.path.exists(MODULES_DIR):
        print(f"❌ 错误：找不到 {MODULES_DIR} 文件夹。")
        return

    existing_icon_map = {}
    if os.path.exists(TOOLS_JSON_FILE):
        try:
            with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for item in old_data:
                    if 'icon' in item:
                        existing_icon_map[item['id']] = item['icon']
        except: pass

    # 1. 移动文件
    moved_count = 0
    for root, dirs, files in os.walk(MODULES_DIR):
        for filename in files:
            if filename.endswith('.html'):
                original_path = os.path.join(root, filename)
                category = get_category_from_content(original_path, filename)
                if 'date' in category or 'time' in category: category = 'date-time'

                new_filename = to_kebab_case(filename)
                target_dir = os.path.join(MODULES_DIR, category)
                target_path = os.path.join(target_dir, new_filename)
                
                # 只有路径真正改变时才移动
                if os.path.abspath(original_path) != os.path.abspath(target_path):
                    if not os.path.exists(target_dir): os.makedirs(target_dir)
                    try:
                        shutil.move(original_path, target_path)
                        print(f"✅ 移动: {filename} -> {category}/{new_filename}")
                        moved_count += 1
                    except Exception as e:
                        print(f"⚠️ 移动失败: {filename} -> {e}")

    # 2. 清理空目录
    for root, dirs, files in os.walk(MODULES_DIR, topdown=False):
        for name in dirs:
            try: os.rmdir(os.path.join(root, name))
            except: pass

    # 3. 生成 tools.json (带内容对比检测)
    print(">>> 正在检查 tools.json...")
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
    
    new_json_content = json.dumps(tools_data, indent=2, ensure_ascii=False)
    if write_if_changed(TOOLS_JSON_FILE, new_json_content):
        print("✅ tools.json 已更新")
    else:
        print("⏩ tools.json 无需更新")

# ================= 任务 2: Canonical (SEO 标签) =================

def run_task_canonical():
    print(">>> 🔍 正在检查 Canonical 标签...")
    root_dir = os.getcwd()
    count = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 排除忽略目录
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            if filename.endswith('.html'):
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
                
                if filename == 'index.html' and rel_path == 'index.html':
                    canonical_url = f"{SITE_DOMAIN}/"
                else:
                    if not rel_path.startswith('/'): rel_path = '/' + rel_path
                    canonical_url = f"{SITE_DOMAIN}{rel_path}"

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # 如果已存在且链接正确，不碰文件
                    if f'link rel="canonical" href="{canonical_url}"' in content:
                        continue
                    
                    # 如果存在但链接不对（旧的），或者完全不存在，则替换/插入
                    if 'rel="canonical"' in content:
                        # 简单正则替换旧标签
                        new_content = re.sub(r'<link rel="canonical".*?>', f'<link rel="canonical" href="{canonical_url}" />', content)
                    else:
                        tag = f'\n    \n    <link rel="canonical" href="{canonical_url}" />'
                        if '</title>' in content:
                            new_content = content.replace('</title>', '</title>' + tag, 1)
                        elif '<head>' in content:
                            new_content = content.replace('<head>', '<head>' + tag, 1)
                        else:
                            continue

                    if write_if_changed(file_path, new_content):
                        print(f"✅ 修复 SEO: {rel_path}")
                        count += 1
                except Exception as e:
                    print(f"⚠️ 读取出错 {file_path}: {e}")
                    
    print(f"Canonical 检查完成，更新了 {count} 个文件。")

# ================= 任务 3: AdSense (广告代码) =================

def run_task_adsense():
    print(">>> 💰 正在检查 AdSense 代码...")
    count = 0
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # 严格检查 Client ID，如果有了就绝对不碰
                    if ADSENSE_ID in content:
                        continue

                    if '</head>' in content:
                        new_content = content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>')
                        if write_if_changed(file_path, new_content):
                            print(f"✅ 添加广告: {file}")
                            count += 1
                except: pass
                
    print(f"AdSense 检查完成，更新了 {count} 个文件。")

# ================= 任务 4: Sitemap (网站地图) =================

def run_task_sitemap():
    print(">>> 🗺️ 正在生成 Sitemap...")
    if not os.path.exists(TOOLS_JSON_FILE):
        return

    today = datetime.date.today().isoformat()
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # 首页
    xml_content += f"""  <url>
    <loc>{SITE_DOMAIN}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>\n"""

    try:
        with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
            tools = json.load(f)

        for tool in tools:
            path = tool['path']
            if path.startswith('/'): path = path[1:]
            full_url = f"{SITE_DOMAIN}/{path}".replace("&", "&amp;")

            xml_content += f"""  <url>
    <loc>{full_url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>\n"""
    except: pass

    xml_content += '</urlset>'
    
    # 注意：Sitemap 因为包含 current_date，如果你每天运行，它依然会显示“修改”
    # 这是正常的，因为你确实希望告诉 Google "我今天确认过这个文件了"
    # 但我们依然使用 write_if_changed 来防止同一天内多次运行产生变化
    if write_if_changed('sitemap.xml', xml_content):
        print(f"✅ sitemap.xml 已更新 ({len(tools) + 1} 个链接)")
    else:
        print("⏩ sitemap.xml 无需更新 (今日已生成)")

# ================= 主程序入口 =================

if __name__ == '__main__':
    print('🤖 [ALL-IN-ONE] 维护脚本启动...')

    try:
        run_task_organize()
    except Exception as e: print(f'⚠️ Organize 错误: {e}')

    try:
        run_task_canonical() # 变量名已修复
    except Exception as e: print(f'⚠️ SEO 错误: {e}')

    try:
        run_task_adsense()
    except Exception as e: print(f'⚠️ AdSense 错误: {e}')

    try:
        run_task_sitemap()
    except Exception as e: print(f'⚠️ Sitemap 错误: {e}')

    print('\n🎉 所有任务执行完毕！现在 Git 应该很干净了。')