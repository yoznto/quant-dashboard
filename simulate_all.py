import subprocess
import sys
import time
from datetime import datetime

def run_simulation():
    print("="*60)
    print("🚀 【全系統功能整合測試】開始執行")
    print("目的：模擬一整天三個時段的自動化流程，驗證網頁分頁（Tabs）聚合功能。")
    print("提示：由於需要呼叫本地 Llama 3.1 三次，整體執行可能需要 1~3 分鐘，請耐心等待。")
    print("="*60 + "\n")
    
    start_time = time.time()

    # 1. 模擬早上 08:00 執行【國際政經晨報】
    print(f"⏳ [階段 1/3] 正在模擬 08:00 任務：啟動國際政經爬蟲與 AI 分析...")
    try:
        subprocess.run([sys.executable, "run_global_news.py"], check=True)
        print("✅ 國際政經模組執行成功，已成功寫入 JSON 並更新 index.html！\n")
    except Exception as e:
        print(f"❌ 國際政經模組執行失敗: {e}\n")
    
    time.sleep(2) # 緩衝 2 秒

    # 2. 模擬早上 09:00 執行【台股大數據晨報】
    print(f"⏳ [階段 2/3] 正在模擬 09:00 任務：啟動台股大數據爬蟲與 AI 分析...")
    try:
        subprocess.run([sys.executable, "run_analysis.py"], check=True)
        print("✅ 台股大數據模組執行成功，已成功讀取歷史紀錄並追加台股分頁！\n")
    except Exception as e:
        print(f"❌ 台股大數據模組執行失敗: {e}\n")
    
    time.sleep(2) # 緩衝 2 秒

    # 3. 模擬晚上 21:00 執行【美股科技巨頭晚報】
    print(f"⏳ [階段 3/3] 正在模擬 21:00 任務：啟動美股焦點爬蟲與 AI 分析...")
    try:
        subprocess.run([sys.executable, "run_us_stocks.py"], check=True)
        print("✅ 美股焦點模組執行成功，已完成全網頁數據最終聚合！\n")
    except Exception as e:
        print(f"❌ 美股焦點模組執行失敗: {e}\n")

    end_time = time.time()
    print("="*60)
    print(f"🎉 【模擬測試全部結束】總耗時：{int(end_time - start_time)} 秒")
    print("1. 請檢查資料夾內是否產生了 'dashboard_data.json' 與 'index.html'。")
    print("2. 點開 'index.html'，用滑鼠切換三個分頁，確認資料是否都完美對齊！")
    print("3. 同時檢查 Discord 頻道，應該會按順序收到三則帶有網頁連結的推播報告。")
    print("="*60)

if __name__ == "__main__":
    run_simulation()