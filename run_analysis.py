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
        
        # 1. 建立開頭標題與 AI 報告內文
        final_content = f"**📊 今日台股量化大數據晨報 ({now_str}) 📊**\n\n{message}\n\n"
        
        # 2. 建立網址行（結尾加上 \n 強制換行，確保網址乾淨）
        final_content += "🌐 **查看詳細情報來源**：\n👉 https://yoznto.github.io/quant-dashboard/\n"
        
        # 3. 換行後再加入提示文字，分行顯示
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

def get_huge_taiwan_stock_news(target_limit=30):
    print("1. 正在從 Yahoo 台股焦點取得文章列表與摘要...")
    url = "https://tw.stock.yahoo.com/tw-market/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        info_list = []
        seen_urls = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '/news/' in href and href.endswith('.html'):
                full_url = f"https://tw.stock.yahoo.com{href}" if not href.startswith('http') else href
                
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    
                    # 抓取連結文字作為新聞摘要
                    title_text = a_tag.text.strip() if a_tag.text else "查看原始新聞"
                    if len(title_text) < 5:
                        title_text = "台股大數據財經線索"
                        
                    info_list.append({
                        "url": full_url,
                        "title": title_text
                    })
                    
                if len(info_list) >= target_limit: break
                        
        news_data_pool = []
        just_urls = [item["url"] for item in info_list]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_single_article, just_urls)
            for res in results:
                if res: news_data_pool.append(res)
                
        print(f"✅ 台股抓取完畢！共 {len(news_data_pool)} 篇。")
        return "\n".join(news_data_pool), info_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return "", []

if __name__ == "__main__":
    raw_news_pool, info_list = get_huge_taiwan_stock_news(target_limit=30)
    if not raw_news_pool: exit()
        
    # 傳入「tw」識別碼、純名稱標題、以及帶有標題說明的 info_list
    generate_html_dashboard("tw", "📊 台股大數據晨報", info_list)
    
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