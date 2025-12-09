from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt

class StatusPanel(QWidget):
    """
    状态面板组件
    用于显示应用程序的状态信息
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化状态面板UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 设置面板标题
        title_label = QLabel("Status")
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)
        
        # 创建状态信息标签
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def update_status(self, status):
        """更新状态信息"""
        self.status_label.setText(status)


class ToolButton(QPushButton):
    """
    自定义工具按钮组件
    提供统一的按钮样式和行为
    """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)


class ButtonPanel(QWidget):
    """
    按钮面板组件
    包含一组工具按钮
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化按钮面板UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # 添加一些示例按钮
        self.btn_action1 = ToolButton("Action 1")
        self.btn_action2 = ToolButton("Action 2")
        
        layout.addWidget(self.btn_action1)
        layout.addWidget(self.btn_action2)
        layout.addStretch()  # 添加伸缩空间使按钮保持在顶部