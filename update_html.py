import os
import re

# 配置路径
MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
# 你的网站域名 (用于生成 Canonical URL)
SITE_DOMAIN = "https://toolboxpro.top"

def process_file(file_path, category, filename):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # 1. 修复相对路径 (CSS/JS/Images)
    # 逻辑：因为文件从 modules/ 移到了 modules/cat/，所有 ../ 需要变成 ../../
    # 我们查找所有 href="../" 或 src="../" 且后面不是跟随 modules 的情况
    # 注意：防止重复运行导致变成 ../../../
    if '../../' not in content: 
        content = content.replace('href="../', 'href="../../')
        content = content.replace('src="../', 'src="../../')
        content = content.replace('href="index.html"', 'href="../../index.html"') # 修复返回首页链接

    # 2. 插入 Canonical 标签 (SEO 关键)
    # 目标格式: <link rel="canonical" href="https://toolboxpro.top/modules/category/tool.html" />
    canonical_url = f"{SITE_DOMAIN}/modules/{category}/{filename}"
    canonical_tag = f'<link rel="canonical" href="{canonical_url}" />'
    
    # 检查是否已存在 canonical，不存在则插入到 </head> 前
    if 'rel="canonical"' not in content:
        content = content.replace('</head>', f'    {canonical_tag}\n</head>')

    # 3. 插入“相关推荐”容器和脚本 (Request #3)
    recommendation_html = '''
    <div id="related-tools-container"></div>
    <script src="../../scripts/related.js"></script>
    '''
    
    # 检查是否已存在 script，不存在则插入到 </body> 前
    if 'related-tools-container' not in content:
        content = content.replace('</body>', f'{recommendation_html}\n</body>')

    # 只有内容发生变化时才写入
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {category}/{filename}")
    else:
        print(f"Skipped (No changes): {category}/{filename}")

def main():
    if not os.path.exists(MODULES_DIR):
        print("Error: modules folder not found")
        return

    print("开始更新 HTML 文件路径和注入代码...")
    
    # 遍历所有子文件夹
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                # 获取分类名 (文件夹名)
                category = os.path.basename(root)
                # 只有当文件在子文件夹里时才处理 (排除 modules 根目录下的残留文件)
                if root != MODULES_DIR:
                    file_path = os.path.join(root, file)
                    process_file(file_path, category, file)

    print("-" * 30)
    print("所有文件更新完成！")
    print("1. 已修复 CSS/JS 相对路径")
    print("2. 已添加 Canonical SEO 标签")
    print("3. 已植入相关推荐模块")

if __name__ == '__main__':
    main()