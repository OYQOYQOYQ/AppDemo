#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI工具模块，包含UI相关的工具函数
"""

import os
import logging
from PySide6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)

def load_fonts():
    """加载项目中的自定义字体（保持兼容性）"""
    return load_custom_fonts()

def load_custom_fonts():
    """加载项目中的自定义字体"""
    fonts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "fonts")
    title_font_path = os.path.join(fonts_path, "title.ttf")
    oppo_font_path = os.path.join(fonts_path, "OPPOSans-R.ttf")
    
    # 加载字体文件
    try:
        title_font_id = QFontDatabase.addApplicationFont(title_font_path)
        oppo_font_id = QFontDatabase.addApplicationFont(oppo_font_path)
        
        if title_font_id == -1:
            logger.warning(f"无法加载title字体: {title_font_path}")
        if oppo_font_id == -1:
            logger.warning(f"无法加载OPPO字体: {oppo_font_path}")
            
        return {
            "title": QFontDatabase.applicationFontFamilies(title_font_id)[0] if title_font_id != -1 else "Arial",
            "oppo": QFontDatabase.applicationFontFamilies(oppo_font_id)[0] if oppo_font_id != -1 else "Arial"
        }
    except Exception as e:
        logger.error(f"加载自定义字体失败: {e}")
        return {"title": "Arial", "oppo": "Arial"}

def get_system_theme():
    """获取系统当前主题（浅色/深色）"""
    try:
        # 尝试检测Windows系统主题
        if os.name == 'nt':
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return 'light' if value == 1 else 'dark'
        # 对于其他系统，默认返回浅色
        return 'light'
    except Exception:
        return 'light'

def get_theme_stylesheet(theme):
    """获取指定主题的样式表
    
    Args:
        theme: 主题类型 ('system', 'light', 'dark')
        
    Returns:
        str: CSS样式表字符串
    """
    # 如果是跟随系统，获取系统主题
    if theme == 'system':
        theme = get_system_theme()
    
    # 定义主题样式
    stylesheets = {
        'light': '''
            QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                background-color: #f9f9f9;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #000000;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
            }
            QScrollArea {
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 10px;
            }
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 10px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #cccccc;
                border-radius: 5px;
            }
        ''',
        'dark': '''
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #666666;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QGroupBox {
                border: 1px solid #666666;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #666666;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom-color: #2d2d2d;
            }
            QScrollArea {
                background-color: #2d2d2d;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 10px;
            }
            QScrollBar:horizontal {
                background-color: #404040;
                height: 10px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #666666;
                border-radius: 5px;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #666666;
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        '''
    }
    
    return stylesheets.get(theme, stylesheets['light'])
