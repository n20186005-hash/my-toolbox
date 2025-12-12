import os
import shutil
import re
import json

# 配置路径
MODULES_DIR = 'modules'
TOOLS_JSON_FILE = 'tools.json'

# --- 0. 你的 AdSense 广告代码 ---
ADSENSE_SCRIPT = r'''
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9279583389810634"
     crossorigin="anonymous"></script>
'''

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

# --- 2. 强力纠错名单 ---
SPECIFIC_FIXES = {
    'mortgage-calculator-uk': 'finance',
    'canadian-mortgage': 'finance',
    'percentage-calculator': 'math',
    'language-switcher': 'development-tools',
    'world-clock-meeting-planner': 'date-time'
}

# --- 3. 图标备份库 ---
BACKUP_ICONS = {
    'molarity': '🧪', 'molecular': '⚗️', 'half-life': '⚛️', 'periodic': '🧬', 'chemical': '🧪',
    'z-score': '📊', 'standard-deviation': '📈', 'probability': '🎲', 'p-value': '📈', 'statistics': '📊',
    'confidence': '📈', 'sample-size': '📊', 'weight': '👤', 'gfr': '🔍', 'body-type': '📏',
    'safe-period': '📅', 'bra-size': '👙', 'ovulation': '🌙', 'calorie': '🍽️', 'anorexic': '📊',
    'overweight': '⚖️', 'sleep': '😴', 'ideal-weight': '⚖️', 'shoe-size': '👟', 'pregnancy': '👶',
    'height': '📏', 'fetal': '👶', 'bmr': '❤️', 'carbohydrate': '🍞', 'blood': '🅱️',
    'heart-rate': '❤️', 'food-calorie': '🍎', 'lean-body': '💪', 'body-fat': '📊', 'macro': '🥗',
    'protein': '🥩', 'shengxiao': '🐉', 'clock': '🔧', 'timestamp': '⏱️', 'day-of-week': '📅',
    'time-card': '⏰', 'duration': '⏰', 'runyue': '📅', 'unix': '🔧', 'percent': '🔧',
    'race-time': '🔧', 'mortgage': '🔧', 'converter': '⏱️', 'countdown': '📅', 'pomodoro': '⏱️',
    'life-count': '📅', 'age': '🎂', 'day-counter': '📆', 'pace': '🏃', 'date-calc': '📆',
    'stopwatch': '⏱️', 'daylight': '⏰', 'meeting': '🔧', 'love': '🔧', 'zone': '🌐',
    'map': '🌍', 'hours': '⏰', 'chunjie': '🧧', 'difference': '🕰️', 'days': '📆',
    'birthday': '🎂', 'abbreviations': '🕒', 'relative': '👨‍👩‍👧‍👦', 'mobile': '📱', 'region': '🌍',
    'marriage': '💍', 'usa': '🗺️', 'id-query': '🔧', 'zodiac': '🎂', 'capitals': '🌍',
    'hash': '🔒', 'sphere': '🔧', 'deposit': '🔧', 'vocabulary': '💻', 'selector': '🔍',
    'conception': '🔧', 'sql': '🔧', 'shopping': '🔧', 'qr': '📱', 'compound': '🔧',
    'energy': '🔧', 'gpa': '🎓', 'speed': '🚀', 'tdee': '🔧', 'mime': '📄',
    'prism': '🔧', 'absolute': '🔧', 'subnet': '🔗', 'retirement': '🔧', 'torus': '🔧',
    'power': '⚡', 'fat': '🔧', 'temperature': '🔧', 'salary': '🔧', 'chinese': '🔧',
    'ua': '🔍', 'bac': '🔧', 'autoprefixer': '🎨', 'currency': '💱', 'sudoku': '🔧',
    'minifier': '🎨', 'inventory': '🔧', 'cidr': '🔗', 'html': '🔧', 'discount': '🔧',
    'debt': '🔧', 'points': '🔧', 'cron': '⏰', 'regex': '🔍', 'exam': '🔧',
    'frustum': '🔧', 'cone': '🔧', 'vscode': '⌨️', 'curl': '🔄', 'linux': '🐧',
    'year': '🔧', 'case': '🔧', 'programmer': '💻', 'url': '🔗', 'cdn': '🔍',
    'bmi': '🔧', 'vat': '🔧', 'title': '🔧', 'vim': '⌨️', 'go': '🔄',
    'loan': '🔧', 'git': '🔧', 'bandwidth': '🔧', 'net-pay': '🔧', 'xml': '🔄',
    'pressure': '🔧', 'entities': '🔤', 'dwz': '🔧', 'editor': '📝', 'investment': '🔧',
    'javascript': '🔧', 'markdown': '🔧', 'cylinder': '🔧', 'escape': '🔗', 'whois': '🔍',
    'http': '🌐', 'key': '⌨️', 'base': '🔧', 'request': '🔗', 'final': '🔧',
    'bsa': '🔧', 'star': '⭐', 'mass': '⚖️', 'density': '⚖️', 'class': '🔧',
    'college': '🎓', 'gaokao': '🎓', 'global': '🌍', 'grade': '📚', 'sun': '🔧',
    'heat': '🌡️', 'wind': '🌬️', 'weather': '🌤️', 'water': '💧', 'prime': '🔧',
    'length': '📏', 'fraction': '🔢', 'roman': '🔢', 'multi': '🔧', 'binary': '🔢',
    'scientific': '🔢', 'bernoulli': 'B', 'ratio': '📊', 'gamma': '📐', 'fibonacci': '🔢',
    'taylor': '🔬', '3d': '🔺', 'area': '📏', 'limit': '📈', 'integral': '∫',
    'complex': '√', 'cos': '📐', 'exponent': 'ⁿ', 'gas': '🔬', 'trigonometry': 'sin',
    'ring': '💍', 'derivative': '📈', 'traffic': '📊', 'gcd': '🧮', 'common': '🔗',
    'hex': '🔣', 'variance': 'σ', 'footage': '📏', 'distance': '📍', 'random': '🎲',
    'surface': '📏', 'factor': '🧮', 'big': '🔢', 'factoring': '🔢', 'hexagonal': '🔧',
    'volume': '📦', 'graphing': '📈', 'pythagorean': '📐', 'quadratic': '📐', 'combination': 'C',
    'simplifier': '✏️', 'expression': '📐', 'factorial': '❏', 'average': '📊', 'error': '%%',
    'lcm': '🔢', 'log': '🔢', 'permutation': '🔢', 'series': '🔢', 'root': '√',
    'division': '➗', '2d': '📐', 'basic': '➕', 'sequence': '🔢', 'equation': '📐',
    'circular': '⭕', 'latex': '∑', 'cube': '³', 'right': '🔺', 'rounding': '📐',
    'inverse': '🔄', 'matrix': '🧮', 'slope': '📉', 'euler': 'E', 'advanced': '🔧',
    'notation': '🔬', 'triangle': '🔺', 'mileage': '🚗', 'plate': '🚗', 'fuel': '⛽',
    'tire': '🚗', 'horsepower': '🚗', 'vin': '🚗', 'engine': '🚗', 'tank': '🐠',
    'concrete': '🏗️', 'tile': '🧱', 'roofing': '🏠', 'stair': '🔺', 'gravel': '⛏️',
    'pricing': '🔧', 'forbidden': '✂️', 'pinduoduo': '🛍️', 'operation': '🛍️', 'amazon': '🛍️',
    'shipping': '🔧', 'tax': '🔧', 'compare': '🛍️', 'trademark': '🏷️', 'resistor': '🎛️',
    'sampling': '📊', 'resistance': 'Ω', 'voltage': '⚡', 'zener': '💡', 'current': '⚡',
    'electricity': '🔌', '2fa': '🔒', 'password': '🔐', 'check': '🔑', 'golf': '⛳',
    'payment': '💰', 'amortization': '📋', 'commission': '💸', 'take-home': '💵', 'cash': '💳',
    'roth': '💹', 'va': '🏠', '401k': '💰', 'personal': '💰', 'tip': '💸',
    'rent': '🏠', 'boat': '🚤', 'cd': '💲', 'gdp': '📊', 'future': '💰',
    'inflation': '💸', 'income': '💰', 'finance': '💰', 'insurance': '🏥', 'rental': '🏠',
    'uk': '🏠', 'depreciation': '💸', 'student': '🎓', 'anime4k': '🖼️', 'btu': '🔥',
    'storage': '🔧', 'cpu': '💻', 'unit': '🔄', 'conversion': '🔄', 'emoji': '😊',
    'renpin': '😊', 'dice': '🎲', 'solitaire': '🔧', 'paper': '📏', 'new-word': '🔧',
    'japanese': '🔤', 'translator': '🌐', 'zero-width': '🔒', 'symbols': '🔣', 'remover': '✂️',
    'morse': '🔐', 'font': '✏️', 'letter': 'Aa', 'braille': '🔒', 'autospace': '🔤',
    'pinyin': '🔤', 'speech': '🔊', 'abstract': '🔧', 'encoding': '🔤', 'mulch': '🌱',
    'colors': '🎨'
}

def to_kebab_case(name):
    name_no_ext = os.path.splitext(name)[0]
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name_no_ext)
    s1 = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1)
    clean_name = s1.lower().replace(' ', '-').replace('_', '-')
    clean_name = re.sub(r'-+', '-', clean_name)
    return clean_name + '.html'

def get_icon(tool_id, filename, existing_icon_map):
    if tool_id in existing_icon_map and existing_icon_map[tool_id] != '🔧':
        return existing_icon_map[tool_id]
    for key, icon in BACKUP_ICONS.items():
        if key in filename.lower():
            return icon
    return '🔧'

def inject_ads_to_file(file_path):
    """自动给文件植入 AdSense 代码"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 如果文件里已经有 client ID，就说明加过了，直接返回
        if 'ca-pub-9279583389810634' in content:
            return

        if '</head>' in content:
            new_content = content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"💰 [自动广告] 已为新文件添加广告: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"⚠️ 广告植入失败: {file_path} - {e}")

def get_category_from_content(file_path, filename):
    tool_id = filename.replace('.html', '')
    if tool_id in SPECIFIC_FIXES: return SPECIFIC_FIXES[tool_id]
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            match = re.search(r'<meta\s+name=["\']category["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
            if match:
                raw_cat = match.group(1).lower().strip()
                if 'date' in raw_cat and 'time' in raw_cat: return 'date-time'
                if 'math' in raw_cat: return 'math'
                raw_cat = raw_cat.replace('&', '').replace(' ', '-')
                return re.sub(r'-+', '-', raw_cat)
    except Exception: pass
    lower_name = filename.lower()
    for cat_folder, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            if kw in lower_name: return cat_folder
    return 'others'

def main():
    if not os.path.exists(MODULES_DIR):
        print(f"错误：找不到 {MODULES_DIR} 文件夹。")
        return

    # --- 0. 读取旧图标数据 ---
    existing_icon_map = {}
    if os.path.exists(TOOLS_JSON_FILE):
        try:
            with open(TOOLS_JSON_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                for item in old_data:
                    if 'icon' in item: existing_icon_map[item['id']] = item['icon']
        except: pass

    # --- 1. 移动文件 & 自动补全广告 ---
    print("开始整理文件并检查广告代码...")
    for root, dirs, files in os.walk(MODULES_DIR):
        for filename in files:
            if filename.endswith('.html'):
                original_path = os.path.join(root, filename)
                correct_category = get_category_from_content(original_path, filename)
                new_filename = to_kebab_case(filename)
                target_dir = os.path.join(MODULES_DIR, correct_category)
                target_path = os.path.join(target_dir, new_filename)
                
                # 移动文件
                if os.path.abspath(original_path) != os.path.abspath(target_path):
                    if not os.path.exists(target_dir): os.makedirs(target_dir)
                    try: shutil.move(original_path, target_path)
                    except: pass
                
                # 🔥 关键点：文件就位后，立即检查并注入广告
                inject_ads_to_file(target_path)

    # --- 2. 生成 tools.json ---
    print("正在更新 tools.json...")
    tools_data = []
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                tool_id = file.replace('.html', '')
                current_folder = os.path.basename(root)
                category = current_folder
                if tool_id in SPECIFIC_FIXES: category = SPECIFIC_FIXES[tool_id]
                elif current_folder == MODULES_DIR: category = 'others'
                if category == 'Date & Time' or ('date' in category and 'time' in category): category = 'date-time'
                if category == 'Math': category = 'math'
                
                display_title = tool_id.replace('-', ' ').title()
                restored_icon = get_icon(tool_id, file, existing_icon_map)

                tools_data.append({
                    "id": tool_id,
                    "title": display_title,
                    "category": category,
                    "path": f"modules/{category}/{file}".replace('\\', '/'),
                    "description": f"Free online {display_title} tool.",
                    "icon": restored_icon
                })
    
    tools_data.sort(key=lambda x: x['category'])
    with open(TOOLS_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(tools_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 处理完成！分类已整理，广告已检查，列表已更新。")

if __name__ == '__main__':
    main()