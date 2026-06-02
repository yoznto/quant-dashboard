import json
import ollama
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Quant Room Dynamic Industry Chain Brain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SHENG_SECRET_KEY = "ShengGeSecret666"

class SearchRequest(BaseModel):
    query: str

@app.post("/api/analyze")
async def analyze_industry_chain(req: SearchRequest, x_quant_key: str = Header(None)):
    if x_quant_key != SHENG_SECRET_KEY:
        raise HTTPException(status_code=403, detail="ACCESS_DENIED: Invalid Key.")

    keyword = req.query.strip()
    if not keyword:
        return {"summary": "請輸入有效產業名稱", "chains": []}

    print(f"⚡ [核心推理] 正在現場動態剖析『{keyword}』的上中下游產業鏈...")

    system_prompt = """你是一個精通全球股市（美股、台股、日韓歐股）的頂級產業鏈量化策略師。
使用者的痛點是：當某個熱門產品或概念爆紅時，主力的指標股往往已經漲太多。他們需要你幫忙拆解出「上游、中游、下游」的完整全球供應鏈，用以尋找尚未發酵的落後補漲股或隱藏受惠者。

🎯【全球產業地圖與代碼鋼鐵紀律】：
1. 視野必須是『全球化』的。請精準列出該產業鏈中掌握關鍵壁壘的全球企業。
2. 只要該公司有在公開市場上市，『必須強制附上正確的股票代號』。（美股如 NVDA.US；台股如 2330.TW）。
3. ⚠️【防數字幻覺嚴格警告】：你必須確保股票代號完全正確！如果缺乏把握，寧可只寫公司名稱。常見錯誤範例修正：『台達電是 2308.TW，絕對不是 2369.TW（菱生）』。請務必在腦中查證 Ticker 的正確性再輸出。
4. 每個節點（上游/中游/下游）的 companies 陣列『最多精選 3~4 家核心企業』，並在 desc 中一句話點出其技術護城河或受惠邏輯。
5. 你『必須嚴格』回傳純 JSON 格式，絕對不准包含任何 Markdown 標記（如 ```json），不要有任何客套話與廢話。

回傳的 JSON 語法結構必須完全符合以下規範（不准逸出）：
{
  "summary": "用兩句話宏觀總結。第一句點出該主題的全球市場趨勢；第二句指出在指標股大漲後，目前資金可能流向哪個上下游板塊尋找補漲機會。",
  "chains": [
    {
      "stage": "上游",
      "title": "原物料 / 核心晶片 / 設備設計",
      "companies": [
        {"name": "企業A", "id": "股票代號", "desc": "一小句話點出其在該上游節點的核心技術壁壘"}
      ]
    },
    {
      "stage": "中游",
      "title": "關鍵零組件 / 模組整合 / 中端代工",
      "companies": [
        {"name": "...", "id": "...", "desc": "..."}
      ]
    },
    {
      "stage": "下游",
      "title": "終端品牌 / 系統組裝 / 應用市場",
      "companies": [
        {"name": "...", "id": "...", "desc": "..."}
      ]
    }
  ]
}
"""

    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': system_prompt},
                # 👉 這裡也幫你改了，明確告訴模型使用者想找補漲機會
                {'role': 'user', 'content': f"請即時生出『{keyword}』的上中下游全球產業鏈，並提供股票代號尋找落後補漲機會。"}
            ],
            options={'temperature': 0.1, 'num_ctx': 4096}
        )

        reply = response['message']['content'].strip()

        if "```" in reply:
            reply = reply.split("```")[1]
            if reply.startswith("json"): reply = reply[4:]

        return json.loads(reply)

    except Exception as e:
        print(f"❌ 語法解析或推理失敗: {e}")
        return {{
            "summary": f"動態解析『{keyword}』時發生內部錯誤。",
            "chains": [
                {{"stage": "異常", "title": "大腦異常中斷", "companies": [{{"name": "請重試一次", "id": "500", "desc": str(e)}}]}}
            ]
        }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)