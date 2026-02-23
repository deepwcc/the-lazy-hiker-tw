import subprocess
import os
import sys
import json

def select_sample():
    base_path = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(base_path, "samples")
    
    if not os.path.exists(samples_dir):
        print(f"錯誤：找不到 samples 資料夾 ({samples_dir})")
        return None

    # 目前僅支援玉山單攻，其餘範本暫不顯示
    supported_list = ["application.玉山單攻.sample.json"]
    samples = [f for f in os.listdir(samples_dir) if f in supported_list]
    
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
            choice = input(f"\n請輸入編號 (1/{len(samples)})：")
            idx = int(choice) - 1
            if 0 <= idx < len(samples):
                return os.path.join(samples_dir, samples[idx])
            else:
                print(f"請輸入有效編號 (1/{len(samples)})")
        except ValueError:
            print("請輸入數字編號")

def run_apply(sample_path, test_mode=False):
    """
    執行自動填表腳本
    :param sample_path: JSON 範本路徑
    :param test_mode: 是否為測試模式 (True 會在填完後自動關閉瀏覽器)
    :return: 狀態碼 (0 為成功)
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_path, "src", "apply.js")

    if not os.path.exists(script_path):
        print(f"錯誤：找不到檔案 {script_path}")
        return 1

    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            application_data = f.read()
            # 驗證一下 JSON 格式
            json.loads(application_data)
    except Exception as e:
        print(f"讀取範本失敗: {e}")
        return 1

    # 設定環境變數
    env = os.environ.copy()
    env["APPLICATION_DATA"] = application_data
    if test_mode:
        env["TEST_MODE"] = "true"

    try:
        if not test_mode:
            print(f"\n正在啟動自動填表流程... (範本: {os.path.basename(sample_path)})")
        
        # 使用 subprocess 執行 Node.js 進程
        result = subprocess.run(
            ["node", "apply.js"],
            cwd=os.path.join(base_path, "src"),
            env=env
        )
        return result.returncode
    except Exception as e:
        print(f"啟動程式時發生錯誤: {e}")
        return 1

def main():
    # 1. 選擇範本
    sample_path = select_sample()
    if not sample_path:
        return

    # 2. 執行
    return_code = run_apply(sample_path)
    
    if return_code == 0:
        print("\n[Python] 腳本執行完成 (回傳碼 0)。")
    else:
        print(f"\n[Python] 腳本執行失敗 (回傳碼 {return_code})。")

if __name__ == "__main__":
    main()
