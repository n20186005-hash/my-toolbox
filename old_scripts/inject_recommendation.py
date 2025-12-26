import os

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# 1. 确保 scripts/related.js 存在
def ensure_related_js():
    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR)
    
    js_path = os.path.join(SCRIPTS_DIR, 'related.js')
    
    js_content = """
document.addEventListener("DOMContentLoaded", async function() {
    const container = document.getElementById('related-tools-container');
    if (!container) return;

    try {
        // Fetch tools data (path adjusted for modules/category/tool.html)
        const response = await fetch('../../tools.json');
        const tools = await response.json();

        // Detect current category from URL
        const pathSegments = window.location.pathname.split('/');
        // Assuming structure: /modules/category/tool.html
        // Last segment is file, second to last is category
        let currentCategory = pathSegments[pathSegments.length - 2];
        const currentFilename = pathSegments[pathSegments.length - 1];

        // Filter related tools
        const related = tools.filter(t => 
            t.category === currentCategory && 
            !t.path.endsWith(currentFilename) 
        );

        // Shuffle and pick 6
        const shuffled = related.sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, 6);

        if (selected.length > 0) {
            let html = `
                <div class="mt-12 p-6 bg-gray-50 rounded-xl border border-gray-100">
                    <h3 class="text-lg font-bold text-gray-800 mb-4">🔧 You may also like in ${currentCategory.replace(/-/g, ' ')}</h3>
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            `;
            
            selected.forEach(tool => {
                let linkPath = tool.path;
                // Fix path if it doesn't start with /
                if (!linkPath.startsWith('/')) linkPath = '/' + linkPath;
                
                // Keep current language param
                const urlParams = new URLSearchParams(window.location.search);
                const lang = urlParams.get('lang');
                if(lang) linkPath += `?lang=${lang}`;

                html += `
                    <a href="${linkPath}" class="block p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-sm transition text-gray-700 text-sm font-medium truncate">
                        ${tool.title}
                    </a>
                `;
            });
            
            html += `</div></div>`;
            container.innerHTML = html;
        }
    } catch (error) {
        console.error("Failed to load related tools:", error);
    }
});
"""
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ [检查] related.js 已确保存在于 {js_path}")

# 2. 植入 HTML 代码
def process_html_files():
    print("🚀 开始批量植入推荐代码...")
    count = 0
    
    for root, dirs, files in os.walk(MODULES_DIR):
        for file in files:
            if file.endswith('.html'):
                # 跳过 modules 根目录下的文件（如果有的话），只处理子文件夹里的
                if root == MODULES_DIR:
                    continue

                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                # A. 修复 CSS/JS 相对路径 (../ -> ../../)
                # 只有当还没有变成 ../../ 时才修复，防止重复运行
                if '../../scripts' not in content and '../../details' not in content:
                    content = content.replace('href="../', 'href="../../')
                    content = content.replace('src="../', 'src="../../')
                
                # B. 植入推荐容器和脚本引用
                rec_code = '\n    \n    <div id="related-tools-container"></div>\n    <script src="../../scripts/related.js"></script>\n'
                
                if 'related-tools-container' not in content:
                    # 尝试插入到 </body> 之前
                    if '</body>' in content:
                        content = content.replace('</body>', rec_code + '</body>')
                    else:
                        # 如果没有 body 标签，这就很尴尬，直接追加在最后
                        content += rec_code

                # C. 保存修改
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  👉 已更新: {file}")
                    count += 1
    
    print(f"\n✅ 全部完成！共修改了 {count} 个文件。")

if __name__ == '__main__':
    ensure_related_js()
    process_html_files()