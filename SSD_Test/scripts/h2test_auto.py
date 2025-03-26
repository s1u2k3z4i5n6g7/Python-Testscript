"""
h2testw.exe自动化测试脚本
Requirements:
  - tested on Windows 10
  - pywinauto 0.6.9
  - H2testw 1.4
  - h2testw.exe-32位,需配置对应的Python环境32位
"""
from __future__ import print_function
from datetime import datetime
import logging
from pywinauto import actionlogger
from pywinauto import Application
import pyperclip
import os
import argparse
import ctypes
import time
import glob

# def list_h2test_gui():
#     try:
#         # 连接到已打开的主窗口 H2testw
#         app = Application(backend='uia').connect(title_re='H2testw')  # 连接到 H2testw 窗口
#         main_window = app.window(title_re='H2testw')  # 获取主窗口
#
#         # 查找子窗口 H2testw | Progress
#         progress_window = main_window.child_window(title="H2testw | Progress", control_type="Window")
#         progress_window.wait('visible')  # 等待子窗口可见
#
#         # print("Found the progress window.")
#         # 打印进度窗口的控件标识符，查看是否能够成功定位到控件
#         # print("Printing control identifiers for the Progress window:")
#         progress_window.print_control_identifiers()
#
#     except Exception as e:
#         print(f"错误: {e}")
#         return None  # 如果出错，返回 None

# 设置日志记录
log_file = r"C:\auto_run_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,  # 记录所有级别的日志
    format='%(asctime)s - %(levelname)s - %(message)s',  # 格式化日志输出
)

def format_drive(drive):
    """确保盘符格式正确（大写并添加 ':'）"""
    return drive.rstrip(":").upper() + ":"

def delete_h2w_files(drive):
    """删除指定盘符下的所有 .h2w 文件"""
    drive = format_drive(drive)
    h2w_files = glob.glob(f"{drive}\\*.h2w")

    if not h2w_files:
        logging.error(f"No .h2w files found in {drive}")
        return

    for file in h2w_files:
        try:
            os.remove(file)
            logging.info(f"Deleted: {file}")
        except Exception as e:
            logging.error(f"Failed to delete {file}: {e}")


def check_disk_space(drive):
    """获取指定盘符的剩余空间（单位：MB）"""
    drive = format_drive(drive)
    try:
        free_bytes = ctypes.c_ulonglong(0)
        total_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(drive),
            None,
            ctypes.pointer(total_bytes),
            ctypes.pointer(free_bytes)
        )
        free_space_gb = int(free_bytes.value / (1024**3))  # 将剩余空间存储为整数
        free_space_mb = int(free_space_gb * 1024)
        logging.info(f"磁盘 {drive} 剩余空间: {free_space_mb} MB")
        return free_space_mb  # 返回剩余空间的变量
    except Exception as e:
        logging.error(f"错误: {e}")
        return None  # 如果出错，返回 None


def run_h2test(drive):
    """运行 H2test 并测试指定磁盘"""
    drive = format_drive(drive)
    # 检查是否存在 .h2w 文件
    h2w_files = glob.glob(f"{drive}\\*.h2w")
    if h2w_files:
        logging.info(f"检测到 {len(h2w_files)} 个 .h2w 文件：")
        for file in h2w_files[:5]:  # 只展示前 5 个文件，避免列表过长
            logging.info(file)
        logging.info("...")

        choice = input("是否删除这些 .h2w 文件？(y/n): ").strip().lower()
        if choice == 'y':
            delete_h2w_files(drive)
        else:
            logging.info("未删除 .h2w 文件，继续运行 H2testw。")

    # 获取磁盘剩余空间
    free_space_mb = check_disk_space(drive)
    if free_space_mb is None:
        logging.info("未能获取磁盘空间信息，无法继续操作")
        return

    # 启动 H2testw
    app = Application(backend='uia').start(r'C:\Users\Administrator\Downloads\h2testw_1.4\h2testw.exe')
    dlg = app.window(title_re='H2testw')


    dlg['English'].click()
    dlg['Select target'].click()

    dlg['浏览文件夹'].wait('ready')
    dlg['浏览文件夹'].child_window(title="文件夹(F):", control_type="Edit").set_text(drive)
    dlg['浏览文件夹'].child_window(title="确定", auto_id="1", control_type="Button").click()

    dlg['only'].click()
    dlg['Edit'].set_text(str(free_space_mb))
    dlg['Write + Verify'].click()
    dlg['确定'].click()
    time.sleep(1)  # 等待进度窗口初始化


def check_h2test_result(drive):
    """检查 H2testw 测试结果"""
    drive = format_drive(drive)
    logging.info(f"Checking H2testw results for {drive}...")

    try:
        # 使用更具体的条件连接到H2testw窗口
        app = Application(backend='uia').connect(title='H2testw', visible_only=True)
        main_window = app.window(title='H2testw')  # 确保窗口标题为 'H2testw'
        # print("连接到主窗口成功")

        # 查找子窗口 H2testw | Progress
        progress_window = main_window.child_window(title="H2testw | Progress", control_type="Window")
        progress_window.wait('visible')  # 等待子窗口可见
        # print("Found the progress window.")

        # 设置最大等待时间（480 分钟）和检查间隔（5 分钟）
        max_wait_time = 480 * 60  # 480 分钟
        check_interval = 1 * 90   # 5 分钟
        elapsed_time = 0

        while elapsed_time < max_wait_time:
            try:
                # 清空剪贴板
                pyperclip.copy("")
                time.sleep(1)
                # 获取当前时间并格式化
                #current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

                # 点击 "Copy to clipboard" 按钮
                copy_button = progress_window.child_window(title="Copy to clipboard", control_type="Button")
                copy_button.click_input()  # 模拟点击
                # 打印当前时间以及已经经过的分钟
                logging.info(f"[{elapsed_time // 60} min ] Clicked 'Copy to clipboard'.")

                # 等待 2 秒以确保系统已将日志复制到剪贴板
                time.sleep(2)

                # 获取剪贴板内容
                log_content = pyperclip.paste()
                logging.info(f"[{elapsed_time // 60} min ] Log copied to clipboard.")

                # 保存日志到文件
                log_file_path = r"C:\h2test_log.txt"
                with open(log_file_path, "w") as log_file:
                    log_file.write(log_content)
                logging.info(f"Log written to {log_file_path}.")

                # 如果日志内容包含 "Test finished without errors."，说明测试通过
                if "Test finished without errors." in log_content:
                    logging.info("Test finished successfully.")
                    ok_button = progress_window.child_window(title="OK", control_type="Button")
                    ok_button.click_input()  # 点击 OK 按钮完成测试
                    logging.info("Clicked OK to finish the test.")

                    # 删除驱动器上的所有 .h2w 文件
                    delete_h2w_files(drive)
                    return "Pass"  # 测试通过

            except Exception as e:
                logging.error(f"Error occurred during check: {e}")

            # 每 5 分钟检查一次
            time.sleep(check_interval)
            elapsed_time += check_interval

        logging.error("Max wait time reached. Test might still be running.")
        return "Fail"  # 如果超时，则视为测试失败

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "Fail"