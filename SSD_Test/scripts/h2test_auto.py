"""
h2testw.exe自动化测试脚本
Requirements:
  - tested on Windows 10
  - pywinauto 0.6.9
  - H2testw 1.4
  - h2testw.exe-32位,需配置对应的Python环境32位
"""
from __future__ import print_function
import logging
from pywinauto import actionlogger
from pywinauto import Application
import argparse
import time
def run_h2test(log_file=None):
    # 参数解析（避免直接运行时的冲突）
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", help="enable logging", type=str, required=False)
    args = parser.parse_args()

    # 初始化日志
    actionlogger.enable()
    logger = logging.getLogger('pywinauto')
    if args.log:
        logger.handlers[0] = logging.FileHandler(args.log)

    # 启动应用程序
    app = Application(backend='uia').start(r'C:\Users\Administrator\Downloads\h2testw_1.4\h2testw.exe')
    dlg = app.window(title_re='H2testw')
    dlg['English'].click()
    dlg['Select target'].click()
    #dlg.child_window(title='浏览文件夹', control_type='MenuItem', found_index=0).invoke()
    #dlg.print_control_identifiers()
    dlg['浏览文件夹'].wait('ready')  # 等待控件准备好
    file_name_edit = dlg['浏览文件夹'].child_window(title="文件夹(F):", control_type="Edit")
    file_name_edit.set_text(r'F:')
    dlg['浏览文件夹'].child_window(title="确定", auto_id="1", control_type="Button").click()
    dlg['only'].click()
    file_name_edit2 = dlg['H2testw'].child_window(title="",auto_id="1", control_type="Edit")
    dlg['Edit'].set_text(r'1024')
    dlg['Write + Verify'].click()
    dlg['确定'].click()

if __name__ == "__main__":
    run_h2test()  # 直接运行时调用