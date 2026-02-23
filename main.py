import execjs
import os
import sys

def main():
    # 取得目前檔案所在的絕對路徑
    base_path = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_path, "src", "apply.js")
    
    if not os.path.exists(script_path):
        print(f"錯誤：找不到檔案 {script_path}")
        return

    # 讀取 apply.js 內容
    with open(script_path, "r", encoding="utf-8") as f:
        js_code = f.read()

    # 因為 apply.js 裡面使用了 require("./application.json")
    # 我們需要切換工作目錄到 src 之下，否則 Node.js 會找不到該 json 檔案
    original_cwd = os.getcwd()
    src_dir = os.path.join(base_path, "src")
    os.chdir(src_dir)

    try:
        print("正在使用 PyExecJS 呼叫 src/apply.js...")
        
        # 確保使用 Node.js 作為執行後端（Playwright 必須在 Node 環境執行）
        # 如果您的系統 node 指令不在 PATH 中，可能需要手動指定
        node = execjs.get("Node")
        
        # 執行 JS 代碼
        # 由於 apply.js 最後一行已經寫了 apply().catch(console.error);
        # 所以只要執行這段代碼就會觸發非同步的 apply 函式
        node.exec_(js_code)
        
        print("執行完畢。")
        
    except execjs.RuntimeError as e:
        print(f"執行時發生 RuntimeError: {e}")
    except Exception as e:
        print(f"發生錯誤: {e}")
        print("\n請檢查：")
        print("1. 是否已安裝 PyExecJS (pip install PyExecJS)")
        print("2. 系統是否已安裝 Node.js")
        print("3. 是否已執行過 npm install (確保 playwright 已安裝)")
    finally:
        # 切換回原來的目錄
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()
