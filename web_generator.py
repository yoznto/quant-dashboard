import os
import json
from datetime import datetime

DB_FILE = "dashboard_data.json"
HTML_FILE = "index.html"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "global": {"title": "🌍 國際政經與環球情報", "time": "尚未更新", "data": []},
        "tw": {"title": "📊 台股大數據晨報", "time": "尚未更新", "data": []},
        "us": {"title": "🦅 美股科技巨頭晚報", "time": "尚未更新", "data": []}
    }

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate_html_dashboard(category_key, page_title, info_list):
    data = load_data()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data[category_key] = {
        "title": page_title,
        "time": now_str,
        "data": info_list
    }
    save_data(data)
    json_state = json.dumps(data, ensure_ascii=False)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QUANT ROOM - AI 量化情報戰情室</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {{ darkMode: 'class' }}
        </script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');
            body {{
                font-family: 'Noto Sans TC', 'JetBrains Mono', sans-serif;
                transition: background 0.3s ease, color 0.3s ease;
            }}
            .theme-dark {{ background: radial-gradient(circle at 50% 0%, #1a1c29 0%, #0d0e15 100%); }}
            .theme-light {{ background: radial-gradient(circle at 50% 0%, #f4f5f9 0%, #e9ecf5 100%); }}
            .pulse-light {{ animation: pulse 2s infinite; }}
            @keyframes pulse {{
                0% {{ opacity: 0.4; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }}
                70% {{ opacity: 1; box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }}
                100% {{ opacity: 0.4; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
            }}
            ::-webkit-scrollbar {{ width: 6px; }}
            ::-webkit-scrollbar-thumb {{ background-color: #4b5563; border-radius: 10px; }}
        </style>
        <script>
            const dbData = {json_state};
            
            const themes = {{
                'tw': {{ btn: 'from-green-500 to-emerald-600', border: 'border-emerald-500/30', lightBorder: 'border-emerald-500/40', text: 'text-emerald-500 dark:text-emerald-400', badge: 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border-emerald-300 dark:border-emerald-500/40' }},
                'us': {{ btn: 'from-blue-500 to-indigo-600', border: 'border-blue-500/30', lightBorder: 'border-blue-500/40', text: 'text-blue-500 dark:text-blue-400', badge: 'bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-500/40' }},
                'global': {{ btn: 'from-purple-500 to-pink-600', border: 'border-purple-500/30', lightBorder: 'border-purple-500/40', text: 'text-purple-500 dark:text-purple-400', badge: 'bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border-purple-300 dark:border-purple-500/40' }}
            }};

            let activeTabId = 'tw';

            function switchTab(tabId) {{
                activeTabId = tabId;
                document.querySelectorAll('.tab-btn').forEach(btn => {{
                    btn.className = "tab-btn px-5 py-2.5 rounded-xl font-medium transition-all duration-300 bg-gray-200/60 dark:bg-gray-800/40 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-700/50 hover:bg-gray-300/50 dark:hover:bg-gray-800/80";
                }});
                
                const currentTheme = themes[tabId];
                const activeBtn = document.getElementById('btn-' + tabId);
                activeBtn.className = `tab-btn px-6 py-2.5 rounded-xl font-bold transition-all duration-300 bg-gradient-to-r ${{currentTheme.btn}} text-white shadow-lg border-transparent`;
                
                const tabData = dbData[tabId];
                const mainPanel = document.getElementById('main-panel');
                mainPanel.className = `bg-white/80 dark:bg-gray-900/60 backdrop-blur-xl p-6 md:p-8 rounded-2xl shadow-2xl border ${{currentTheme.lightBorder}} dark:${{currentTheme.border}} transition-all duration-500`;
                
                document.getElementById('panel-title').className = `text-2xl font-bold tracking-tight bg-gradient-to-r ${{currentTheme.btn}} bg-clip-text text-transparent`;
                document.getElementById('panel-title').innerText = tabData.title + "資料來源";
                document.getElementById('panel-time').innerText = "SYSTEM UPDATE: " + tabData.time;
                
                const listContainer = document.getElementById('link-list');
                listContainer.innerHTML = "";
                
                const items = tabData.data || tabData.links || [];
                if (items.length === 0) {{
                    listContainer.innerHTML = "<p class='text-gray-400 dark:text-gray-500 italic text-center py-12 font-mono'>[NO DATA INJECTED] 等待系統定時排程抓取...</p>";
                    return;
                }}
                
                items.forEach((item, idx) => {{
                    const isDict = (typeof item === 'object' && item !== null);
                    const url = isDict ? item.url : item;
                    const desc = isDict ? item.title : "點擊鏈結前往查看原始新聞內容";
                    
                    const li = document.createElement('li');
                    li.className = "group relative p-4 bg-gray-50/50 dark:bg-gray-800/30 hover:bg-gray-100/80 dark:hover:bg-gray-800/70 rounded-xl border border-gray-200 dark:border-gray-700/30 hover:border-gray-300 dark:hover:border-gray-600/50 transition-all duration-300 shadow-sm hover:shadow-md hover:-translate-y-0.5 flex flex-col gap-2";
                    
                    li.innerHTML = `
                        <div class="text-xs font-semibold text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-800 pb-1 mb-1 tracking-wide">
                            📌 新聞摘要說明：${{desc}}
                        </div>
                        <a href="${{url}}" target="_blank" class="flex items-start">
                            <span class="font-mono text-xs font-bold px-2 py-1 rounded-md border mr-4 mt-0.5 tracking-wider transition-colors duration-300 ${{currentTheme.badge}}">
                                SRC_${{String(idx + 1).padStart(2, '0')}}
                            </span>
                            <span class="text-gray-600 dark:text-gray-300 group-hover:${{currentTheme.text}} transition-colors duration-300 text-sm font-mono break-all pr-6">
                                ${{url}}
                            </span>
                            <span class="absolute right-4 bottom-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-300 text-gray-400">
                                ↗
                            </span>
                        </a>
                    `;
                    listContainer.appendChild(li);
                }});
            }}
            
            function toggleDarkMode() {{
                const html = document.documentElement;
                const body = document.body;
                const modeText = document.getElementById('mode-text');
                
                if (html.classList.contains('dark')) {{
                    html.classList.remove('dark');
                    body.className = "theme-light text-gray-900 min-h-screen flex flex-col justify-between selection:bg-blue-500/20";
                    modeText.innerText = "切換暗黑模式 🌙";
                    localStorage.setItem('theme', 'light');
                }} else {{
                    html.classList.add('dark');
                    body.className = "theme-dark text-gray-100 min-h-screen flex flex-col justify-between selection:bg-blue-500/30 selection:text-blue-200";
                    modeText.innerText = "切換亮色模式 ☀️";
                    localStorage.setItem('theme', 'dark');
                }}
                switchTab(activeTabId);
            }}

            function toggleSidebar() {{
                const sidebar = document.getElementById('sidebar');
                const backdrop = document.getElementById('sidebar-backdrop');
                
                if (sidebar.classList.contains('-translate-x-full')) {{
                    sidebar.classList.remove('-translate-x-full');
                    backdrop.classList.remove('hidden');
                    setTimeout(() => backdrop.classList.remove('opacity-0'), 10);
                }} else {{
                    sidebar.classList.add('-translate-x-full');
                    backdrop.classList.add('opacity-0');
                    setTimeout(() => backdrop.classList.add('hidden'), 300);
                }}
            }}

            window.onload = () => {{
                const savedTheme = localStorage.getItem('theme') || 'dark';
                if (savedTheme === 'dark') {{
                    document.documentElement.classList.add('dark');
                    document.body.className = "theme-dark text-gray-100 min-h-screen flex flex-col justify-between selection:bg-blue-500/30 selection:text-blue-200";
                    document.getElementById('mode-text').innerText = "切換亮色模式 ☀️";
                }} else {{
                    document.documentElement.classList.remove('dark');
                    document.body.className = "theme-light text-gray-900 min-h-screen flex flex-col justify-between selection:bg-blue-500/20";
                    document.getElementById('mode-text').innerText = "切換暗黑模式 🌙";
                }}
                switchTab('tw');
            }};
        </script>
    </head>
    <body class="min-h-screen flex flex-col justify-between">
        
        <div id="sidebar-backdrop" onclick="toggleSidebar()" class="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-40 hidden transition-opacity duration-300 opacity-0"></div>

        <aside id="sidebar" class="fixed top-0 left-0 h-full w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 z-50 transform -translate-x-full transition-transform duration-300 shadow-2xl flex flex-col">
            <div class="p-6 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
                <h2 class="text-xl font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-600 font-mono">QUANT_MENU</h2>
                <button onclick="toggleSidebar()" class="text-gray-500 hover:text-red-500 transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
            <nav class="flex-1 p-4 space-y-3 overflow-y-auto">
                <p class="text-xs font-mono text-gray-400 dark:text-gray-500 uppercase tracking-widest pl-2 mb-2">Platform Modules</p>
                <a href="#" class="flex items-center px-4 py-3 rounded-xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-bold border border-blue-200 dark:border-blue-800/50 shadow-sm relative overflow-hidden group">
                    <span class="relative">📊 新聞情報中心</span>
                </a>
                <a href="#" onclick="alert('產業鏈查詢系統即將上線！準備實作中... 🚀'); toggleSidebar();" class="flex items-center justify-between px-4 py-3 rounded-xl text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800/60 font-medium transition-colors border border-transparent">
                    <span>🔗 產業鏈查詢</span>
                    <span class="text-[10px] bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 px-2 py-0.5 rounded-full font-mono">SOON</span>
                </a>
            </nav>
            <div class="p-4 border-t border-gray-200 dark:border-gray-800 text-xs text-gray-400 font-mono text-center">System Ver 1.4<br>Local Hosted</div>
        </aside>

        <div class="w-full flex justify-between items-center px-4 md:px-6 py-3 border-b border-gray-200 dark:border-gray-800/80 bg-white/70 dark:bg-gray-900/40 backdrop-blur-md sticky top-0 z-30">
            <div class="flex items-center gap-4">
                <button onclick="toggleSidebar()" class="p-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white/80 dark:bg-gray-800/60 shadow-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition duration-200 group">
                    <svg class="w-5 h-5 group-hover:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
                <div class="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 dark:bg-emerald-950/40 border border-emerald-500/30 rounded-full text-emerald-600 dark:text-emerald-400 text-xs font-mono">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 pulse-light"></span>
                    QUANT_CORE_ALIVE
                </div>
            </div>
            
            <button onclick="toggleDarkMode()" class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white/80 dark:bg-gray-800/60 shadow-sm text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition duration-200">
                <span id="mode-text">切換亮色模式 ☀️</span>
            </button>
        </div>

        <div class="max-w-5xl mx-auto w-full p-4 md:p-8 flex-1 mt-2">
            <header class="text-center mb-8">
                <h1 class="text-3xl md:text-4xl font-extrabold tracking-wider text-gray-800 dark:text-transparent dark:bg-clip-text dark:bg-gradient-to-r dark:from-gray-100 dark:via-gray-300 dark:to-gray-500 font-mono">
                    QUANT_ROOM <span class="text-blue-500 font-light">v1.4</span>
                </h1>
                <p class="text-xs text-gray-400 dark:text-gray-500 font-mono mt-1 uppercase tracking-widest">AI-Powered Quantitative Intelligence Hub</p>
            </header>
            
            <div class="bg-blue-500/10 dark:bg-blue-950/20 backdrop-blur-md border border-blue-500/20 text-blue-700 dark:text-blue-300/90 p-4 mb-8 rounded-xl shadow-lg text-xs md:text-sm flex gap-3 items-start max-w-3xl mx-auto">
                <span class="text-base mt-0.5">💡</span>
                <div>
                    <span class="font-bold text-blue-600 dark:text-blue-400 font-mono">DEPLOYMENT_NOTICE:</span> 
                    每次 AI 推播後，GitHub 雲端部署約需 1~2 分鐘。若資訊尚未同步，請在電腦端按 <code class="bg-gray-200 dark:bg-blue-950 px-1.5 py-0.5 rounded text-blue-800 dark:text-blue-300 font-mono">Ctrl + F5</code> 強制刷新緩存。
                </div>
            </div>
            
            <nav class="flex justify-center space-x-2 md:space-x-3 mb-6">
                <button id="btn-tw" onclick="switchTab('tw')" class="tab-btn px-5 py-2.5 rounded-xl font-medium transition-all duration-300">📊 台股大數據</button>
                <button id="btn-us" onclick="switchTab('us')" class="tab-btn px-5 py-2.5 rounded-xl font-medium transition-all duration-300">🦅 美股焦點</button>
                <button id="btn-global" onclick="switchTab('global')" class="tab-btn px-5 py-2.5 rounded-xl font-medium transition-all duration-300">🌍 國際政經</button>
            </nav>
            
            <main id="main-panel" class="p-6 md:p-8 rounded-2xl shadow-2xl min-h-[450px] transition-all duration-500">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between border-b border-gray-200 dark:border-gray-800 pb-4 mb-6 gap-2">
                    <h2 id="panel-title" class="text-2xl font-bold tracking-tight">載入中...</h2>
                    <span id="panel-time" class="text-xs font-mono text-gray-400 dark:text-gray-500 uppercase tracking-wider bg-gray-100 dark:bg-gray-950/50 px-2.5 py-1 rounded-md border border-gray-200 dark:border-gray-800/80">
                        SYSTEM UPDATE: --
                    </span>
                </div>
                <ul id="link-list" class="space-y-3"></ul>
            </main>
        </div>
        
        <footer class="mt-16 mb-4 text-center text-gray-400 dark:text-gray-600 text-xs font-mono tracking-wider uppercase">
            // INTERNAL TERMINAL CLIENT // METRIC_DATA_NODE // OLLAMA_LLAMA3.1_SYSTEM
        </footer>
        
    </body>
    </html>
    """
    
    try:
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"🌐 頂級科技風儀表板升級成功！(Google翻譯極致拉伸版) -> {HTML_FILE}")
    except Exception as e:
        print(f"❌ 網頁生成失敗: {e}")