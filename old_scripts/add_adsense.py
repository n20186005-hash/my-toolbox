import os

# --- 你的 AdSense 代码 (已根据截图为你提取) ---
ADSENSE_SCRIPT = r'''
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9279583389810634"
     crossorigin="anonymous"></script>
'''

# 需要跳过不处理的文件夹 (比如 .git, scripts 等)
IGNORE_DIRS = {'.git', '.github', '__pycache__', 'scripts', 'node_modules'}

def add_ads_to_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 检查是否已经存在广告代码 (防止重复添加)
        # 我们用 client ID 来作为判断依据，比较准确
        if 'ca-pub-9279583389810634' in content:
            print(f"⏩ 跳过 (已存在): {file_path}")
            return

        # 2. 寻找插入位置
        # Google 要求代码放在 <head> 和 </head> 之间
        # 最稳妥的方法是替换 </head> 标签，把它插在 </head> 的前面
        if '</head>' in content:
            new_content = content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已添加广告: {file_path}")
        else:
            print(f"⚠️ 找不到 </head> 标签: {file_path}")

    except Exception as e:
        print(f"❌ 读取错误 {file_path}: {e}")

def main():
    print("开始全站扫描并添加 AdSense 代码...")
    count = 0
    
    # os.walk('.') 表示从当前根目录开始递归遍历所有文件夹
    for root, dirs, files in os.walk('.'):
        # 移除不需要扫描的目录，提高效率并防止改错
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                add_ads_to_html(file_path)
                count += 1
                
    print("-" * 30)
    print(f"🎉 处理完成！共扫描了 {count} 个 HTML 文件。")
    print("请记得使用 Git 提交并推送到服务器生效。")

if __name__ == '__main__':
    main()