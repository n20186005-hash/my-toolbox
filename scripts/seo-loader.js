document.addEventListener('DOMContentLoaded', async () => {
    // 1. 启动面包屑 (修复版)
    initBreadcrumb();
    
    // 2. 启动SEO内容加载
    loadSeoData();
});

function initBreadcrumb() {
    // 1. 找到主容器 (工具的白色卡片区域)
    const moduleDiv = document.querySelector('.tool-module');
    if (!moduleDiv) return;

    // 2. 检查是否已有面包屑
    let nav = document.getElementById('breadcrumb-nav');

    // 3. 如果没有，就创建一个
    if (!nav) {
        nav = document.createElement('nav');
        nav.id = 'breadcrumb-nav';
        // 样式：灰色小字，下边距，弹性布局
        nav.className = 'breadcrumb text-sm text-gray-500 mb-4 flex items-center'; 
    }

    // 4. 【核心修复】强制将面包屑移动到容器的最开始位置 (Prepend)
    // 无论它之前在哪里，这句话都会把它“提”到最前面
    moduleDiv.prepend(nav);

    // 5. 填充内容
    const categoryMeta = document.querySelector('meta[name="category"]');
    const category = categoryMeta ? categoryMeta.content : 'Tools';
    
    // 获取标题并去掉前面的图标（如果标题里有图标的话）
    const h2 = document.querySelector('h2');
    const title = h2 ? h2.innerText.replace(/^[^\w\u4e00-\u9fa5]+/, '').trim() : document.title;

    nav.innerHTML = `
        <a href="/" class="text-green-600 hover:underline">Home</a> 
        <span class="mx-2">/</span> 
        <span class="text-gray-500">${category}</span> 
        <span class="mx-2">/</span> 
        <span class="text-gray-800 font-medium">${title}</span>
    `;
}

async function loadSeoData() {
    let toolId = document.querySelector('meta[name="tool-id"]')?.content;
    if (!toolId) {
        const path = window.location.pathname;
        const filename = path.substring(path.lastIndexOf('/') + 1);
        toolId = filename.replace('.html', '');
    }

    // SEO内容容器 (通常放在底部)
    let container = document.getElementById('toolbox-seo-wrapper-unique-id');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toolbox-seo-wrapper-unique-id';
        container.className = 'seo-content mt-10 pt-6 border-t border-green-50 text-gray-700';
        const moduleDiv = document.querySelector('.tool-module');
        if (moduleDiv) moduleDiv.appendChild(container); // SEO内容放在末尾
    }

    if (!toolId) return;

    try {
        // 加载 JSON 数据
        const response = await fetch('/seo-data.json');
        if (!response.ok) return;
        
        const allData = await response.json();
        const data = allData[toolId];

        if (data) {
            let html = `
                <h2 class="text-2xl font-bold text-green-800 mb-4">${data.title || data.seo_title || 'Tool Info'}</h2>
                <p class="mb-4 leading-relaxed">${data.description || data.intro || data.introduction || ''}</p>
            `;

            if (data.steps && data.steps.length > 0) {
                html += `<h3 class="text-xl font-semibold text-green-700 mt-6 mb-3">How to Use</h3><ul class="list-disc pl-5 space-y-2 mb-6">`;
                data.steps.forEach(step => html += `<li>${step}</li>`);
                html += `</ul>`;
            }

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
            container.classList.remove('hidden');
        }
    } catch (e) {
        console.error('SEO Auto-load failed', e);
    }
}