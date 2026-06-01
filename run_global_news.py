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
        final_content += "🌐 **查看詳細情報來源**：\n👉 https://yoznto.github.io/quant-dashboard/"
        
        data = {"content": final_content}
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print(f"✅ 成功推送到 Discord！(發送時間: {now_str})")
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
    print("1. 正在從 Yahoo 國際股市專區取得文章列表...")
    url = "https://tw.stock.yahoo.com/intl-markets/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        candidate_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/news/' in href:
                full_url = f"https://tw.stock.yahoo.com{href}" if not href.startswith('http') else href
                clean_url = full_url.split('?')[0]
                if clean_url not in candidate_links: candidate_links.append(clean_url)
                if len(candidate_links) >= target_limit: break
                        
        news_data_pool = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_single_article, candidate_links)
            for res in results:
                if res: news_data_pool.append(res)
        print(f"✅ 國際情報抓取完畢！共 {len(news_data_pool)} 篇。")
        return "\n".join(news_data_pool), candidate_links
    except Exception as e:
        print(f"抓取失敗: {e}")
        return "", []

if __name__ == "__main__":
    raw_news_pool, source_links = get_huge_global_news(target_limit=25)
    if not raw_news_pool: exit()
        
    generate_html_dashboard("global", "🌍 國際政經與環球情報", source_links)
    
    print(f"2. 【國際資料庫建立完成】正在將海量原始資料丟給 Llama 3.1 分析...\n")
    system_prompt = "你是一個專注於地緣政治與非美市場的宏觀經濟學家。請用極度客觀的語氣陳述國際事實。"
    user_prompt = f"""
    分析以下國際新聞（不含純美股）：
    {raw_news_pool}
    
    【⚠️ 鋼鐵紀律】：禁止發明數字，嚴禁廢話。
    
    🌍 **環球政經焦點**
    • [亞洲市場動態]：(中、日、韓等重要市場數據或政策)
    • [歐洲與地緣政治]：(歐洲央行、各國政策或地緣衝突事件)
    • [原油與匯率]：(原物料或重要貨幣走勢事實)

    ---
    📉 **宏觀風險提示**
    (給出一句關於國際局勢對供應鏈或全球資金的風險提示)
    """
    
    final_response = ollama.chat(
        model='llama3.1', 
        messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}],
        options={'temperature': 0, 'num_ctx': 8192} 
    )
    final_report = final_response['message']['content'].strip()
    
    print("="*60 + f"\n{final_report}\n" + "="*60)
    send_to_discord(final_report)