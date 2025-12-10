import os

# ================= 配置区域 =================
ROOT_DIR = '.'  # 脚本扫描的目录
TARGET_TAG = '</body>'

# 1. 同类工具推荐代码 (检查标记: related-tools-container)
RELATED_CODE = """
    <div id="related-tools-container"></div>
    <script src="/scripts/related.js"></script>
"""

# 2. SEO 文案容器代码 (检查标记: toolbox-seo-wrapper-unique-id)
SEO_CODE = """
    <div id="toolbox-seo-wrapper-unique-id" class="max-w-4xl mx-auto px-4"></div>
    <script src="/scripts/seo-loader.js"></script>
"""
# ===========================================

def batch_update_html():
    updated_count = 0
    skip_count = 0
    error_count = 0

    print("🚀 开始智能扫描并更新 HTML 文件...")

    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.lower().endswith(".html"):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 这里的逻辑是：构建需要插入到 </body> 前面的字符串
                    insertion_buffer = ""
                    is_modified = False

                    # 1. 检查是否缺 "相关推荐"
                    if "related-tools-container" not in content:
                        insertion_buffer += RELATED_CODE
                        is_modified = True
                    
                    # 2. 检查是否缺 "SEO内容"
                    if "toolbox-seo-wrapper-unique-id" not in content:
                        insertion_buffer += SEO_CODE
                        is_modified = True

                    # 如果没有需要修改的，就跳过
                    if not is_modified:
                        # print(f"[跳过] 无需更新: {file}") #以此减少刷屏
                        skip_count += 1
                        continue

                    # 3. 检查是否有 </body> 标签可以替换
                    if TARGET_TAG not in content:
                        print(f"[警告] 文件缺少 </body> 标签，跳过: {file_path}")
                        error_count += 1
                        continue

                    # 4. 执行替换：把 </body> 替换成 (新增代码 + </body>)
                    # 这样新增代码就在 body 结束前了
                    new_content = content.replace(TARGET_TAG, insertion_buffer + "\n" + TARGET_TAG)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"[成功] 更新了: {file}")
                    updated_count += 1

                except Exception as e:
                    print(f"[错误] 读取/写入失败 {file_path}: {e}")
                    error_count += 1

    print("-" * 30)
    print(f"🎉 处理完成！")
    print(f"✅ 成功更新文件: {updated_count}")
    print(f"⏭️ 跳过(已存在): {skip_count}")
    print(f"❌ 错误/异常: {error_count}")

if __name__ == "__main__":
    print("此脚本将自动检测并补充 '相关推荐' 和 'SEO容器' 代码。")
    print("⚠️  请确保已备份网站文件！")
    confirm = input("输入 'y' 开始执行，其他键退出: ")
    if confirm.lower() == 'y':
        batch_update_html()
    else:
        print("操作已取消。")