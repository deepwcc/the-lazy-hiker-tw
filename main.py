import execjs
import os
import sys
import json

def select_sample():
    base_path = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(base_path, "samples")
    
    if not os.path.exists(samples_dir):
        print(f"錯誤：找不到 samples 資料夾 ({samples_dir})")
        return None

    # 列出所有 .sample.json 檔案
    samples = [f for f in os.listdir(samples_dir) if f.endswith(".sample.json")]
    
    if not samples:
        print("錯誤：samples 資料夾內沒有範本檔案")
        return None

    print("\n請選擇要使用的申請範本：")
    for i, name in enumerate(samples, 1):
        # 移除 .sample.json 讓顯示更乾淨
        display_name = name.replace("application.", "").replace(".sample.json", "")
        print(f"{i}. {display_name} ({name})")

    while True:
        try:
            choice = input(f"\n請輸入編號 (1-{len(samples)})：")
            idx = int(choice) - 1
            if 0 <= idx < len(samples):
                return os.path.join(samples_dir, samples[idx])
            else:
                print(f"請輸入有效編號 (1-{len(samples)})")
        except ValueError:
            print("請輸入數字編號")

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_path, "src", "apply.js")
    
    if not os.path.exists(script_path):
        print(f"錯誤：找不到檔案 {script_path}")
        return

    # 1. 選擇範本
    sample_path = select_sample()
    if not sample_path:
        return

    # 2. 讀取範本內容
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            application_data = f.read()
            # 驗證一下 JSON 格式
            json.loads(application_data)
    except Exception as e:
        print(f"讀取範本失敗: {e}")
        return

    # 3. 讀取 apply.js 內容
    with open(script_path, "r", encoding="utf-8") as f:
        js_code = f.read()

    # 切換工作目錄到 src 之下以利 Node.js 運作
    original_cwd = os.getcwd()
    src_dir = os.path.join(base_path, "src")
    os.chdir(src_dir)

    try:
        print(f"\n正在準備執行範本: {os.path.basename(sample_path)}")
        
        # 4. 使用環境變數傳遞資料給 JS
        # PyExecJS 預設可能不會繼承 env，我們需要透過一些方式確保 Node 拿到資料
        # 這裡我們直接在 JS 代碼最前面注入資料，這比環境變數更可靠 (針對 ExecJS)
        injected_js = f"process.env.APPLICATION_DATA = {json.dumps(application_data)};\n" + js_code
        
        node = execjs.get("Node")
        node.exec_(injected_js)
        
        print("執行完畢。")
        
    except execjs.RuntimeError as e:
        print(f"執行時發生 RuntimeError: {e}")
    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()
