import schedule
import time
import subprocess
import sys
from datetime import datetime

def run_script(script_name, job_title):
    print("="*50)
    print(f"🚀 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 啟動: {job_title}")
    try:
        # 呼叫獨立腳本執行，跑完釋放記憶體
        subprocess.run([sys.executable, script_name], check=True)
        print(f"✅ {job_title} 發送完畢！")
    except Exception as e:
        print(f"❌ {job_title} 發生錯誤: {e}")
    print("="*50 + "\n")

# ================= 時間排程設定 =================

# 1. 每天早上 08:00 跑【國際形勢版】
schedule.every().day.at("08:00").do(run_script, "run_global_news.py", "國際政經晨報")

# 2. 每天早上 09:00 跑【台股大數據版】
schedule.every().day.at("09:00").do(run_script, "run_analysis.py", "台股大數據晨報")

# 3. 每天晚上 21:00 (下午9:00) 跑【美股焦點版】
schedule.every().day.at("21:00").do(run_script, "run_us_stocks.py", "美股科技巨頭晚報")

# ================= 主程式區塊 =================
if __name__ == "__main__":
    print("🚀 三棲量化情資排程總管已啟動！")
    print(f"🕒 啟動時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⏳ 等待排程觸發中 (08:00 國際晨報 / 09:00 台股晨報 / 21:00 美股晚報)...")
    print("⚠️ 請保持此終端機開啟運作\n")
    
    while True:
        schedule.run_pending()
        time.sleep(1)