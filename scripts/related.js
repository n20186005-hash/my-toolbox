document.addEventListener("DOMContentLoaded", async function() {
    const container = document.getElementById('related-tools-container');
    if (!container) return; // 如果页面没有放容器就不执行

    try {
        // 1. 获取 tools.json 数据 (注意路径：因为我们在 modules/cat/ 下，所以是 ../../tools.json)
        const response = await fetch('../../tools.json');
        const tools = await response.json();

        // 2. 识别当前页面属于哪个分类
        // URL 结构通常是: .../modules/category/tool.html
        const pathSegments = window.location.pathname.split('/');
        // 兼容本地开发和生产环境，取倒数第二个片段作为分类名
        let currentCategory = pathSegments[pathSegments.length - 2];
        const currentFilename = pathSegments[pathSegments.length - 1];

        // 3. 筛选同类工具（排除当前这个）
        const related = tools.filter(t => 
            t.category === currentCategory && 
            !t.path.endsWith(currentFilename) 
        );

        // 4. 随机打乱并取前 5 个
        const shuffled = related.sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, 5);

        // 5. 生成 HTML
        if (selected.length > 0) {
            let html = `
                <div class="related-section" style="margin-top: 50px; padding: 20px; background: #f9f9f9; border-radius: 8px;">
                    <h3>🔧 You may also like in ${currentCategory.replace(/-/g, ' ')}:</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
            `;
            
            selected.forEach(tool => {
                // path 格式是 modules/cat/tool.html，我们需要相对路径链接
                // 当前在 modules/cat/，所以链接只需要 tool.html 名字吗？
                // 不，tools.json 里的 path 是全路径。我们需要处理一下跳转。
                // 最稳妥是用根路径 /modules/...
                const linkPath = '/' + tool.path; 
                html += `
                    <a href="${linkPath}" style="text-decoration: none; color: #333; background: white; padding: 8px 15px; border: 1px solid #ddd; border-radius: 20px; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
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