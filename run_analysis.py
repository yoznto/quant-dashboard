import requests
from bs4 import BeautifulSoup
import ollama
import time
from datetime import datetime
import concurrent.futures
from web_generator import generate_html_dashboard # 引入網頁生成器

# 👉 你的專屬 Discord Webhook
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1510814929186324550/foMi7Kqoc7q2gILVYg5-qo-g9dCBjrwnUrzffTIk1V6Bd8yvCqNH6rGFoYfVE3M_jAig"

def send_to_discord(message):
    if not DISCORD_WEBHOOK_URL: return
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        final_content = f"**📊 今日台股量化大數據晨報 ({now_str}) 📊**\n\n{message}\n\n"
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

def get_huge_taiwan_stock_news(target_limit=30):
    print("1. 正在從 Yahoo 台股焦點取得文章列表...")
    url = "https://tw.stock.yahoo.com/tw-market/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        candidate_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/news/' in href and href.endswith('.html'):
                full_url = f"https://tw.stock.yahoo.com{href}" if not href.startswith('http') else href
                if full_url not in candidate_links: candidate_links.append(full_url)
                if len(candidate_links) >= target_limit: break
                        
        news_data_pool = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_single_article, candidate_links)
            for res in results:
                if res: news_data_pool.append(res)
        print(f"✅ 台股抓取完畢！共 {len(news_data_pool)} 篇。")
        
        # 👉 回傳字串內容與網址清單
        return "\n".join(news_data_pool), candidate_links
    except Exception as e:
        print(f"抓取失敗: {e}")
        return "", []

if __name__ == "__main__":
    raw_news_pool, source_links = get_huge_taiwan_stock_news(target_limit=30)
    if not raw_news_pool: exit()
        
    generate_html_dashboard("tw", "📊 台股大數據晨報", source_links)
    
    print(f"2. 【台股資料庫建立完成】正在將海量原始資料丟給 Llama 3.1 分析...\n")
    system_prompt = "你是一個高冷且極度嚴謹的台股量化策略師。你的任務是從大量新聞中萃取純乾貨，請直接陳述市場事實。"
    user_prompt = f"""
    分析以下台股新聞資料庫：
    {raw_news_pool}
    
    【⚠️ 鋼鐵紀律】：
    1. 絕對不准捏造大盤點位或股價！
    2. 必須點出具體「公司名稱」或「族群」。
    3. 嚴禁廢話。
    
    🎯 **今日市場焦點**
    • [產業與板塊動態]：(熱門產業事實與具體公司)
    • [大盤與總體表現]：(客觀描述大盤氛圍)
    • [個股與強勢標的]：(突出的個股或 ETF)

    ---
    📈 **操盤策略與投資建議**
    • ⚖️ 潛在風險：(一句極度客觀的風險警告)
    • 💰 行動方針：(短線操作的具體方向)
    """
    
    final_response = ollama.chat(
        model='llama3.1', 
        messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}],
        options={'temperature': 0, 'num_ctx': 8192} 
    )
    final_report = final_response['message']['content'].strip()
    
    print("="*60 + f"\n{final_report}\n" + "="*60)
    send_to_discord(final_report)