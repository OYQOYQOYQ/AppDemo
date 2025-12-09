#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序主窗口模块
"""

import os
import sys
import subprocess
import logging
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
    QFrame, QScrollArea, QTextBrowser, QMessageBox, QSizePolicy, QListWidget, QListWidgetItem, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QFontDatabase, QIcon

# 导入其他模块
from .logging import LogToWidgetHandler
from .utils import load_custom_fonts

# 导入系统监控和搜索模块
from monitor.monitor import init_monitor, get_system_info
# 从monitor模块导入真实的系统监控功能
from monitor.monitor import get_system_info as get_mock_system_info
from search.search_wrapper import is_c_search_available, search_files, scan_files

logger = logging.getLogger(__name__)


class SearchResultsWindow(QMainWindow):
    """搜索结果显示窗口"""
    # 添加关闭信号，用于通知主窗口
    window_closed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("搜索结果")
        self.setGeometry(100, 100, 500, 400)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons", "mining_38202.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建标题
        title_label = QLabel("搜索结果")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建文件列表
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(300)
        layout.addWidget(self.file_list)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 打开文件按钮
        self.open_button = QPushButton("打开选中文件所在的文件夹")
        self.open_button.clicked.connect(self.open_selected_file)
        button_layout.addWidget(self.open_button)
        
        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 发出窗口关闭信号
        self.window_closed.emit()
        event.accept()
        
    def set_search_results(self, results, search_time=0.0):
        """设置搜索结果
        
        Args:
            results: 搜索结果列表
            search_time: 搜索所用时间(秒)
        """
        self.file_list.clear()
        
        # 更新标题
        for label in self.findChildren(QLabel):
            if label.text().startswith("搜索结果"):
                if search_time > 0:
                    label.setText(f"搜索结果 ({len(results)} 个文件) - 耗时: {search_time:.3f}秒")
                else:
                    label.setText(f"搜索结果 ({len(results)} 个文件)")
                break
        
        # 添加结果到列表
        for file_path in results:
            item = QListWidgetItem(file_path)
            self.file_list.addItem(item)
        
        # 自动选择第一个结果
        if self.file_list.count() > 0:
            self.file_list.setCurrentRow(0)
    
    def open_selected_file(self):
        """打开选中文件所在的文件夹"""
        current_item = self.file_list.currentItem()
        if current_item:
            file_path = current_item.text()
            folder_path = os.path.dirname(file_path)
            logger.info(f"尝试打开文件所在文件夹: {folder_path}")
            try:
                if sys.platform.startswith('win'):
                    os.startfile(folder_path)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', folder_path], check=False)
                else:
                    subprocess.run(['xdg-open', folder_path], check=False)
            except Exception as e:
                logger.error(f"打开文件夹失败: {e}")
                QMessageBox.warning(self, "错误", f"无法打开文件夹: {folder_path}")


class SearchThread(QThread):
    """异步搜索线程类"""
    search_completed = Signal(list, str, bool, float)  # 信号：搜索结果, 搜索文本, 是否由回车键触发, 搜索时间(秒)
    
    def __init__(self, button_names, search_text, triggered_by_return):
        super().__init__()
        self.button_names = button_names
        self.search_text = search_text
        self.triggered_by_return = triggered_by_return
    
    def run(self):
        """执行搜索操作"""
        import time
        start_time = time.time()
        
        try:
            # 执行搜索逻辑
            results = []
            for i, name in enumerate(self.button_names):
                if self.search_text in name:
                    results.append(i)
            
            # 计算搜索时间
            search_time = time.time() - start_time
            
            # 发送搜索完成信号
            self.search_completed.emit(results, self.search_text, self.triggered_by_return, search_time)
        except Exception as e:
            logger.error(f"异步搜索发生错误: {e}")
            # 计算搜索时间
            search_time = time.time() - start_time
            self.search_completed.emit([], self.search_text, self.triggered_by_return, search_time)


class MainWindow(QMainWindow):
    def __init__(self, fonts):
        super().__init__()
        self.fonts = fonts  # 存储字体信息
        self.setWindowTitle("MiniApp")
        self.setFixedSize(260, 260)  # 设置窗口固定大小为260x260像素，禁用放大缩小
        
        # 搜索线程相关
        self.search_thread = None
        
        # 初始化搜索数据集
        self.initialize_search_data()
        # 检查搜索实现类型
        if is_c_search_available():
            self.search_impl_type = "C实现"
        else:
            self.search_impl_type = "Python实现"
        logger.info(f"使用的搜索实现类型: {self.search_impl_type}")
        
        # 文件搜索相关变量
        self.search_files_option = False  # 是否启用文件搜索选项
        self.file_search_results = []  # 文件搜索结果
        self.file_search_list = None  # 文件搜索结果显示组件
        self.file_search_widget = None  # 文件搜索结果显示组件
        self.current_directory = os.path.expanduser("~")  # 默认搜索目录为用户主目录
        
        # 设置窗口标志，确保显示关闭按钮和最小化按钮，同时禁用最大化按钮
        self.setWindowFlags(Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        # 创建中央部件和布局
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 5, 10, 0)  # 减小顶部边距至5px，进一步使下方区域上移
        self.main_layout.setSpacing(3)  # 减小布局间距，使元素更紧凑
        
        # 创建顶部搜索区
        self.create_search_area()
        
        # 初始化搜索启用状态为False
        self.search_enabled = False
        
        # 创建下方区域
        self.create_bottom_area()
        
        # 设置中央部件
        self.setCentralWidget(self.central_widget)
        
        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons", "mining_38202.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning(f"图标文件不存在: {icon_path}")
        
        logger.info("Main window initialized")
        
        # 在后台线程中执行预扫描，但只在没有缓存文件时才扫描
        def background_pre_scan():
            try:
                import os
                from search.search_wrapper import SearchWrapper
                
                # 获取缓存文件路径
                cache_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'search', 'cache_files', 'file_cache.bin')
                
                # 检查缓存文件是否存在
                if not os.path.exists(cache_path):
                    logger.info("缓存文件不存在，开始执行文件预扫描")
                    from search.search_wrapper import pre_scan
                    file_count = pre_scan()
                    logger.info(f"文件预扫描完成，共扫描 {file_count} 个文件")
                else:
                    logger.info(f"缓存文件已存在 ({cache_path})，跳过预扫描")
            except Exception as e:
                logger.error(f"预扫描检查失败: {e}")
        
        # 创建并启动后台线程
        import threading
        self.pre_scan_thread = threading.Thread(target=background_pre_scan, daemon=True)
        self.pre_scan_thread.start()
        
        # 初始化时显示今日计划
        self.display_file_search_results()
        
        # 加载启动设置
        self.load_settings_on_startup()
    
    def create_search_area(self):
        """创建顶部搜索区域"""
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 5, 0, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("请输入搜索内容，按回车搜索")
        self.search_input.setMinimumHeight(28)
        # 设置OPPO字体
        self.search_input.setFont(QFont(self.fonts['oppo']))
        # 设置搜索框圆角效果
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 5px 0px;
            }
        """)
        
        # 添加搜索功能
        # 回车事件 - 传递参数表明是回车触发
        self.search_input.returnPressed.connect(lambda: self.on_search(triggered_by_return=True) if getattr(self, 'search_enabled', True) else self.statusBar().showMessage("搜索功能已禁用，请在设置中启用", 3000))
        
        # 添加文本变化事件处理，当搜索框为空时重置按钮显示
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        # 移除文本变化事件的自动搜索
        # 只在回车键时触发搜索
        
        search_layout.addWidget(self.search_input, 1)  # 搜索框占满整个区域
        
        self.main_layout.addWidget(search_frame)
    
    def create_bottom_area(self):
        """创建下方区域，分为左右两部分"""
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)  # 保持两个区域之间有适当间距

        # 2.1 左侧按钮区 - 使用滚动区域
        button_frame = QFrame()
        # 添加边框效果，只应用于外部框架
        button_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QFrame * {
                border: none;
            }
        """)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 创建一个独立的标题区域，将其放在滚动区域外部
        button_title = QLabel("功能按钮")
        button_title.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        button_title.setFixedHeight(45)  # 增加高度以容纳更大的文字
        # 设置OPPO字体，标题使用更大的字号和加粗
        font = QFont(self.fonts['oppo'], 12, QFont.Bold)
        button_title.setFont(font)
        
        # 创建按钮容器
        scroll_content = QWidget()
        button_layout = QVBoxLayout(scroll_content)
        button_layout.setContentsMargins(8, 3, 8, 3)  # 进一步减小垂直内边距至3px
        button_layout.setSpacing(6)
        button_layout.setAlignment(Qt.AlignTop)  # 设置按钮布局顶部对齐
        
        # 初始化按钮
        self.buttons = []
        self.init_buttons(button_layout)
        
        # 将按钮容器设置为滚动区域的widget
        scroll_area.setWidget(scroll_content)
        
        # 设置按钮框架的布局，将标题放在滚动区域外部
        button_frame_layout = QVBoxLayout(button_frame)
        button_frame_layout.setContentsMargins(0, 0, 0, 0)
        button_frame_layout.setSpacing(0)
        button_frame_layout.addWidget(button_title)
        button_frame_layout.addWidget(scroll_area)
        button_frame_layout.setStretch(0, 0)  # 标题不拉伸
        button_frame_layout.setStretch(1, 1)  # 滚动区域占据剩余空间
        
        # 创建右侧信息区
        self.info_container = QFrame()
        
        # 将左右区域添加到下方布局
        bottom_layout.addWidget(button_frame, 2)  # 左侧按钮区
        bottom_layout.addWidget(self.info_container, 3)  # 右侧信息区
        # 添加边框效果
        self.info_container.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QFrame * {
                border: none;
            }
        """)
        
        # 创建信息区布局
        container_layout = QVBoxLayout(self.info_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 创建标题栏
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        title_layout.setSpacing(0)
        
        # 添加标题
        self.content_title = QLabel("系统信息")
        self.content_title.setAlignment(Qt.AlignCenter)  # 将标题设置为居中对齐
        # 设置OPPO字体，标题使用更大的字号和加粗
        font = QFont(self.fonts['oppo'], 12, QFont.Bold)
        self.content_title.setFont(font)
        title_layout.addWidget(self.content_title)
        
        container_layout.addWidget(title_bar)
        
        # 创建内容区域，用于切换不同的显示内容
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        container_layout.addWidget(self.content_area)
        container_layout.setStretch(0, 0)  # 标题栏不拉伸
        container_layout.setStretch(1, 1)  # 内容区域占据剩余空间
        
        # 创建日志显示组件
        self.log_container = QWidget()
        self.log_container.setStyleSheet("background-color: #f9f9f9;")
        log_layout = QVBoxLayout(self.log_container)
        log_layout.setContentsMargins(12, 3, 12, 3)
        log_layout.setSpacing(6)
        
        # 使用QTextBrowser作为日志显示组件，支持滚动
        self.log_display = QTextBrowser()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 7))
        self.log_display.setStyleSheet("""
            QTextBrowser {
                background-color: #f9f9f9;
                border: none;
                color: #333333;
            }
        """)
        
        log_layout.addWidget(self.log_display)
        
        # 创建系统信息显示组件
        self.system_info_container = QWidget()
        system_info_layout = QVBoxLayout(self.system_info_container)
        system_info_layout.setContentsMargins(12, 3, 12, 3)
        system_info_layout.setSpacing(6)
        
        # 初始化系统信息标签
        self.system_info_labels = {}
        system_info_items = [
            "CPU使用率",
            "CPU温度",
            "GPU使用率",
            "GPU温度",
            "内存使用率",
            "磁盘使用率",
            "网络接收",
            "网络发送"
        ]
        
        for item in system_info_items:
            label = QLabel(f"{item}: --")
            label.setAlignment(Qt.AlignCenter)
            # 设置OPPO字体，增大字号并设置清晰的颜色
            font = QFont(self.fonts['oppo'], 8)
            label.setFont(font)
            # 设置明确的文字颜色，确保与背景有足够对比度
            label.setStyleSheet("color: #333333")
            self.system_info_labels[item] = label
            system_info_layout.addWidget(label)
        
        # 创建空白显示组件
        self.empty_container = QWidget()
        empty_layout = QVBoxLayout(self.empty_container)
        empty_layout.setContentsMargins(0, 0, 0, 0)
        
        # 将三个显示组件添加到内容布局中
        self.content_layout.addWidget(self.log_container)
        self.content_layout.addWidget(self.system_info_container)
        self.content_layout.addWidget(self.empty_container)
        
        # 默认显示系统信息，隐藏其他
        self.log_container.hide()
        self.system_info_container.show()
        self.empty_container.hide()
        
        # 初始化系统监控
        self.init_system_monitor()
        
        # 重定向日志到日志显示组件
        self.setup_log_handler()
        
        # 将下方区域添加到主布局
        self.main_layout.addLayout(bottom_layout, 0)  # 减小下方区域的空间分配
        


    
    def init_buttons(self, button_layout):
        """从配置文件初始化按钮"""
        import os
        import json
        
        # 默认按钮文本列表
        default_order = ["设置", "功能2", "功能3", "功能4", "功能5", "功能6", "功能7", "功能8"]
        button_texts = default_order
        
        # 尝试从配置文件加载按钮顺序
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if "button_order" in settings and isinstance(settings["button_order"], list):
                        button_texts = settings["button_order"]
                        logger.info(f"从配置文件加载按钮顺序: {button_texts}")
        except Exception as e:
            logger.error(f"加载按钮顺序失败: {e}")
        
        # 创建按钮
        self.buttons = []
        for i, text in enumerate(button_texts):
            btn = QPushButton(text)
            btn.setMinimumHeight(28)  # 减小按钮高度
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # 按钮水平方向填满可用空间
            # 设置OPPO字体，按钮使用适中的字号
            btn.setFont(QFont(self.fonts['oppo'], 10))
            
            # 为按钮设置ID（从1开始）
            btn_id = i + 1
            btn.clicked.connect(lambda checked, n=btn_id: self.on_button_clicked(n))
            
            # 添加底部边框，除了最后一个按钮
            if i < len(button_texts) - 1:
                btn.setStyleSheet("""
                    QPushButton {
                        border-bottom: 1px solid #ccc;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                """)
            
            button_layout.addWidget(btn)
            self.buttons.append(btn)
        
        # 更新搜索项目列表以匹配按钮顺序
        self.search_items = button_texts.copy()
    
    def setup_log_handler(self):
        """设置日志处理器，将日志输出到UI组件"""
        from logging.handlers import QueueHandler, QueueListener
        from queue import Queue
        
        # 创建日志队列
        self.log_queue = Queue()
        
        # 创建队列处理器并添加到根日志器
        queue_handler = QueueHandler(self.log_queue)
        logger.root.addHandler(queue_handler)
        
        # 创建队列监听器，将日志输出到UI
        self.log_listener = QueueListener(
            self.log_queue, 
            LogToWidgetHandler(self.log_display),
            respect_handler_level=True
        )
        self.log_listener.start()
    
    def scan_directory(self, directory):
        """扫描指定目录的文件"""
        try:
            logger.info(f"开始扫描目录: {directory}")
            scan_files(directory, depth=2, include_extensions=[".txt", ".pdf", ".docx", ".xlsx", ".jpg", ".png", ".py", ".js", ".html"])
            logger.info(f"目录扫描完成: {directory}")
        except Exception as e:
            logger.error(f"目录扫描失败: {e}")

    # 移除了on_display_option_changed方法，系统信息始终显示
    
    def init_system_monitor(self):
        """初始化系统监控模块"""
        logger.info("初始化系统监控模块")
        
        # 初始化真实监控模块
        try:
            self.monitor = init_monitor()
            logger.info("系统监控模块初始化成功")
        except Exception as e:
            logger.error(f"系统监控模块初始化失败: {e}")
            self.monitor = None
        
        # 设置定时器，定期更新系统信息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(2000)  # 2秒更新一次，优化性能
        
        # 立即更新一次
        self.update_system_info()
    
    def update_system_info(self):
        """更新系统信息显示"""
        try:
            # 优先使用真实监控数据
            if self.monitor:
                system_data = get_system_info()
                logger.debug(f"使用真实监控数据: {system_data}")
            else:
                # 备用使用模拟数据
                system_data = get_mock_system_info()
                logger.debug(f"使用模拟监控数据: {system_data}")
            
            # 批量更新UI，减少重绘
            self.setUpdatesEnabled(False)
            
            # 更新UI显示
            updates = {
                "CPU使用率": f"CPU使用率: {system_data.get('cpu_usage', 'N/A')}%",
                "CPU温度": f"CPU温度: {system_data.get('cpu_temp', 'N/A')}°C",
                "GPU使用率": f"GPU使用率: {system_data.get('gpu_usage', 'N/A')}%",
                "GPU温度": f"GPU温度: {system_data.get('gpu_temp', 'N/A')}°C",
                "内存使用率": f"内存使用率: {system_data.get('memory_usage', 'N/A')}%",
                "磁盘使用率": f"磁盘使用率: {system_data.get('disk_usage', 'N/A')}%",
                "网络接收": f"网络接收: {system_data.get('network_rx', 'N/A')} KB/s",
                "网络发送": f"网络发送: {system_data.get('network_tx', 'N/A')} KB/s"
            }
            
            for key, value in updates.items():
                if key in self.system_info_labels:
                    self.system_info_labels[key].setText(value)
            
            # 恢复UI更新
            self.setUpdatesEnabled(True)
                
        except Exception as e:
            logger.error(f"更新系统信息失败: {e}")
            # 出错时使用模拟数据作为备用
            try:
                system_data = get_mock_system_info()
                
                # 批量更新UI
                self.setUpdatesEnabled(False)
                
                updates = {
                    "CPU使用率": f"CPU使用率: {system_data.get('cpu_usage', 'N/A')}%",
                    "CPU温度": f"CPU温度: {system_data.get('cpu_temp', 'N/A')}°C",
                    "GPU使用率": f"GPU使用率: {system_data.get('gpu_usage', 'N/A')}%",
                    "GPU温度": f"GPU温度: {system_data.get('gpu_temp', 'N/A')}°C",
                    "内存使用率": f"内存使用率: {system_data.get('memory_usage', 'N/A')}%",
                    "磁盘使用率": f"磁盘使用率: {system_data.get('disk_usage', 'N/A')}%",
                    "网络接收": f"网络接收: {system_data.get('network_rx', 'N/A')} KB/s",
                    "网络发送": f"网络发送: {system_data.get('network_tx', 'N/A')} KB/s"
                }
                
                for key, value in updates.items():
                    if key in self.system_info_labels:
                        self.system_info_labels[key].setText(value)
                
                # 恢复UI更新
                self.setUpdatesEnabled(True)
            except Exception as backup_e:
                logger.error(f"使用备用模拟数据失败: {backup_e}")
                pass
    
    def initialize_search_data(self):
        """初始化搜索数据集"""
        # 仅包含按钮相关内容
        self.search_items = [
            "设置", "功能2", "功能3", "功能4", 
            "功能5", "功能6", "功能7", "功能8",
            "按钮1", "按钮2", "按钮3", "按钮4", 
            "按钮5", "按钮6", "按钮7", "按钮8"
        ]
        # 预排序数据用于二分搜索
        self.sorted_items = sorted(self.search_items)
    
    def on_search(self, triggered_by_return: bool):
        """搜索功能处理函数
        
        Args:
            triggered_by_return: 是否由回车键触发
        """
        # 检查搜索功能是否启用
        if not getattr(self, 'search_enabled', True):
            self.statusBar().showMessage("搜索功能已禁用，请在设置中启用", 3000)
            # 即使禁用也允许点击搜索按钮，但不执行搜索操作
            return
            
        text = self.search_input.text()
        
        # 如果搜索框为空，显示所有按钮
        if not text:
            self.reset_buttons()
            return
            
        logger.info(f"搜索内容: {text} (使用{self.search_impl_type})")
        
        # 停止当前正在运行的搜索线程
        if self.search_thread and self.search_thread.isRunning():
            self.search_thread.quit()
            self.search_thread.wait()
        
        # 创建并启动新的搜索线程
        button_names = [btn.text() for btn in self.buttons]
        self.search_thread = SearchThread(button_names, text, triggered_by_return)
        self.search_thread.search_completed.connect(self.on_search_completed)
        self.search_thread.start()
    
    def on_search_completed(self, results, search_text, triggered_by_return, button_search_time):
        """搜索完成后的处理函数
        
        Args:
            results: 搜索结果列表
            search_text: 搜索文本
            triggered_by_return: 是否由回车键触发
            button_search_time: 按钮搜索所用时间(秒)
        """
        import time
        # 检查搜索文本是否与当前输入一致，避免显示过时结果
        if search_text != self.search_input.text():
            return
            
        # 显示匹配的按钮，隐藏不匹配的按钮
        self.setUpdatesEnabled(False)  # 禁用UI更新，减少重绘
        
        for i, btn in enumerate(self.buttons):
            if i in results:
                btn.show()
            else:
                btn.hide()
        
        # 搜索整个电脑
        file_search_start_time = time.time()
        try:
            logger.info(f"开始文件搜索: {search_text}")
            
            # 使用缓存搜索（不指定目录）
            self.file_search_results = search_files(keyword=search_text, depth=3)
            
            logger.info(f"文件搜索结果: {len(self.file_search_results)} 个文件")
        except Exception as e:
            logger.error(f"文件搜索失败: {e}")
            self.file_search_results = []
        
        file_search_time = time.time() - file_search_start_time
        total_search_time = button_search_time + file_search_time
        logger.info(f"搜索时间 - 按钮: {button_search_time:.3f}秒, 文件: {file_search_time:.3f}秒, 总计: {total_search_time:.3f}秒")
        
        self.setUpdatesEnabled(True)  # 启用UI更新
        
        # 如果有文件搜索结果，在新窗口中显示
        if self.file_search_results:
            # 在新窗口中显示搜索结果
            if not hasattr(self, "search_results_window") or not self.search_results_window.isVisible():
                self.search_results_window = SearchResultsWindow(self)
                # 连接窗口关闭信号
                self.search_results_window.window_closed.connect(self.on_search_results_closed)
            self.search_results_window.set_search_results(self.file_search_results, total_search_time)
            self.search_results_window.show()
            self.search_results_window.raise_()  # 确保窗口在最前面
            # 隐藏主窗口
            self.hide()
        
        # 如果是回车键触发的搜索，根据结果数量执行不同操作
        if triggered_by_return:
            if len(results) == 1 and len(self.file_search_results) == 0:
                # 只有一个搜索结果，自动触发对应按钮
                button_index = results[0]
                button_name = [btn.text() for btn in self.buttons][button_index]
                logger.info(f"自动触发按钮: {button_name}")
                self.on_button_clicked(button_index + 1)  # button_id从1开始
    
    def display_file_search_results(self):
        """显示今日计划"""
        # 清空现有内容
        if self.file_search_widget:
            self.file_search_widget.hide()
            self.file_search_widget.deleteLater()
        
        # 清空空白容器的现有内容
        while self.empty_container.layout().count() > 0:
            item = self.empty_container.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 创建今日计划显示组件
        self.today_plan_widget = QWidget()
        layout = QVBoxLayout(self.today_plan_widget)
        
        # 创建标题
        plan_title = QLabel("今日计划")
        plan_title.setFont(QFont(self.fonts['oppo'], 12, QFont.Bold))
        plan_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(plan_title)
        
        # 创建计划内容区域
        plan_content = QLabel("计划内容将在这里显示")
        plan_content.setFont(QFont(self.fonts['oppo'], 10))
        plan_content.setAlignment(Qt.AlignCenter)
        plan_content.setMinimumHeight(100)
        layout.addWidget(plan_content)
        
        # 将今日计划组件添加到空白容器中
        container_layout = self.empty_container.layout()
        container_layout.addWidget(self.today_plan_widget)
    
        # 清理搜索线程
        self.search_thread = None
    
    def reset_buttons(self):
        """重置所有按钮的显示状态"""
        logger.info("重置所有按钮显示状态")
        for btn in self.buttons:
            btn.show()
    
    def on_search_text_changed(self):
        """搜索框文本变化事件处理"""
        # 当搜索框为空时，重置按钮显示
        if not self.search_input.text():
            self.reset_buttons()
    
    def on_button_clicked(self, button_id):
        """按钮点击事件"""
        if button_id == 1:
            logger.info("设置按钮被点击")
            self.open_settings_window()
        else:
            logger.info(f"功能{button_id}被点击")
            QMessageBox.information(self, "功能按钮", f"你点击了功能{button_id}")
    
    def open_settings_window(self):
        """打开设置窗口"""
        from ui.views.settings_window import SettingsWindow
        
        # 检查设置窗口是否已存在，如果存在则显示，否则创建新窗口
        if not hasattr(self, "settings_window") or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(self)
            # 连接主题变化信号
            self.settings_window.theme_changed.connect(self.apply_theme)
            # 连接搜索功能状态变化信号
            self.settings_window.search_enabled_changed.connect(self.update_search_enabled)
        
        self.settings_window.show()
        self.settings_window.raise_()  # 确保窗口在最前面
    
    def apply_theme(self, theme):
        """应用主题设置
        
        Args:
            theme: 主题类型 ('system', 'light', 'dark')
        """
        logger.info(f"应用主题: {theme}")
        
        # 获取对应的样式表
        from ui.utils import get_theme_stylesheet
        stylesheet = get_theme_stylesheet(theme)
        
        # 应用样式表到整个应用
        self.setStyleSheet(stylesheet)
        
        # 应用到所有子窗口
        for window in self.findChildren(self.__class__.__base__):
            if window != self and hasattr(window, 'objectName') and window.objectName() not in ['central_widget']:
                window.setStyleSheet(stylesheet)
    
    def update_search_enabled(self, enabled):
        """更新搜索功能启用状态"""
        logger.info(f"更新搜索功能状态: {'启用' if enabled else '禁用'}")
        
        # 保存状态到实例变量
        self.search_enabled = enabled
        
        # 保留其他UI元素的启用状态，但始终允许搜索按钮可点击
        if hasattr(self, 'search_button'):
            self.search_button.setEnabled(True)  # 始终允许点击搜索按钮
        
        # 如果禁用搜索功能，清空搜索框
        if not enabled and hasattr(self, 'search_input'):
            self.search_input.clear()
            # 可以在这里添加显示提示信息的逻辑
            self.statusBar().showMessage("搜索功能已禁用，请在设置中启用", 3000)
    
    def load_settings_on_startup(self):
        """启动时加载设置"""
        try:
            import os
            import json
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.json")
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 应用保存的主题设置
                if "theme" in settings:
                    self.apply_theme(settings["theme"])
                
                # 应用搜索功能设置
                if "search_enabled" in settings:
                    self.update_search_enabled(settings["search_enabled"])
                
                logger.info("启动设置已加载")
        except Exception as e:
            logger.error(f"加载启动设置失败: {e}")
            # 使用默认设置
            pass
    
    def on_search_results_closed(self):
        """处理搜索结果窗口关闭事件"""
        logger.info("搜索结果窗口已关闭，显示主窗口")
        # 显示主窗口
        self.show()
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止定时器
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        event.accept()
