import os
import re

# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')

def fix_meta_category(file_path, folder_name, filename):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # 定义标准的 meta 标签格式
        new_meta_tag = f'<meta name="category" content="{folder_name}">'
        
        # 检查是否存在 category meta 标签 (正则匹配，忽略大小写)
        # 匹配 <meta name="category" ... > 或 <meta content="..." name="category">
        pattern = re.compile(r'<meta\s+[^>]*name=["\']category["\'][^>]*>', re.IGNORECASE)
        match = pattern.search(content)

        if match:
            # --- 情况 A: 标签存在 ---
            existing_tag = match.group(0)
            
            # 检查内容是否为空，或者是否需要强制更新
            # 这里我们提取 content="..." 的值
            content_match = re.search(r'content=["\'](.*?)["\']', existing_tag, re.IGNORECASE)
            
            if content_match:
                current_value = content_match.group(1).strip()
                # 如果内容是空的，或者是 " "，或者是 "others" 但现在在具体分类文件夹里
                if not current_value or current_value == "" or (current_value == 'others' and folder_name != 'others'):
                    # 替换旧标签为新标签
                    print(f"[修正] {folder_name}/{filename}: 发现空/旧分类 '{current_value}' -> 更新为 '{folder_name}'")
                    content = content.replace(existing_tag, new_meta_tag)
                else:
                    # 内容看起来是正常的，但如果你想强制统一，可以把这行注释解开：
                    # if current_value != folder_name:
                    #     print(f"[更新] {folder_name}/{filename}: '{current_value}' -> '{folder_name}'")
                    #     content = content.replace(existing_tag, new_meta_tag)
                    pass 
            else:
                # 有标签但没 content 属性？直接换掉
                print(f"[修复] {folder_name}/{filename}: 标签格式错误 -> 重写")
                content = content.replace(existing_tag, new_meta_tag)
                
        else:
            # --- 情况 B: 标签完全不存在 ---
            print(f"[新增] {folder_name}/{filename}: 缺少 meta category -> 添加 '{folder_name}'")
            # 插入到 <head> 标签之后
            if '<head>' in content:
                content = content.replace('<head>', f'<head>\n    {new_meta_tag}')
            elif '<HEAD>' in content:
                content = content.replace('<HEAD>', f'<HEAD>\n    {new_meta_tag}')
            else:
                print(f"⚠️ 警告: {filename} 没有 <head> 标签，跳过。")

        # 写入文件（如果有变化）
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            # 只有在 verbose 模式下才打印 "跳过"
            # print(f"[跳过] {filename} 已正常")
            pass

    except Exception as e:
        print(f"处理出错 {filename}: {e}")

def main():
    if not os.path.exists(MODULES_DIR):
        print("错误：找不到 modules 文件夹")
        return

    print("开始检查并修复 Meta Category 标签...")
    print("-" * 40)

    count_fixed = 0

    # 遍历所有文件夹
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                # 获取当前文件夹名字 (作为分类名)
                folder_name = os.path.basename(root)
                
                # 如果文件在 modules 根目录 (root == MODULES_DIR)，暂时跳过或标记为 others
                # 既然你已经整理过，文件应该都在子文件夹里
                if root == MODULES_DIR:
                    continue

                file_path = os.path.join(root, file)
                fix_meta_category(file_path, folder_name, file)
                count_fixed += 1

    print("-" * 40)
    print("检查完成！")

if __name__ == '__main__':
    main()