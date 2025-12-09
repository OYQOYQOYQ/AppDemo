#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniApp - 一个集成搜索、系统监控和日志功能的小应用
"""

import sys
import os
import logging
from PySide6.QtWidgets import QApplication

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 导入模块
from ui.utils import load_custom_fonts
from ui.main_window import MainWindow

# 兼容旧的log函数
def log(message):
    """记录日志（兼容旧代码）"""
    logger.info(message)

def main():
    """
    应用程序主函数
    """
    try:
        print("Starting Mini App...")
        
        # 创建Qt应用程序实例
        app = QApplication(sys.argv)
        print("QApplication instance created")
        
        # 加载自定义字体
        fonts = load_custom_fonts()
        print(f"加载的字体: title='{fonts['title']}', oppo='{fonts['oppo']}'")
        
        # 创建主窗口
        print("Creating main window...")
        main_window = MainWindow(fonts)
        print("Main window created")
        
        # 显示主窗口
        main_window.show()
        print("Main window shown with size 260x260")
        
        # 进入应用程序主循环
        print("Entering application main loop")
        exit_code = app.exec()
        
        print(f"Application exited with code {exit_code}")
        return exit_code
        
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print("详细错误信息:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())