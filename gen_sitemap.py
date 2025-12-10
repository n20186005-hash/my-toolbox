import os
import datetime

# 配置
# ⚠️ 这里一定要填你真实的域名，不要带最后的斜杠
SITE_DOMAIN = "https://toolboxpro.top"
MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
OUTPUT_FILE = 'sitemap.xml'

def generate_sitemap():
    if not os.path.exists(MODULES_DIR):
        print("错误：找不到 modules 文件夹")
        return

    urls = []
    
    # 1. 添加首页
    urls.append({
        "loc": f"{SITE_DOMAIN}/",
        "lastmod": datetime.date.today().isoformat(),
        "priority": "1.0"
    })

    # 2. 遍历所有工具
    print("正在扫描文件...")
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                # 获取相对路径 (例如: finance/401k-calculator.html)
                # 我们要把 Windows 的反斜杠 \ 换成 URL 的正斜杠 /
                rel_path = os.path.relpath(os.path.join(root, file), MODULES_DIR).replace('\\', '/')
                
                # 拼接完整 URL
                full_url = f"{SITE_DOMAIN}/modules/{rel_path}"
                
                urls.append({
                    "loc": full_url,
                    "lastmod": datetime.date.today().isoformat(),
                    "priority": "0.8"
                })

    # 3. 生成 XML 内容
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for url in urls:
        xml_content.append('  <url>')
        xml_content.append(f'    <loc>{url["loc"]}</loc>')
        xml_content.append(f'    <lastmod>{url["lastmod"]}</lastmod>')
        xml_content.append(f'    <priority>{url["priority"]}</priority>')
        xml_content.append('  </url>')
    
    xml_content.append('</urlset>')

    # 4. 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_content))
    
    print(f"成功生成 {OUTPUT_FILE}！包含 {len(urls)} 个链接。")

if __name__ == '__main__':
    generate_sitemap()