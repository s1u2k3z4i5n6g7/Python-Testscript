# main.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
from h2test_auto import run_h2test
from h2test_auto import check_h2test_result
from BurnInTest_auto import run_BurnInTest

if __name__ == "__main__":
    drive = input("请输入测试盘符 (如 E:): ").strip()
    if drive:
        run_h2test(drive)
        result = check_h2test_result(drive)
        print(f"测试结果: {result}")
    else:
        print("未输入有效的盘符，退出程序。")
