import os
import json
from datetime import datetime

# 小型本地資料庫，用來記住三個排程的最新狀態
DB_FILE = "dashboard_data.json"
HTML_FILE = "index.html"

def load_data():
    """讀取歷史資料庫"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 預設空的資料庫結構
    return {
        "global": {"title": "🌍 國際政經與環球情報", "time": "尚未更新", "links": []},
        "tw": {"title": "📊 台股大數據晨報", "time": "尚未更新", "links": []},
        "us": {"title": "🦅 美股科技巨頭晚報", "time": "尚未更新", "links": []}
    }

def save_data(data):
    """儲存進本地資料庫"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate_html_dashboard(category_key, page_title, links_list):
    """
    接收最新資料，更新資料庫，並生成終極版單頁網站 (SPA)
    category_key 必須是 "tw", "us", 或 "global"
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. 讀取並更新資料庫
    data = load_data()
    data[category_key] = {
        "title": page_title,
        "time": now_str,
        "links": links_list
    }
    save_data(data)
    
    # 2. 將 Python 字典轉成字串，準備注入到 HTML 裡的 JavaScript
    json_state = json.dumps(data, ensure_ascii=False)
    
    # 3. 帶有 JavaScript 分頁切換功能的 HTML 母版
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI 量化情報儀表板</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            // 接收來自 Python 的完整資料庫
            const dbData = {json_state};
            
            // 切換分頁的邏輯
            function switchTab(tabId) {{
                // 更新按鈕樣式
                document.querySelectorAll('.tab-btn').forEach(btn => {{
                    btn.classList.remove('bg-blue-600', 'text-white');
                    btn.classList.add('bg-gray-700', 'text-gray-300');
                }});
                document.getElementById('btn-' + tabId).classList.remove('bg-gray-700', 'text-gray-300');
                document.getElementById('btn-' + tabId).classList.add('bg-blue-600', 'text-white');
                
                // 渲染內容
                const tabData = dbData[tabId];
                document.getElementById('panel-title').innerText = tabData.title;
                document.getElementById('panel-time').innerText = "最後更新時間：" + tabData.time;
                
                const listContainer = document.getElementById('link-list');
                listContainer.innerHTML = "";
                
                if (tabData.links.length === 0) {{
                    listContainer.innerHTML = "<p class='text-gray-500 italic'>目前尚無資料，請等待系統排程抓取。</p>";
                    return;
                }}
                
                tabData.links.forEach((link, idx) => {{
                    const li = document.createElement('li');
                    li.className = "p-4 bg-gray-800 rounded-lg hover:bg-gray-700 transition duration-200";
                    li.innerHTML = `
                        <a href="${{link}}" target="_blank" class="text-blue-400 hover:text-blue-300 break-all flex items-start">
                            <span class="bg-blue-900 text-blue-200 text-xs font-bold px-2 py-1 rounded mr-3 mt-0.5">${{idx + 1}}</span>
                            <span>${{link}}</span>
                        </a>
                    `;
                    listContainer.appendChild(li);
                }});
            }}
            
            // 網頁載入後，預設顯示台股分頁
            window.onload = () => switchTab('tw');
        </script>
    </head>
    <body class="bg-gray-900 text-gray-100 font-sans antialiased p-6 md:p-12 min-h-screen">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold text-white mb-6 text-center shadow-sm">🚀 AI 量化情報戰情室</h1>
            
            <div class="flex justify-center space-x-2 md:space-x-4 mb-8">
                <button id="btn-global" onclick="switchTab('global')" class="tab-btn px-4 py-2 rounded-lg font-semibold transition bg-gray-700 text-gray-300 hover:bg-gray-600">🌍 國際政經</button>
                <button id="btn-tw" onclick="switchTab('tw')" class="tab-btn px-4 py-2 rounded-lg font-semibold transition bg-gray-700 text-gray-300 hover:bg-gray-600">📊 台股大數據</button>
                <button id="btn-us" onclick="switchTab('us')" class="tab-btn px-4 py-2 rounded-lg font-semibold transition bg-gray-700 text-gray-300 hover:bg-gray-600">🦅 美股焦點</button>
            </div>
            
            <div class="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700 min-h-[400px]">
                <h2 id="panel-title" class="text-2xl font-bold mb-2 text-white">載入中...</h2>
                <p id="panel-time" class="text-gray-400 mb-6 border-b border-gray-600 pb-4 text-sm">最後更新時間：載入中...</p>
                
                <ul id="link-list" class="space-y-3">
                    </ul>
            </div>
            
            <footer class="mt-12 text-center text-gray-500 text-sm">
                Powered by Python, Llama 3.1 & Tailwind CSS
            </footer>
        </div>
    </body>
    </html>
    """
    
    # 4. 寫入統一的 index.html
    try:
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"🌐 統一儀表板生成成功！(更新了 {category_key} 分頁)，已儲存為 {HTML_FILE}")
    except Exception as e:
        print(f"❌ 網頁生成失敗: {e}")