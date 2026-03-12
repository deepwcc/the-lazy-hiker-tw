import argparse
import os
import sys
import json
import yaml
import asyncio
from src.apply_yushan import apply as apply_yushan
from src.apply_shei_pa import apply as apply_shei_pa
from src.apply_taroko import apply as apply_taroko

def run_apply(sample_path, test_mode=False):
# ... (rest of the function stays same) ...
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
        
        # 取得國家公園名稱來判斷要用哪個 apply
        org = application_data.get("org", "")
        if "玉山" in org:
            print("偵測到玉山國家公園路線，使用 apply_yushan.py 邏輯")
            has_dialog, has_page_error = asyncio.run(apply_yushan(data=application_data, test_mode=test_mode))
        elif "雪霸" in org:
            print("偵測到雪霸國家公園路線，使用 apply_shei_pa.py 邏輯")
            has_dialog, has_page_error = asyncio.run(apply_shei_pa(data=application_data, test_mode=test_mode))
        elif "太魯閣" in org:
            print("偵測到太魯閣國家公園路線，使用 apply_taroko.py 邏輯")
            has_dialog, has_page_error = asyncio.run(apply_taroko(data=application_data, test_mode=test_mode))
        else:
            print(f"錯誤：不支援的國家公園管理處 '{org}'")
            return 1
        
        if has_dialog or has_page_error:
            return 1
        return 0
    except Exception as e:
        print(f"執行時發生錯誤: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="自動填寫入園申請")
    parser.add_argument("-p", "--sample_path", nargs="?", help="申請範本檔案路徑 (YAML/JSON)")
    parser.add_argument("-t", "--test", action="store_true", help="執行測試模式 (填寫完後不關閉瀏覽器，但會回傳狀態)")
    
    args = parser.parse_args()

    if not args.sample_path:
        print("錯誤：未提供檔案路徑")
        return

    if not os.path.exists(args.sample_path):
        print(f"錯誤：找不到檔案 '{args.sample_path}'")
        return

    # 2. 執行
    return_code = run_apply(args.sample_path, test_mode=args.test)
    
    if return_code == 0:
        print(f"\n[Python] 腳本執行完成 (回傳碼 0)。")
    else:
        print(f"\n[Python] 腳本執行失敗 (回傳碼 {return_code})。")

if __name__ == "__main__":
    main()
