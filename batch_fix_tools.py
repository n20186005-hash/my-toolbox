import os
import re

# 设置你的工具文件夹路径
TARGET_DIR = './modules'

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(file_path)
    tool_id = filename.replace('.html', '')
    
    modified = False

    # 1. 检查并添加 tool-id meta 标签 (为了让 JS 知道去读哪条 SEO 数据)
    if 'meta name="tool-id"' not in content:
        # 尝试插在 category meta 后面，或者 head 里面
        meta_tag = f'<meta name="tool-id" content="{tool_id}">'
        if '<meta name="category"' in content:
            content = content.replace('<meta name="category"', f'{meta_tag}\n    <meta name="category"')
            modified = True
        elif '<head>' in content:
            content = content.replace('<head>', f'<head>\n    {meta_tag}')
            modified = True
        print(f"[Meta] Added tool-id to {filename}")

    # 2. 检查并添加 seo-loader.js 引用
    script_tag = '<script src="/scripts/seo-loader.js"></script>'
    if 'seo-loader.js' not in content:
        # 插在 </body> 之前
        if '</body>' in content:
            content = content.replace('</body>', f'\n    {script_tag}\n</body>')
            modified = True
            print(f"[Script] Added script to {filename}")
    
    # 3. 保存文件 (只有修改过才保存)
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Saved: {filename}")
    else:
        print(f"Skipped (No changes): {filename}")

def main():
    print("🚀 Starting batch update for 400+ tools...")
    count = 0
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    process_file(file_path)
                    count += 1
                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")
    
    print(f"\n🎉 Finished! Processed {count} files.")

if __name__ == '__main__':
    main()