document.addEventListener('DOMContentLoaded', async () => {
    // 1. 自动生成面包屑
    initBreadcrumb();
    
    // 2. 自动加载 SEO 数据
    loadSeoData();
});

function initBreadcrumb() {
    // 找到面包屑容器，如果没有就创建一个插在 tool-module 开头
    let nav = document.getElementById('breadcrumb-nav');
    if (!nav) {
        const moduleDiv = document.querySelector('.tool-module');
        if (moduleDiv) {
            nav = document.createElement('nav');
            nav.id = 'breadcrumb-nav';
            nav.className = 'breadcrumb text-sm text-gray-500 mb-4 flex items-center';
            moduleDiv.insertBefore(nav, moduleDiv.firstChild);
        } else {
            return; // 找不到挂载点
        }
    }

    // 获取分类和标题
    const categoryMeta = document.querySelector('meta[name="category"]');
    const category = categoryMeta ? categoryMeta.content : 'Tools';
    
    // 尝试获取标题，去掉图标
    const h2 = document.querySelector('h2');
    const title = h2 ? h2.innerText.replace(/^[^\w\u4e00-\u9fa5]+/, '').trim() : 'Current Tool';

    nav.innerHTML = `
        <a href="/" class="text-green-600 hover:underline">Home</a> 
        <span class="mx-2">/</span> 
        <span class="text-gray-500">${category}</span> 
        <span class="mx-2">/</span> 
        <span class="text-gray-800 font-medium">${title}</span>
    `;
}

async function loadSeoData() {
    // 获取工具 ID (文件名)
    let toolId = document.querySelector('meta[name="tool-id"]')?.content;
    
    // 如果 HTML 里没写 meta tool-id，尝试从 URL 获取 (备用方案)
    if (!toolId) {
        const path = window.location.pathname;
        const filename = path.substring(path.lastIndexOf('/') + 1);
        toolId = filename.replace('.html', '');
    }

    // 找到 SEO 容器，如果没有就创建一个插在 body 底部
    let container = document.getElementById('toolbox-seo-wrapper-unique-id');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toolbox-seo-wrapper-unique-id';
        container.className = 'seo-content mt-10 pt-6 border-t border-green-50 text-gray-700';
        // 插在 .tool-module 内部的最后面
        const moduleDiv = document.querySelector('.tool-module');
        if (moduleDiv) moduleDiv.appendChild(container);
    }

    if (!toolId) return;

    try {
        const response = await fetch('/seo-data.json');
        if (!response.ok) return;
        
        const allData = await response.json();
        const data = allData[toolId];

        if (data) {
            let html = `
                <h2 class="text-2xl font-bold text-green-800 mb-4">${data.title || data.seo_title || 'Tool Info'}</h2>
                <p class="mb-4 leading-relaxed">${data.description || data.intro || data.introduction || ''}</p>
            `;

            // 渲染 Steps
            if (data.steps && data.steps.length > 0) {
                html += `<h3 class="text-xl font-semibold text-green-700 mt-6 mb-3">How to Use</h3><ul class="list-disc pl-5 space-y-2 mb-6">`;
                data.steps.forEach(step => html += `<li>${step}</li>`);
                html += `</ul>`;
            }

            // 渲染 FAQ
            const faqs = data.faqs || data.faq || [];
            if (faqs.length > 0) {
                html += `<h3 class="text-xl font-semibold text-green-700 mt-6 mb-3">FAQ</h3>`;
                faqs.forEach(f => {
                    html += `<div class="mb-4 border-l-4 border-green-200 pl-4">
                        <div class="font-bold text-green-800 mb-1">${f.question || f.q}</div>
                        <div class="text-gray-600">${f.answer || f.a}</div>
                    </div>`;
                });
            }
            container.innerHTML = html;
        }
    } catch (e) {
        console.error('SEO Auto-load failed', e);
    }
}