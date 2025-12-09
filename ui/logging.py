#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI日志模块，包含日志相关的功能
"""

import logging

logger = logging.getLogger(__name__)

# 兼容原有的log函数
def log(message):
    logger.info(message)

class LogToWidgetHandler(logging.Handler):
    """自定义日志处理器，将日志输出到Qt组件"""
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
    
    def format(self, record):
        """重写format方法，只返回消息内容，与Python解释器输入文本格式一致"""
        return record.getMessage()
    
    def emit(self, record):
        """输出日志记录到UI组件"""
        try:
            # 格式化日志消息
            msg = self.format(record)
            
            # 使用信号槽机制或直接在主线程中更新
            def update_log():
                self.widget.append(msg)
                # 自动滚动到底部
                self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum())
            
            # 直接调用，因为QueueListener已经在主线程中运行
            update_log()
        except Exception as e:
            self.handleError(record)
