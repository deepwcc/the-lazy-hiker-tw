import os
import sys
import json
import yaml
import asyncio
from src.apply import apply

def select_sample():
    base_path = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(base_path, "samples")
    
    # 優先尋找根目錄下的自定義申請檔案
    for ext in ["yaml", "yml", "json"]:
        custom_file = os.path.join(base_path, f"application.{ext}")
        if os.path.exists(custom_file):
            print(f"偵測到自定義申請檔案: {custom_file}")
            return custom_file

    if not os.path.exists(samples_dir):
        print(f"錯誤：找不到 samples 資料夾 ({samples_dir})")
        return None

    # 目前支援玉山主東兩天、桃山單攻，其餘範本暫不顯示
    supported_list = ["application.玉山主東兩天.sample.yaml", "application.桃山單攻.sample.yaml"]
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
            choice = input(f"\n請輸入編號 (1-{len(samples)})：")
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
    :param sample_path: 範本路徑 (JSON 或 YAML)
    :param test_mode: 是否為測試模式 (True 會在填完後自動關閉瀏覽器)
    :return: 狀態碼 (0 為成功)
    """
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            if sample_path.endswith((".yaml", ".yml")):
                application_data = yaml.safe_load(f)
            else:
                application_data = json.load(f)
    except Exception as e:
        print(f"讀取範本失敗: {e}")
        return 1

    try:
        if not test_mode:
            print(f"\n正在啟動自動填表流程... (範本: {os.path.basename(sample_path)})")
        
        # 直接呼叫 Python 函式
        has_dialog, has_page_error = asyncio.run(apply(data=application_data, test_mode=test_mode))
        
        if has_dialog or has_page_error:
            return 1
        return 0
    except Exception as e:
        print(f"執行時發生錯誤: {e}")
        return 1

def main():
    # 1. 選擇範本
    sample_path = select_sample()
    if not sample_path:
        return

    # 2. 執行
    return_code = run_apply(sample_path)
    
    if return_code == 0:
        print(f"\n[Python] 腳本執行完成 (回傳碼 0)。")
    else:
        print(f"\n[Python] 腳本執行失敗 (回傳碼 {return_code})。")

if __name__ == "__main__":
    main()
