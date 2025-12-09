# Mini App

一个使用PySide6框架开发的小型桌面应用程序，支持跨平台运行（Windows、macOS、Linux）。

## 项目结构

```
miniapp/
├── main.py              # 主程序入口
├── requirements.txt     # 项目依赖
├── ui/                  # UI组件模块
│   ├── __init__.py
│   ├── main_window.py   # 主窗口类
│   ├── components.py    # UI组件类
│   ├── utils.py         # 工具函数
│   ├── logging.py       # 日志功能
│   └── mock_monitor.py  # 模拟监控数据
├── core/                # 核心业务逻辑模块
│   ├── __init__.py
│   ├── app_manager.py   # 应用程序管理器
│   └── config_manager.py # 配置管理器
├── config/              # 配置文件目录
│   ├── __init__.py
│   └── default_config.json # 默认配置文件
├── resources/           # 资源文件目录
│   ├── fonts/           # 字体文件
│   └── icons/           # 图标文件
├── search/              # 搜索功能模块
│   ├── __init__.py
│   ├── search_wrapper.py # 搜索功能封装
│   └── search.dll       # 搜索功能动态链接库（Windows）
├── c_library/           # C语言实现的核心功能
│   ├── search.c         # 搜索算法实现
│   ├── directory_scanner.c # 目录扫描实现
│   └── build_search_lib.py # 编译脚本
└── monitor/             # 系统监控模块
    ├── __init__.py
    └── monitor.py       # 系统监控实现
```

## 功能特性

- 跨平台支持（Windows、macOS、Linux）
- 260x260像素的紧凑窗口设计
- 模块化的代码结构，便于维护和扩展
- 可配置的应用程序设置
- 基本的UI交互元素
- 日志记录功能
- 文件搜索功能
- 系统监控功能（CPU、内存、磁盘、网络等）
- 自定义字体支持

## 安装说明

### 前提条件

- Python 3.8 或更高版本
- pip 包管理器
- GCC编译器（用于编译C语言代码，Windows平台可使用MinGW）

### 安装步骤

1. 克隆或下载项目到本地

2. 安装所需依赖：

   ```bash
   cd miniapp
   pip install -r requirements.txt
   ```

3. 编译C语言库（可选，已提供预编译的动态链接库）：

   ```bash
   cd c_library
   python build_search_lib.py
   ```

## 使用方法

### 运行应用程序

在项目根目录下执行以下命令：

```bash
python main.py
```

### 跨平台运行

应用程序已优化，可以在不同平台上运行：

- **Windows**: 直接运行 `python main.py`
- **macOS**: 直接运行 `python3 main.py`
- **Linux**: 直接运行 `python3 main.py`

### 应用程序操作

- 点击界面上的按钮执行相应操作
- 查看状态面板了解应用程序当前状态

## 配置说明

应用程序的默认配置存储在 `config/default_config.json` 文件中。主要配置项包括：

- `app_name`: 应用程序名称
- `version`: 应用程序版本
- `window_size`: 窗口尺寸（固定为260x260）
- `window_position`: 窗口初始位置
- `theme`: 应用程序主题
- `log_level`: 日志记录级别

运行时，应用程序会在当前目录创建 `config.json` 文件用于保存用户配置。

## 跨平台兼容性

应用程序已进行跨平台优化：

- **资源管理**: 所有资源文件（字体、图标）统一放在 `resources/` 目录下
- **路径处理**: 使用 `os.path.join` 构建路径，避免硬编码的绝对路径
- **系统API**: 根据不同平台使用相应的系统API
  - Windows: 使用Win32 API和WMI
  - macOS: 使用POSIX API和系统命令
  - Linux: 使用POSIX API和系统文件

## 功能模块说明

### 搜索功能

- 支持按文件扩展名搜索
- 支持递归扫描子目录
- 提供C语言实现的高性能搜索算法

### 系统监控

- CPU使用率和温度监控
- 内存使用率监控
- 磁盘使用率监控
- 网络速度监控
- GPU使用率和温度监控（如果可用）

## 开发说明

### 模块职责

- **ui/**: 负责所有用户界面元素的创建和管理
- **core/**: 实现应用程序的核心业务逻辑
- **config/**: 存储和管理配置文件
- **resources/**: 存放所有资源文件（字体、图标等）
- **search/**: 实现文件搜索功能
- **c_library/**: 提供高性能的C语言实现
- **monitor/**: 实现系统监控功能

### 添加新功能

1. 在适当的模块中添加新的类或函数
2. 确保遵循现有的代码风格和架构模式
3. 更新配置文件（如果需要）
4. 在主程序中集成新功能
5. 确保新功能支持跨平台运行

### 编译C语言库

如果修改了C语言源代码，需要重新编译：

```bash
cd c_library
python build_search_lib.py
```

编译脚本会根据当前平台生成相应的动态链接库：
- Windows: `search.dll` 和 `directory_scanner.dll`
- macOS: `libsearch.dylib` 和 `libdirectory_scanner.dylib`
- Linux: `libsearch.so` 和 `libdirectory_scanner.so`

## 故障排除

### 常见问题

1. **应用程序无法启动**
   - 检查是否已安装所有依赖（`pip install -r requirements.txt`）
   - 确保使用的是Python 3.8或更高版本
   - 检查PySide6是否正确安装

2. **界面显示异常**
   - 检查PySide6是否正确安装
   - 尝试重新安装依赖
   - 确保系统支持图形界面

3. **配置不生效**
   - 删除当前目录下的 `config.json` 文件，让应用程序使用默认配置

4. **搜索功能无法使用**
   - 确保C语言库已正确编译
   - 检查动态链接库文件是否存在

5. **系统监控数据异常**
   - 检查psutil库是否正确安装
   - 确保系统权限足够获取监控数据

### 日志查看

应用程序会生成日志文件记录运行日志，可以通过查看该文件了解应用程序的运行状态和错误信息。

## 版本更新日志

### 最新更新

- 实现了跨平台支持（Windows、macOS、Linux）
- 重构了项目结构，优化了资源管理
- 改进了文件搜索功能的性能
- 添加了系统监控功能
- 优化了UI界面和交互体验
- 修复了各种bug和兼容性问题

## 许可证

[MIT License](LICENSE)

## 作者

Mini App Team