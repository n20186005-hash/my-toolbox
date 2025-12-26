import json
import os
import datetime

# --- 配置区域 ---
# 你的网站域名 (注意：不要带最后的斜杠 /)
DOMAIN = "https://toolboxpro.top"
TOOLS_FILE = "tools.json"
OUTPUT_FILE = "sitemap.xml"

# XML 标准头尾
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
XML_FOOTER = '</urlset>'

def generate_sitemap():
    print("🗺️ 正在根据 tools.json 生成网站地图...")
    
    # 1. 检查 tools.json 是否存在
    if not os.path.exists(TOOLS_FILE):
        print(f"❌ 错误：找不到 {TOOLS_FILE}。请先运行 organize.py！")
        return

    # 获取今天的日期
    today = datetime.date.today().isoformat()
    
    xml_content = XML_HEADER

    # --- 2. 添加首页 (权重最高 1.0) ---
    xml_content += f"""  <url>
    <loc>{DOMAIN}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>\n"""

    # --- 3. 读取 tools.json 添加工具页 (权重 0.8) ---
    try:
        with open(TOOLS_FILE, 'r', encoding='utf-8') as f:
            tools = json.load(f)
            
        print(f"📦 发现 {len(tools)} 个工具，正在写入...")

        for tool in tools:
            # 获取路径 (例如 modules/date-time/timestamp.html)
            path = tool['path']
            
            # 确保路径开头没有斜杠，避免 https://toolboxpro.top//modules... 这种情况
            if path.startswith('/'):
                path = path[1:]
            
            # 拼接完整 URL
            full_url = f"{DOMAIN}/{path}"
            
            # 转义 URL 中的特殊字符 (比如 & 变为 &amp;)
            full_url = full_url.replace("&", "&amp;")

            xml_content += f"""  <url>
    <loc>{full_url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>\n"""

    except Exception as e:
        print(f"❌ 读取错误: {e}")
        return

    # --- 4. 结束并保存 ---
    xml_content += XML_FOOTER
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)
        
    print("-" * 30)
    print(f"✅ 成功生成: {OUTPUT_FILE}")
    print(f"✅ 共包含链接数: {len(tools) + 1}")
    print("🚀 现在，你可以 git push 提交代码了！")

if __name__ == "__main__":
    generate_sitemap()