import os
import json
import re

# 配置路径
MODULES_DIR = 'modules'
DETAILS_DIR = 'details'
OUTPUT_JSON = 'tools.json'

# 确保详情目录存在
if not os.path.exists(DETAILS_DIR):
    os.makedirs(DETAILS_DIR)

tools_list = []

print("-" * 50)
print(f"开始扫描 {MODULES_DIR} 目录...")
print("-" * 50)

# 遍历 modules 目录
for filename in os.listdir(MODULES_DIR):
    if filename.endswith(".html"):
        filepath = os.path.join(MODULES_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 使用正则提取元数据 (比BeautifulSoup更轻量，不需要安装依赖)
            def get_meta(name):
                # 兼容双引号和单引号
                match = re.search(r'<meta\s+name=[\"\']' + name + r'[\"\']\s+content=[\"\'](.*?)[\"\']', content, re.IGNORECASE)
                return match.group(1) if match else ""

            def get_title():
                match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                return match.group(1) if match else filename

            # 提取数据
            t_id = get_meta('tool-id') or filename.replace('.html', '')
            t_cat = get_meta('category') or 'other'
            t_icon = get_meta('icon') or '🔧'
            t_desc = get_meta('description') or '暂无描述'
            t_title = get_title()

            tool = {
                "id": t_id,
                "title": t_title,
                "icon": t_icon,
                "category": t_cat,
                "file": filename,
                "desc": t_desc,
                "detail_page": f"details/{t_id}.html"
            }
            
            tools_list.append(tool)
            
            # --- 生成工具详情页 HTML (不包含任何功能限制) ---
            detail_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{t_title} - Details</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50 p-8">
                <div class="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-lg">
                    <a href="../index.html" class="text-blue-600 hover:underline mb-4 block">&larr; Back to Tools</a>
                    <h1 class="text-3xl font-bold mb-2">{t_icon} {t_title}</h1>
                    <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">{t_cat}</span>
                    
                    <div class="mt-6 border-t pt-6">
                        <h2 class="text-xl font-bold mb-2">About this Tool</h2>
                        <p class="text-gray-600 leading-relaxed">
                            {t_desc}
                        </p>
                        <p class="mt-4 text-gray-600">
                            This tool is designed to help users with {t_cat} related tasks. 
                            It is free to use and runs entirely in your browser.
                        </p>
                    </div>

                    <div class="mt-8">
                        <a href="../{MODULES_DIR}/{filename}" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
                            Launch Tool
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 写入详情页文件
            with open(os.path.join(DETAILS_DIR, f"{t_id}.html"), 'w', encoding='utf-8') as df:
                df.write(detail_html)

print("-" * 50)
print(f"扫描完成。发现 {len(tools_list)} 个工具。")
print("-" * 50)

# ！！重要检查！！：如果在这里发现列表被切片（例如 tools_list = tools_list[:100]），请删除该行代码。
# 确保写入 JSON 的是完整的 tools_list。

# 写入 tools.json
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    # 确保写入的是完整的 tools_list
    json.dump(tools_list, f, indent=4, ensure_ascii=False)

print(f"成功将 {len(tools_list)} 个工具写入 {OUTPUT_JSON}。")
