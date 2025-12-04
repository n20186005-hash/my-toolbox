import os
import json
import re
from pathlib import Path

# 配置路径
MODULES_DIR = 'modules'
DETAILS_DIR = 'details'
OUTPUT_JSON = 'tools.json'

# 确保详情目录存在
Path(DETAILS_DIR).mkdir(exist_ok=True)

tools_list = []
modules_path = Path(MODULES_DIR)

print("-" * 50)
print(f"--- 工具列表生成诊断开始 ---")
print("-" * 50)

# 【诊断步骤 1：检查模块目录是否存在】
if not modules_path.is_dir():
    print(f"❌ 致命错误：找不到模块目录 '{MODULES_DIR}'。脚本中止。")
    exit(1)

# 【诊断步骤 2：报告模块目录下的总条目数】
try:
    total_entries = len(list(modules_path.iterdir()))
    print(f"🔍 '{MODULES_DIR}' 根目录下总条目数（文件/文件夹）：{total_entries}")
except Exception as e:
    print(f"⚠️ 无法统计目录条目数: {e}")


print(f"开始递归扫描 {MODULES_DIR} 目录及其子目录...")
# rglob("**/*.html") 会查找 modules/ 下所有目录中的所有 .html 文件
html_files_found = list(modules_path.rglob("*.html"))
print(f"✅ 递归扫描发现的 .html 文件总数：{len(html_files_found)}")
print("-" * 50)

# 使用 pathlib.Path.rglob() 进行递归文件遍历
for filepath in html_files_found:
    # 路径相对 modules 目录，例如： 'finance/Car-Loan-Calculator.html' 或 'Car-Loan-Calculator.html'
    relative_module_path = filepath.relative_to(modules_path).as_posix()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 使用正则提取元数据
            def get_meta(name):
                match = re.search(r'<meta\s+name=[\"\']' + name + r'[\"\']\s+content=[\"\'](.*?)[\"\']', content, re.IGNORECASE)
                return match.group(1) if match else ""

            def get_title():
                match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                return match.group(1) if match else filepath.name

            # 提取数据
            # 使用 stem 获取不带扩展名的文件名作为默认 ID
            t_id = get_meta('tool-id') or filepath.stem 
            t_cat = get_meta('category') or 'other'
            t_icon = get_meta('icon') or '🔧'
            t_desc = get_meta('description') or '暂无描述'
            t_title = get_title()

            tool = {
                "id": t_id,
                "title": t_title,
                "icon": t_icon,
                "category": t_cat,
                # 存储相对于项目根目录的完整路径，例如: "modules/finance/tool.html"
                "file": filepath.as_posix(), 
                "desc": t_desc,
                "detail_page": f"details/{t_id}.html"
            }
            
            tools_list.append(tool)
            
            # --- 生成工具详情页 HTML ---
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
                        <!-- 链接使用完整的相对路径 -->
                        <a href="../{filepath.as_posix()}" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
                            Launch Tool
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 写入详情页文件
            with open(Path(DETAILS_DIR) / f"{t_id}.html", 'w', encoding='utf-8') as df:
                df.write(detail_html)
                
    except Exception as e:
        print(f"处理文件 {relative_module_path} 时发生错误: {e}")
        continue


print("-" * 50)
print(f"扫描完成。最终发现并处理了 {len(tools_list)} 个工具。")
print("-" * 50)


# 写入 tools.json
try:
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(tools_list, f, indent=4, ensure_ascii=False)
    print(f"✅ 成功将 {len(tools_list)} 个工具写入 {OUTPUT_JSON}。")

except Exception as e:
    print(f"❌ 写入 {OUTPUT_JSON} 文件时发生错误: {e}")
