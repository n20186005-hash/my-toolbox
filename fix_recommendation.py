import os

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# 1. 重写 related.js (使用绝对路径 + 增加调试日志)
def fix_related_js():
    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR)
    
    js_path = os.path.join(SCRIPTS_DIR, 'related.js')
    
    js_content = """
document.addEventListener("DOMContentLoaded", async function() {
    const container = document.getElementById('related-tools-container');
    if (!container) return;

    // 调试日志：按 F12 看 Console
    console.log("🔍 Starting related tools check...");

    try {
        // 【核心修复】使用绝对路径 /tools.json，防止路径错误
        const response = await fetch('/tools.json?t=' + Date.now());
        if (!response.ok) throw new Error("HTTP error " + response.status);
        const tools = await response.json();

        // 获取当前分类 (假设路径结构 /modules/category/tool)
        const pathSegments = window.location.pathname.split('/');
        // 过滤掉空元素
        const cleanSegments = pathSegments.filter(s => s !== '');
        
        // 通常结构: ['modules', 'category', 'tool']
        // 分类应该是倒数第二个
        let currentCategory = 'others';
        if (cleanSegments.length >= 2) {
             currentCategory = cleanSegments[cleanSegments.length - 2];
        }
        
        const currentFilename = cleanSegments[cleanSegments.length - 1];

        console.log("📂 Detected Category:", currentCategory);

        // 筛选逻辑
        const related = tools.filter(t => 
            t.category === currentCategory && 
            !t.path.endsWith(currentFilename) 
        );

        if (related.length === 0) {
            console.log("⚠️ No related tools found for category:", currentCategory);
            return;
        }

        // 随机取 6 个
        const shuffled = related.sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, 6);

        if (selected.length > 0) {
            let html = `
                <div class="mt-12 p-6 bg-gray-50 rounded-xl border border-gray-100">
                    <h3 class="text-lg font-bold text-gray-800 mb-4">🔧 You may also like in ${currentCategory.replace(/-/g, ' ')}</h3>
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            `;
            
            selected.forEach(tool => {
                let linkPath = tool.path || tool.file;
                if (!linkPath.startsWith('/') && !linkPath.startsWith('http')) linkPath = '/' + linkPath;
                
                // 保持语言参数
                const urlParams = new URLSearchParams(window.location.search);
                const lang = urlParams.get('lang');
                if(lang) {
                    const separator = linkPath.includes('?') ? '&' : '?';
                    linkPath += `${separator}lang=${lang}`;
                }

                html += `
                    <a href="${linkPath}" class="block p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-sm transition text-gray-700 text-sm font-medium truncate">
                        ${tool.title}
                    </a>
                `;
            });
            
            html += `</div></div>`;
            container.innerHTML = html;
            console.log("✅ Related tools rendered:", selected.length);
        }
    } catch (error) {
        console.error("❌ Failed to load related tools:", error);
    }
});
"""
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ [修复] related.js 已更新为绝对路径版本")

# 2. 批量修正 HTML 引用
def fix_html_references():
    print("🚀 开始修正 HTML 文件引用...")
    count = 0
    
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                if root == MODULES_DIR: continue

                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # 【核心修复】将相对引用改为绝对引用
                # 替换 ../../scripts/related.js 为 /scripts/related.js
                if 'src="../../scripts/related.js"' in content:
                    content = content.replace('src="../../scripts/related.js"', 'src="/scripts/related.js"')
                
                # 如果之前没加进去，这里强制加绝对路径版本
                if '/scripts/related.js' not in content and 'related-tools-container' in content:
                     # 可能是旧的引用方式，尝试替换
                     pass 
                
                # 确保容器存在
                if 'related-tools-container' not in content:
                     rec_code = '\n    \n    <div id="related-tools-container"></div>\n    <script src="/scripts/related.js"></script>\n'
                     if '</body>' in content:
                        content = content.replace('</body>', rec_code + '</body>')

                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  👉 已修正路径: {file}")
                    count += 1
    
    print(f"\n✅ 全部完成！共修正了 {count} 个文件。")

if __name__ == '__main__':
    fix_related_js()
    fix_html_references()