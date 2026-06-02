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
        
        final_content = f"**🦅 今日美股盤前與科技巨頭晚報 ({now_str}) 🦅**\n\n{message}\n\n"
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

def get_huge_us_news(target_limit=30):
    print("1. 正在從 Yahoo 國際與美股焦點專專區取得文章列表與摘要...")
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
                        title_text = "美股財經新聞線索"
                        
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
                
        print(f"✅ 美股抓取完畢！共 {len(news_data_pool)} 篇。")
        return "\n".join(news_data_pool), info_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return "", []

if __name__ == "__main__":
    raw_news_pool, info_list = get_huge_us_news(target_limit=30)
    if not raw_news_pool: exit()
        
    # 🚀 1. 儲存原始新聞清單 (Tab 2: 🦅 美股焦點資料來源)
    generate_html_dashboard("us", "🦅 美股焦點資料來源", info_list)
    
    print(f"2. 【美股資料庫建立完成】正在將海量原始資料丟給 Llama 3.1 分析...\n")
    system_prompt = "你是一個華爾街頂級量化分析師。你的任務是從下方資料庫中，**只篩選出與美股、聯準會或美國科技巨頭相關的情報**進行分析，其餘非美地區直接忽略，嚴禁廢話。"
    
    # 🎯 格式對齊優化：強迫模型吐出精密錨點標題，以便前端 100% 解構切片並投放到三個橫向卡片
    user_prompt = f"""
    分析以下美股與華爾街新聞資料庫：
    {raw_news_pool}
    
    【⚠️ 鋼鐵紀律】：
    1. 絕對不准捏造指數或股價！
    2. 如果情報內沒有美股動態，請根據現有資料陳述華爾街事實。
    3. 嚴禁廢話。
    4. 必須嚴格按照以下指定標題格式輸出，不准自行加表情符號，以便系統進行網頁橫向三欄切片。
    
    市場事實如下：
    1. [科技巨頭動態事実：輝達、蘋果等科技股具體事實]
    2. [聯準會與總經事實：Fed 官員談話、利率或通膨]
    
    **今日市場焦點**
    • [大盤指數表現]：(納斯達克、標普500氛圍與客觀數據)
    • [主力強勢板塊]：(今日資金集中追捧的科技或半導體板塊)
    
    **操盤策略與投資建議**
    • 💰 資金風向：(分析華爾街機構最新聰明錢流向)
    • ⚡ 台股連動影響：(根據美股表現，推測外資明日動向及對台股供應鏈的具體連動衝擊)
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
    
    # 🚀 3. 同步回流到網頁快取槽 (對齊網頁 v1.5.1 的 Tab 4 獨立美股子區塊)
    generate_html_dashboard("ai_news_us", "🧠 美股 AI 核心戰略", final_report)