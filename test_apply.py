import os
import sys
from main import run_apply

def test_yushan_one_day():
    """
    測試：玉山單攻範本自動填寫
    測試通過條件：
    1. 網頁填寫過程沒有任何 dialog 或錯誤回傳 (由 apply.py 偵測並透過回傳碼反應)
    2. apply.py 回傳 0
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(base_path, "samples", "application.玉山單攻.sample.json")
    
    print("\n[Test] 開始執行玉山單攻自動填表測試...")
    
    # 執行測試模式 (test_mode=True)
    return_code = run_apply(sample_path, test_mode=True)
    
    if return_code == 0:
        print("[Test] 測試通過！")
    else:
        print(f"[Test] 測試失敗，回傳碼: {return_code}")
    
    assert return_code == 0

if __name__ == "__main__":
    # 也可以直接執行此檔案進行簡單測試
    try:
        test_yushan_one_day()
        print("\n✅ 所有測試項目通過")
    except AssertionError:
        print("\n❌ 測試未通過")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生意外錯誤: {e}")
        sys.exit(1)
