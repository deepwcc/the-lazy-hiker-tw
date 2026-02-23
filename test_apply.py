import os
import sys
import argparse
import fnmatch
from main import run_apply

def run_test_for_sample(sample_path):
    """
    通用測試函式
    測試通過條件：
    1. 網頁填寫過程沒有任何 dialog 或錯誤回傳
    2. 各國家公園對應的 apply_*.py 回傳 0
    """
    sample_name = os.path.basename(sample_path)
    print(f"\n[Test] 開始執行 {sample_name} 自動填表測試...")
    
    # 執行測試模式 (test_mode=True)
    return_code = run_apply(sample_path, test_mode=True)
    
    if return_code == 0:
        print(f"[Test] {sample_name} 測試通過！")
        return True
    else:
        print(f"[Test] {sample_name} 測試失敗，回傳碼: {return_code}")
        return False

def test_samples(filter_pattern=None, run_all=False):
    """
    跑 samples 資料夾下的 .json 檔案，可依據參數篩選
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(base_path, "samples")
    
    if not os.path.exists(samples_dir):
        print(f"錯誤：找不到 samples 資料夾 ({samples_dir})")
        sys.exit(1)
        
    sample_files = []
    for root, dirs, files in os.walk(samples_dir):
        for f in files:
            if f.endswith((".yaml", ".yml")):
                # 取得相對路徑
                rel_path = os.path.relpath(os.path.join(root, f), samples_dir)
                sample_files.append(rel_path)
    sample_files.sort()
    
    if not sample_files:
        print("警告：samples 資料夾內沒有 .yaml 檔案")
        return

    # 根據參數篩選檔案
    if filter_pattern:
        # 支援簡單的 glob 匹配，如 *玉山*
        filtered_files = [f for f in sample_files if fnmatch.fnmatch(f, f"*{filter_pattern}*")]
    else:
        filtered_files = sample_files

    if not filtered_files:
        print(f"找不到符合篩選條件 '{filter_pattern}' 的測試檔案")
        return

    failed_tests = []
    for filename in filtered_files:
        sample_path = os.path.join(samples_dir, filename)
        success = run_test_for_sample(sample_path)
        if not success:
            failed_tests.append(filename)

    print("\n" + "="*30)
    if not failed_tests:
        print(f"✅ 測試項目通過 (共 {len(filtered_files)} 項)")
    else:
        print(f"❌ 測試未通過，失敗項目: {', '.join(failed_tests)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="執行自動填表測試")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="執行 samples 下所有測試")
    group.add_argument("--filter", type=str, help="依關鍵字篩選測試檔案 (例如: 玉山)")
    
    args = parser.parse_args()

    try:
        # 如果沒給參數，預設跑所有
        if args.filter:
            test_samples(filter_pattern=args.filter)
        else:
            test_samples(run_all=True)
    except Exception as e:
        print(f"\n❌ 發生意外錯誤: {e}")
        sys.exit(1)
