const RelatedTools = {
    init: async function() {
        const container = document.getElementById('related-tools-container');
        if (!container) return;

        // 1. 获取当前页面的分类
        const metaCat = document.querySelector('meta[name="category"]');
        if (!metaCat) {
            console.warn('ToolboxPro: No <meta name="category"> tag found.');
            return;
        }
        const currentCategory = metaCat.content.trim();

        // 2. 加载 tools.json
        try {
            // 假设 tools.json 在网站根目录，添加时间戳防止缓存
            const response = await fetch('/tools.json?t=' + Date.now()); 
            if (!response.ok) throw new Error('Failed to load tools list');
            const tools = await response.json();

            // 3. 筛选相关工具
            const currentPath = window.location.pathname;
            const currentFilename = currentPath.substring(currentPath.lastIndexOf('/') + 1);

            const related = tools.filter(tool => {
                // 忽略大小写比较分类
                const isSameCat = tool.category && (tool.category.toLowerCase() === currentCategory.toLowerCase());
                
                // 排除当前页面 (检查文件名是否包含)
                const isNotSelf = !tool.file.includes(currentFilename);
                
                return isSameCat && isNotSelf;
            });

            if (related.length === 0) return;

            // 4. 随机打乱并取前4个 (如果不需要随机，可以删掉 sort 行)
            const displayTools = related.sort(() => 0.5 - Math.random()).slice(0, 4);

            // 5. 渲染 HTML
            this.render(container, displayTools, currentCategory);

        } catch (error) {
            console.error('ToolboxPro Error:', error);
        }
    },

    render: function(container, tools, categoryName) {
        // 获取当前语言参数
        const urlParams = new URLSearchParams(window.location.search);
        const currentLang = urlParams.get('lang') || 'en';

        // 简单的国际化标题映射
        const titles = {
            'en': 'Related Tools',
            'zh-CN': '相关工具推荐',
            'zh-TW': '相關工具推薦',
            'ja': '関連ツール',
            'ru': 'Похожие инструменты'
        };
        const sectionTitle = titles[currentLang] || titles['en'];

        // 生成卡片 HTML
        const cardsHtml = tools.map(tool => {
            // 处理链接，保留语言参数
            let link = '/' + tool.file.replace(/^\//, ''); // 确保以 / 开头
            if (currentLang !== 'en') {
                link += (link.includes('?') ? '&' : '?') + `lang=${currentLang}`;
            }

            // 图标 fallback
            const icon = tool.icon || '🔧';

            return `
                <a href="${link}" class="group block bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg hover:border-green-500 transition-all duration-200">
                    <div class="flex items-start space-x-3">
                        <div class="text-3xl bg-gray-50 rounded-md p-2 group-hover:bg-green-50 transition-colors">
                            ${icon}
                        </div>
                        <div class="flex-1 min-w-0">
                            <h4 class="font-bold text-gray-800 text-sm truncate group-hover:text-green-600 transition-colors">
                                ${tool.title}
                            </h4>
                            <p class="text-xs text-gray-500 mt-1 line-clamp-2 h-8">
                                ${tool.desc || tool.title}
                            </p>
                        </div>
                    </div>
                </a>
            `;
        }).join('');

        // 注入到容器
        container.innerHTML = `
            <div class="mt-12 pt-8 border-t border-gray-200">
                <h3 class="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                    <span>💡</span> ${sectionTitle} 
                    <span class="text-sm font-normal text-gray-400 ml-2">(${categoryName})</span>
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    ${cardsHtml}
                </div>
            </div>
        `;
    }
};

// 页面加载完成后自动执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => RelatedTools.init());
} else {
    RelatedTools.init();
}