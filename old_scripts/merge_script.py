import os
import re

# 定义要合并的文件列表（按执行顺序排列）
# 1. 先整理文件 (organize)
# 2. 整理完后加 SEO 索引 (canonical)
# 3. 加广告 (adsense)
# 4. 最后生成地图 (sitemap)
FILES_TO_MERGE = [
    {'name': 'organize.py', 'func_alias': 'run_task_organize'},
    {'name': 'auto_add_canonical.py', 'func_alias': 'run_task_canonical'},
    {'name': 'add_adsense.py', 'func_alias': 'run_task_adsense'},
    {'name': 'gen_sitemap.py', 'func_alias': 'run_task_sitemap'}
]

OUTPUT_FILENAME = "manage_all.py"

def merge_files():
    print("🚀 开始合并脚本...")
    
    all_imports = set()
    all_codes = []
    
    # 我们需要屏蔽的内部相互引用
    # 因为合并成一个文件后，就不需要 import 对方了
    internal_modules = {f.replace('.py', '') for f in [item['name'] for item in FILES_TO_MERGE]}

    for item in FILES_TO_MERGE:
        filename = item['name']
        alias = item['func_alias']
        
        if not os.path.exists(filename):
            print(f"❌ 错误：找不到文件 {filename}")
            return

        print(f"📖 读取: {filename} ...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        file_code = []
        is_in_main_block = False

        for line in lines:
            stripped = line.strip()

            # 1. 提取并移除 import 语句
            if stripped.startswith('import ') or stripped.startswith('from '):
                # 检查是否是导入内部模块 (比如 import auto_add_canonical)
                # 如果是内部模块，直接丢弃，不需要保留
                is_internal = False
                for module in internal_modules:
                    if f" {module}" in stripped: # 简单检查
                        is_internal = True
                        break
                
                if not is_internal:
                    all_imports.add(stripped)
                continue

            # 2. 处理 main 函数重命名
            # 将 def main(): 替换为 def run_task_xxx(): 以免冲突
            if re.match(r'^def\s+main\s*\(\s*\):', line):
                file_code.append(f"def {alias}():\n")
                continue
            
            # 3. 兼容其他特定的入口函数名
            # auto_add_canonical 用的是 process_directory
            if filename == 'auto_add_canonical.py' and 'def process_directory' in line:
                file_code.append(f"def {alias}(root_dir=None, site_domain=None): # 原 process_directory\n")
                continue
            # gen_sitemap 用的是 generate_sitemap
            if filename == 'gen_sitemap.py' and 'def generate_sitemap' in line:
                file_code.append(f"def {alias}(): # 原 generate_sitemap\n")
                continue

            # 4. 移除 if __name__ == "__main__": 块
            # 我们不需要每个文件原本的启动代码，统一在最后写
            if stripped.startswith('if __name__'):
                is_in_main_block = True
                continue
            
            # 如果在 main 块里，且有缩进，说明是 main 块的内容，跳过（或者保留逻辑但很少见）
            # 大多数脚本 main 块里只是调用 main()，所以跳过即可
            if is_in_main_block:
                if stripped == '' or line.startswith('    ') or line.startswith('\t'):
                    continue
                else:
                    is_in_main_block = False

            # 保留普通代码
            file_code.append(line)

        all_codes.append(f"\n# ==========================================\n# 来源: {filename}\n# ==========================================\n")
        all_codes.extend(file_code)

    # --- 开始写入新文件 ---
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as out:
        # 1. 写入所有去重后的 import
        out.write("# 此文件由 merge_script.py 自动生成\n")
        out.write("# 集成了 organize, canonical, adsense, sitemap 的所有功能\n\n")
        
        # 排序 import 让代码更好看
        sorted_imports = sorted(list(all_imports))
        for imp in sorted_imports:
            out.write(imp + "\n")
        
        out.write("\n")

        # 2. 写入各个文件的逻辑代码
        for code_block in all_codes:
            for line in code_block:
                out.write(line)

        # 3. 写入总控 Main 入口
        out.write("\n\n")
        out.write("# ==========================================\n")
        out.write("# 总执行入口\n")
        out.write("# ==========================================\n")
        out.write("if __name__ == '__main__':\n")
        out.write("    print('🤖 [ALL-IN-ONE] 开始执行全站维护任务...')\n\n")
        
        # 按顺序调用
        out.write("    print('\\n➡️ [1/4] 正在整理文件结构 (Organize)...')\n")
        out.write("    try:\n")
        out.write("        run_task_organize()\n")
        out.write("    except Exception as e: print(f'⚠️ Organize 错误: {e}')\n\n")

        out.write("    print('\\n➡️ [2/4] 正在检查 SEO 索引 (Canonical)...')\n")
        out.write("    try:\n")
        out.write("        # auto_add_canonical 需要参数或者默认值，这里根据别名调用\n")
        out.write("        run_task_canonical()\n")
        out.write("    except Exception as e: print(f'⚠️ SEO 错误: {e}')\n\n")

        out.write("    print('\\n➡️ [3/4] 正在添加 AdSense 广告代码...')\n")
        out.write("    try:\n")
        out.write("        run_task_adsense()\n")
        out.write("    except Exception as e: print(f'⚠️ AdSense 错误: {e}')\n\n")

        out.write("    print('\\n➡️ [4/4] 正在生成网站地图 (Sitemap)...')\n")
        out.write("    try:\n")
        out.write("        run_task_sitemap()\n")
        out.write("    except Exception as e: print(f'⚠️ Sitemap 错误: {e}')\n\n")
        
        out.write("    print('\\n🎉 所有任务执行完毕！')\n")

    print(f"✅ 成功！已生成文件: {OUTPUT_FILENAME}")
    print(f"请检查并在终端运行: python {OUTPUT_FILENAME}")

if __name__ == "__main__":
    merge_files()