#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可拖拽排序的按钮容器组件
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal, QPoint, QEvent, QMimeData
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor

logger = logging.getLogger(__name__)

class DraggableButtonItem(QWidget):
    """可拖拽的按钮项"""
    def __init__(self, text, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.original_text = text
        self.drag_start_position = QPoint()  # 初始化拖拽起始位置
        self.is_being_dragged = False  # 初始化拖拽状态标志
        self.init_ui(text)
        
    def init_ui(self, text):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.button = QPushButton(text)
        self.button.setMinimumHeight(40)
        self.button.setStyleSheet("padding: 8px; border: 1px solid #ccc; background-color: #f8f8f8;")
        self.button.setCursor(Qt.OpenHandCursor)  # 设置手型光标，提示可拖拽
        layout.addWidget(self.button)
        self.setLayout(layout)
        
        # 禁用按钮的默认点击行为
        self.button.setFocusPolicy(Qt.NoFocus)
        
    def mousePressEvent(self, event):
        """鼠标按下事件，准备拖拽"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            # 改变鼠标样式为抓取状态
            self.button.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，实现Qt标准拖拽"""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        # 检查拖拽距离阈值
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return
        
        # 创建拖拽对象
        drag = QDrag(self)
        
        # 创建MIME数据，存储被拖拽项的索引
        mime_data = QMimeData()
        mime_data.setText(f"drag_index:{self.index}")
        drag.setMimeData(mime_data)
        
        # 创建拖拽时的视觉反馈
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 255, 30))  # 半透明蓝色覆盖
        painter.end()
        drag.setPixmap(pixmap)
        
        # 设置拖拽热点
        drag.setHotSpot(event.pos())
        
        # 执行拖拽，使用MoveAction模式
        drag.exec_(Qt.MoveAction)
        
        # 恢复鼠标样式
        self.button.setCursor(Qt.OpenHandCursor)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 恢复鼠标样式
        self.button.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)
        
    def enterEvent(self, event):
        """鼠标进入事件"""
        # 鼠标悬停时高亮显示
        if not hasattr(self, 'is_being_dragged') or not self.is_being_dragged:
            self.button.setStyleSheet("padding: 8px; border: 1px solid #0078d7; background-color: #f0f7ff;")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        # 鼠标离开时恢复默认样式
        if not hasattr(self, 'is_being_dragged') or not self.is_being_dragged:
            self.button.setStyleSheet("padding: 8px; border: 1px solid #ccc; background-color: #f8f8f8;")
        super().leaveEvent(event)

class DraggableButtonContainer(QWidget):
    """可拖拽排序的按钮容器"""
    order_changed = Signal(list)  # 按钮顺序改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_items = []
        self.init_ui()
        
        # 设置为接受拖放事件
        self.setAcceptDrops(True)
    
    def init_ui(self):
        """初始化UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)
        
        # 添加说明标签
        self.info_label = QLabel("拖拽按钮可以调整顺序")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 8px;")
        self.layout.addWidget(self.info_label)
    
    def set_buttons(self, button_texts):
        """设置按钮列表
        
        Args:
            button_texts: 按钮文本列表
        """
        # 清除现有按钮
        self.clear_buttons()
        
        # 创建新按钮项
        for i, text in enumerate(button_texts):
            button_item = DraggableButtonItem(text, i, self)
            self.button_items.append(button_item)
            self.layout.addWidget(button_item)
    
    def clear_buttons(self):
        """清除所有按钮"""
        for item in self.button_items:
            self.layout.removeWidget(item)
            item.deleteLater()
        self.button_items.clear()
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        # 检查MIME数据是否包含我们需要的格式
        mime_data = event.mimeData()
        if mime_data.hasText() and mime_data.text().startswith("drag_index:"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        # 检查MIME数据是否包含我们需要的格式
        mime_data = event.mimeData()
        if mime_data.hasText() and mime_data.text().startswith("drag_index:"):
            event.acceptProposedAction()
            
            # 视觉反馈：在鼠标下方显示插入位置
            self.highlight_drop_target(event)
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        # 清除所有高亮
        self.reset_all_highlights()
    
    def dropEvent(self, event):
        """拖拽放置事件"""
        # 检查MIME数据
        mime_data = event.mimeData()
        if not mime_data.hasText() or not mime_data.text().startswith("drag_index:"):
            return
        
        try:
            # 解析被拖拽项的索引
            dragged_index_str = mime_data.text().split(":")[1]
            dragged_index = int(dragged_index_str)
            
            # 找到拖拽源项
            dragged_item = None
            for item in self.button_items:
                if item.index == dragged_index:
                    dragged_item = item
                    break
            
            if not dragged_item:
                return
            
            # 找到放置目标位置
            drop_position = event.pos()
            target_item = self.find_item_at_position(drop_position)
            
            if not target_item or target_item == dragged_item:
                # 如果没有目标或目标是自身，则重置高亮并返回
                self.reset_all_highlights()
                return
            
            # 执行排序
            old_index = self.button_items.index(dragged_item)
            new_index = self.button_items.index(target_item)
            
            logger.info(f"拖拽排序: 从索引 {old_index} 到 {new_index}")
            
            # 重新排序按钮项列表
            self.button_items.pop(old_index)
            self.button_items.insert(new_index, dragged_item)
            
            # 更新布局
            self.update_layout()
            
            # 更新所有按钮的索引
            for i, btn_item in enumerate(self.button_items):
                btn_item.index = i
            
            # 发出顺序改变信号
            new_order = [btn_item.original_text for btn_item in self.button_items]
            self.order_changed.emit(new_order)
            
            logger.info(f"新的按钮顺序: {new_order}")
            
        except Exception as e:
            logger.error(f"处理拖拽放置错误: {str(e)}")
        finally:
            # 重置所有高亮
            self.reset_all_highlights()
    
    def find_item_at_position(self, position):
        """根据位置查找对应的按钮项
        
        Args:
            position: 鼠标位置
        
        Returns:
            DraggableButtonItem: 对应的按钮项，如果没有则返回None
        """
        for item in self.button_items:
            # 转换为局部坐标进行比较
            item_rect = item.geometry()
            if item_rect.contains(item.mapFrom(self, position)):
                return item
        return None
    
    def highlight_drop_target(self, event):
        """高亮显示放置目标
        
        Args:
            event: 拖拽事件
        """
        # 先重置所有高亮
        self.reset_all_highlights()
        
        # 查找当前位置下的按钮项
        position = event.pos()
        target_item = self.find_item_at_position(position)
        
        if target_item:
            # 高亮显示目标项
            target_item.button.setStyleSheet("padding: 8px; border: 2px dashed #0078d7; background-color: #e6f3ff;")
    
    def reset_all_highlights(self):
        """重置所有按钮的高亮状态"""
        for item in self.button_items:
            item.button.setStyleSheet("padding: 8px; border: 1px solid #ccc; background-color: #f8f8f8;")
    
    def update_layout(self):
        """更新布局中的按钮顺序"""
        # 先移除所有按钮项（除了说明标签）
        while self.layout.count() > 1:  # 保留说明标签
            item = self.layout.takeAt(1).widget()  # 从索引1开始（索引0是说明标签）
            if item:
                self.layout.removeWidget(item)
        
        # 重新添加按钮项
        for item in self.button_items:
            self.layout.addWidget(item)
    
    def get_current_order(self):
        """获取当前按钮顺序
        
        Returns:
            list: 按钮文本列表
        """
        try:
            order = [item.original_text for item in self.button_items]
            logger.debug(f"当前按钮顺序: {order}")
            return order
        except Exception as e:
            logger.error(f"获取按钮顺序错误: {str(e)}")
            return []
