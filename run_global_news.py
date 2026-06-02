import requests
from bs4 import BeautifulSoup
import ollama
import time
from datetime import datetime
import concurrent.futures
from web_generator import generate_html_dashboard

# 👉 你的專屬 Discord Webhook
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510814929186324550/foMi7Kqoc7q2gILVYg5-qo-g9dCBjrwnUrzffTIk1V6Bd8yvCqNH6rGFoYfVE3M_jAig"

def send_to_discord(message):
    if not DISCORD_WEBHOOK_URL: return
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        final_content = f"**🌍 今日國際政經與環球晨報 ({now_str}) 🌍**\n\n{message}\n\n"
        final_content += "🌐 **查看詳細情報來源**：\n👉 https://yoznto.github.io/quant-dashboard/\n"
        final_content += "*(💡 溫馨提醒：雲端網頁同步約需 1~2 分鐘，若未看到最新資料請稍後重整)*"
        
        data = {"content": final_content}
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print(f"✅ 成功推送到 Discord！")
    except Exception as e:
        print(f"❌ 推送失敗: {e}")

def fetch_single_article(link):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(link, headers=headers, timeout=5)
        s = BeautifulSoup(res.text, 'html.parser')
        title = s.find('h1').text.strip() if s.find('h1') else ""
        body = s.find('div', class_='caas-body')
        content = body.text.strip()[:100] if body else "" 
        if title and len(title) > 5: return f"【標題】{title}\n【內文重點】{content}...\n"
        return None
    except:
        return None

def get_huge_global_news(target_limit=30):
    print("1. 正在從 Yahoo 國際股市專區取得文章列表與摘要...")
    url = "https://tw.stock.yahoo.com/intl-markets/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        info_list = []
        seen_urls = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/news/' in href:
                full_url = f"https://tw.stock.yahoo.com{href}" if not href.startswith('http') else href
                clean_url = full_url.split('?')[0]
                
                if clean_url not in seen_urls:
                    seen_urls.add(clean_url)
                    
                    title_text = a_tag.text.strip() if a_tag.text else "查看原始新聞"
                    if len(title_text) < 5:
                        title_text = "國際政經財經線索"
                        
                    info_list.append({
                        "url": clean_url,
                        "title": title_text
                    })
                    
                if len(info_list) >= target_limit: break
                        
        news_data_pool = []
        just_urls = [item["url"] for item in info_list]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_single_article, just_urls)
            for res in results:
                if res: news_data_pool.append(res)
                
        print(f"✅ 國際情報抓取完畢！共 {len(news_data_pool)} 篇。")
        return "\n".join(news_data_pool), info_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return "", []

if __name__ == "__main__":
    raw_news_pool, info_list = get_huge_global_news(target_limit=25)
    if not raw_news_pool: exit()
        
    # 🚀 1. 儲存原始新聞清單 (Tab 3: 🌍 國際政經資料來源)
    generate_html_dashboard("global", "🌍 國際政經與環球情報", info_list)
    
    print(f"2. 【國際資料庫建立完成】正在將海量原始資料丟給 Llama 3.1 分析...\n")
    system_prompt = "你是一個專注於地緣政治與非美市場的宏觀經濟學家。請用極度客觀的語氣陳述國際事實。"
    
    # 🎯 格式對齊優化：強迫 Llama 3.1 使用規範錨點，確保前端 switchAiTab('global') 100% 精準橫向切欄
    user_prompt = f"""
    分析以下國際新聞（不含純美股）：
    {raw_news_pool}
    
    【⚠️ 鋼鐵紀律】：
    1. 絕對不准捏造大盤點位、匯率或數字！
    2. 必須嚴格按照以下指定標題格式輸出，不准自行添加任何表情符號，以便系統進行網頁橫向三欄切片。
    3. 嚴禁廢話。
    
    市場事實如下：
    1. [亞洲市場 facts：中、日、韓等重要市場數據或政策變動事實]
    2. [歐洲與地緣 facts：歐洲央行動態、歐盟政策或地緣衝突事件客觀現狀]
    3. [原物料與匯率 facts：原油、黃金大宗商品或重要外匯走勢 facts]
    
    **今日市場焦點**
    • [避險資產氛圍]：(分析地緣衝突下拉動的黃金、原油避險资金情緒)
    • [國際資金流向]：(分析非美市場政策大環境對全球資金分配的最新影響)
    
    **操盤策略與投資建議**
    • ⚖️ 宏觀風險提示：(給出一句關於國際局勢對供應鏈、外匯劇烈震盪或全球資金套牢的避險警告)
    • 💰 避險防禦方針：(給出宏觀資產配置、防禦型板塊避險或商品操作的具體方向建議)
    """
    
    final_response = ollama.chat(
        model='llama3.1', 
        messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}],
        options={'temperature': 0, 'num_ctx': 8192} 
    )
    final_report = final_response['message']['content'].strip()
    
    print("="*60 + f"\n{final_report}\n" + "="*60)
    
    # 🚀 2. 推送 Discord 頻道
    send_to_discord(final_report)
    
    # 🚀 3. 同步回流到網頁快取槽 (對齊網頁 v1.5.1 的 Tab 4 獨立國際政經子區塊)
    generate_html_dashboard("ai_news_global", "🌍 國際政經 AI 核心戰略", final_report)