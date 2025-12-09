#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI工具模块，包含UI相关的工具函数
"""

import os
import logging
from PySide6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)

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
