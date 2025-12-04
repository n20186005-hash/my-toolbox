import os
import re

MODULES_DIR = 'modules'
TAG_TEMPLATE = """
    <meta name="tool-id" content="{id}">
    <meta name="category" content="{category}">
    <meta name="icon" content="{icon}">
    <meta name="description" content="{description}">
"""

# 定义默认描述（如果找不到更详细的描述）
DEFAULT_DESC = "这是一个非常有用的在线工具。"

print(f"--- 开始扫描 {MODULES_DIR} 目录，批量添加元数据 ---")

for filename in os.listdir(MODULES_DIR):
    if filename.endswith(".html"):
        filepath = os.path.join(MODULES_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 检查文件是否已经添加过标签
        if 'ADDITION_MARKER_V1' in content:
             print(f"跳过: {filename} (已处理)")
             continue
        if '<meta name="tool-id"' in content:
             print(f"跳过: {filename} (已存在 tool-id)")
             continue

        # 2. 从 tool-module div 中提取数据 (这是文件里已有的信息)
        # 例如: <div ... data-id="age_calc" data-category="date" data-icon="🎂">
        match = re.search(r'<div[^>]*tool-module[^>]*data-id="([^"]*)"[^>]*data-category="([^"]*)"[^>]*data-icon="([^"]*)"[^>]*data-title="([^"]*)"', content, re.IGNORECASE | re.DOTALL)
        
        if not match:
            print(f"❌ 警告: {filename} 找不到 data-id/category/icon，跳过!")
            continue

        tool_id = match.group(1)
        category = match.group(2)
        icon = match.group(3)
        title = match.group(4)

        # 3. 构造要插入的标签
        tags_to_insert = TAG_TEMPLATE.format(
            id=tool_id,
            category=category,
            icon=icon,
            description=f"{title}: {DEFAULT_DESC}"
        )

        # 4. 插入到 </head> 之前
        new_content = content.replace('</head>', tags_to_insert + '\n\n</head>', 1)
        
        # 5. 写回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ 成功: {filename} 已添加标签 (ID: {tool_id}, Cat: {category})")

print("--- 批量处理完成 ---")
