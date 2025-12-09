import os
import json
import logging
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QCheckBox, QGroupBox,
    QScrollArea, QFrame, QTabWidget, QStyleFactory, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from ui.utils import load_fonts

logger = logging.getLogger(__name__)

class SettingsWindow(QDialog):
    """设置窗口类"""
    # 主题变化信号
    theme_changed = Signal(str)
    # 搜索功能启用状态变更信号
    search_enabled_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # 配置文件路径
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                       "config", "settings.json")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle("设置")
        self.setGeometry(200, 200, 600, 400)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                "resources", "icons", "mining_38202.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 加载字体
        self.fonts = load_fonts()
        
        # 主布局 (直接设置到QDialog)
        self.main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 创建各个选项卡
        self.create_general_tab()
        self.create_search_tab()
        self.create_buttons_tab()
        self.create_about_tab()
        
        # 添加选项卡到选项卡部件
        self.tab_widget.addTab(self.general_tab, "常规")
        self.tab_widget.addTab(self.search_tab, "搜索")
        self.tab_widget.addTab(self.buttons_tab, "按钮")
        self.tab_widget.addTab(self.about_tab, "关于")
        
        # 添加选项卡部件到主布局
        self.main_layout.addWidget(self.tab_widget)
        
        # 创建底部按钮布局
        button_layout = QHBoxLayout()
        
        # 保存按钮
        self.save_button = QPushButton("保存设置")
        self.save_button.clicked.connect(self.save_settings)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        # 添加按钮布局到主布局
        self.main_layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """创建常规设置选项卡"""
        self.general_tab = QWidget()
        layout = QVBoxLayout(self.general_tab)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建滚动内容部件
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # 主题设置分组
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)
        
        # 主题选择标签
        theme_label = QLabel("选择应用主题:")
        theme_label.setFont(QFont(self.fonts['oppo'], 10))
        theme_layout.addWidget(theme_label)
        
        # 主题选择下拉框
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["跟随系统", "浅色模式", "深色模式"])
        self.theme_combo.setFont(QFont(self.fonts['oppo'], 10))
        theme_layout.addWidget(self.theme_combo)
        
        # 添加主题设置到滚动布局
        scroll_layout.addWidget(theme_group)
        
        # 添加更多通用设置项可以在这里继续添加
        scroll_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 添加滚动区域到布局
        layout.addWidget(scroll_area)
    
    def create_search_tab(self):
        """创建搜索设置选项卡"""
        self.search_tab = QWidget()
        layout = QVBoxLayout(self.search_tab)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建滚动内容部件
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # 搜索设置分组
        search_group = QGroupBox("搜索设置")
        search_layout = QVBoxLayout(search_group)
        
        # 文件搜索启用复选框
        self.file_search_checkbox = QCheckBox("启用搜索文件功能")
        self.file_search_checkbox.setChecked(False)  # 默认不启用
        self.file_search_checkbox.setFont(QFont(self.fonts['oppo'], 10))
        search_layout.addWidget(self.file_search_checkbox)
        
        # 搜索功能说明
        description_label = QLabel("启用后，应用将支持文件内容搜索功能")
        description_label.setFont(QFont(self.fonts['oppo'], 10))
        description_label.setWordWrap(True)
        search_layout.addWidget(description_label)
        
        # 添加搜索设置到滚动布局
        scroll_layout.addWidget(search_group)
        
        scroll_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 添加滚动区域到布局
        layout.addWidget(scroll_area)
    
    def create_buttons_tab(self):
        """创建按钮设置选项卡"""
        self.buttons_tab = QWidget()
        layout = QVBoxLayout(self.buttons_tab)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建滚动内容部件
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # 按钮设置分组 - 已移除排序功能
        buttons_group = QGroupBox("按钮设置")
        buttons_layout = QVBoxLayout(buttons_group)
        
        # 添加说明文本
        info_label = QLabel("按钮顺序调整功能已移除")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont(self.fonts['oppo'], 10))
        buttons_layout.addWidget(info_label)
        
        # 添加按钮设置到滚动布局
        scroll_layout.addWidget(buttons_group)
        
        scroll_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 添加滚动区域到布局
        layout.addWidget(scroll_area)
    
    # 已移除按钮顺序相关方法
    
    def create_about_tab(self):
        """创建关于选项卡"""
        self.about_tab = QWidget()
        layout = QVBoxLayout(self.about_tab)
        layout.setAlignment(Qt.AlignCenter)
        
        # 应用标题
        app_title = QLabel("应用名称")
        app_title.setFont(QFont(self.fonts['oppo'], 16, QFont.Bold))
        app_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(app_title)
        
        # 版本号
        version_label = QLabel("版本: 1.0.0")
        version_label.setFont(QFont(self.fonts['oppo'], 10))
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # 版权信息
        copyright_label = QLabel("© 2025 保留所有权利")
        copyright_label.setFont(QFont(self.fonts['oppo'], 10))
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)
        
        # 添加垂直空白
        layout.addStretch()
    
    def load_settings(self):
        """从配置文件加载设置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 加载主题设置
                if "theme" in settings:
                    theme_map = {"system": 0, "light": 1, "dark": 2}
                    self.theme_combo.setCurrentIndex(theme_map.get(settings["theme"], 0))
                
                # 加载搜索设置
                if "search_enabled" in settings:
                    self.file_search_checkbox.setChecked(settings["search_enabled"])
                
                logger.info(f"设置已从: {self.config_path} 加载")
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            # 使用默认设置
            pass
    
    def save_settings(self):
        """保存设置"""
        # 获取主题设置
        theme_index = self.theme_combo.currentIndex()
        theme_mapping = {0: "system", 1: "light", 2: "dark"}
        theme = theme_mapping[theme_index]
        
        # 获取文件搜索设置
        file_search_enabled = self.file_search_checkbox.isChecked()
        
        # 构建设置字典 - 已移除按钮顺序设置
        settings = {
            "theme": theme,
            "search_enabled": file_search_enabled
        }
        
        # 保存到配置文件
        self.save_to_config(settings)
        
        # 发射信号
        self.theme_changed.emit(theme)
        self.search_enabled_changed.emit(file_search_enabled)
        
        # 保存成功提示
        QMessageBox.information(self, "成功", "设置已保存")
    
    def save_to_config(self, settings):
        """保存设置到配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 保存到JSON文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"设置已保存到: {self.config_path}")
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            QMessageBox.warning(self, "错误", "保存设置失败")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        event.accept()
