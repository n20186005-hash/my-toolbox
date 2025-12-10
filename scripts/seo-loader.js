/**
 * Toolbox Pro SEO Content Loader (v2.0)
 * 新增功能：自动生成面包屑导航 (Breadcrumbs)
 */
(function() {
    const CONFIG = {
        containerId: 'toolbox-seo-wrapper-unique-id',
        jsonPath: '/seo-data.json'
    };

    const SeoLoader = {
        init: async function() {
            const container = document.getElementById(CONFIG.containerId);
            if (!container) return;

            // 1. 获取 Tool ID
            let toolId = container.dataset.toolId;
            if (!toolId) {
                const mainTool = document.getElementById('main-tool-container');
                if (mainTool) toolId = mainTool.getAttribute('data-id');
            }
            if (!toolId) {
                const path = window.location.pathname;
                toolId = path.substring(path.lastIndexOf('/') + 1).replace('.html', '');
            }

            if (!toolId) return;

            // 2. 加载数据
            try {
                const res = await fetch(CONFIG.jsonPath + '?v=' + new Date().getDate());
                if (!res.ok) return;
                
                const allData = await res.json();
                const toolData = allData[toolId];

                if (toolData) {
                    // ★ 获取当前页面分类 (为了面包屑)
                    const metaCat = document.querySelector('meta[name="category"]');
                    const category = metaCat ? metaCat.content : 'Tools';
                    
                    // 渲染内容 (带面包屑)
                    this.render(container, toolData, category);
                    this.injectSchema(toolData);
                    
                    if (toolData.title) {
                        document.title = `${toolData.title} | Toolbox Pro`;
                    }
                }
            } catch (e) {
                console.warn('SEO Content Load Skipped:', e);
            }
        },

        render: function(target, data, category) {
            // ★ 面包屑导航 HTML
            const breadcrumbHtml = `
                <nav class="flex text-sm text-gray-500 mb-6" aria-label="Breadcrumb">
                    <ol class="inline-flex items-center space-x-1 md:space-x-3">
                        <li class="inline-flex items-center">
                            <a href="/" class="hover:text-blue-600 flex items-center gap-1">
                                🏠 Home
                            </a>
                        </li>
                        <li>
                            <div class="flex items-center">
                                <span class="mx-2 text-gray-400">/</span>
                                <span class="capitalize hover:text-blue-600 cursor-default">${category}</span>
                            </div>
                        </li>
                        <li aria-current="page">
                            <div class="flex items-center">
                                <span class="mx-2 text-gray-400">/</span>
                                <span class="text-gray-400 truncate max-w-[150px] sm:max-w-xs">${data.title}</span>
                            </div>
                        </li>
                    </ol>
                </nav>
            `;

            let html = `
                <div class="mt-12 p-6 bg-white rounded-xl border border-gray-100 shadow-sm text-gray-700 font-sans">
                    ${breadcrumbHtml} <h2 class="text-2xl font-bold mb-4 text-gray-800">${data.title || 'About This Tool'}</h2>
                    <div class="prose max-w-none mb-8 text-sm leading-relaxed text-gray-600">
                        ${data.intro || ''}
                    </div>
            `;

            if (data.steps && data.steps.length) {
                html += `
                    <h3 class="text-lg font-bold mb-3 text-gray-800">How to Use</h3>
                    <ol class="list-decimal list-inside space-y-2 mb-8 bg-gray-50 p-4 rounded-lg text-sm">
                        ${data.steps.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                `;
            }

            if (data.faq && data.faq.length) {
                html += `<h3 class="text-lg font-bold mb-3 text-gray-800">FAQ</h3><div class="space-y-3">`;
                data.faq.forEach(item => {
                    html += `
                        <details class="group bg-gray-50 rounded-lg">
                            <summary class="cursor-pointer p-3 font-medium text-gray-800 hover:bg-gray-100 rounded-lg transition list-none flex justify-between items-center text-sm">
                                <span>${item.q}</span>
                                <span class="text-gray-400 group-open:rotate-180 transition">▼</span>
                            </summary>
                            <div class="px-3 pb-3 text-sm text-gray-600 mt-1 pl-4 border-l-2 border-green-500 ml-3 mb-2">${item.a}</div>
                        </details>
                    `;
                });
                html += `</div>`;
            }

            html += `</div>`;
            target.innerHTML = html;
        },

        injectSchema: function(data) {
            // ... Schema 代码保持不变 ...
            const script = document.createElement('script');
            script.type = 'application/ld+json';
            script.text = JSON.stringify({
                "@context": "https://schema.org",
                "@type": "WebApplication",
                "name": data.title,
                "description": (data.intro || "").substring(0, 150),
                "url": window.location.href,
                "applicationCategory": "UtilityApplication",
                "operatingSystem": "All",
                "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" }
            });
            document.head.appendChild(script);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => SeoLoader.init());
    } else {
        SeoLoader.init();
    }
})();