# 高性能搜索模块

本模块封装了基于 C 语言实现的高性能搜索与目录扫描能力，并通过 `ctypes` 在 Python 中调用。支持精确搜索、模糊搜索与二分搜索；当 C 动态库不可用时提供安全降级。

## 功能特点

- **多种搜索算法**：支持线性搜索、二分搜索和模糊搜索
- **高性能实现**：核心算法使用C语言实现，提供更快的搜索速度
- **自动回退机制**：当C语言动态链接库不可用时，自动切换到Python回退实现
- **模糊搜索**：支持基于编辑距离的模糊匹配
- **跨平台支持**：提供了跨平台的编译脚本

## 目录结构

```
search/
├── search_wrapper.py         # 动态库加载与 Python 封装
├── libsearch.*               # 搜索动态库（平台自动命名）
├── libdirectory_scanner.*    # 目录扫描动态库（平台自动命名）
└── README.md

c_library/
├── search.c                  # 搜索算法（C）
├── search.h                  # 头文件（C）
├── directory_scanner.c       # 目录扫描（C）
└── build_search_lib.py       # 跨平台编译脚本
```

## 使用方法

### 基本使用

```python
from search.search_wrapper import search, is_c_search_available

# 准备搜索数据
items = ["apple", "banana", "cherry", "date", "elderberry"]

# 精确搜索
results = search(items, "banana", use_fuzzy=False)
print(f"精确搜索结果: {results}")

# 模糊搜索
results = search(items, "berrie", use_fuzzy=True, max_distance=2)
print(f"模糊搜索结果: {results}")

# 排序数据的二分搜索（更高效）
sorted_items = sorted(items)
results = search(sorted_items, "cherry", is_sorted=True, use_fuzzy=False)
print(f"二分搜索结果: {results}")

# 检查是否使用C语言实现
is_c_available = is_c_search_available()
print(f"C语言实现可用: {is_c_available}")
```

### 参数说明

- `items`: 要搜索的字符串列表
- `keyword`: 搜索关键词
- `is_sorted`: `True` 时使用二分搜索（精确匹配，需预排序）
- `use_fuzzy`: 是否启用模糊搜索
- `max_distance`: 模糊搜索的最大编辑距离

## 编译与安装

1) 安装依赖（示例使用清华镜像）：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2) 编译并复制动态库：

```bash
python3 c_library/build_search_lib.py
```

脚本会根据平台生成并复制到 `search/`：
- Windows: `search.dll`、`directory_scanner.dll`
- macOS: `libsearch.dylib`、`libdirectory_scanner.dylib`
- Linux: `libsearch.so`、`libdirectory_scanner.so`

## 运行与验证

快速验证动态库加载：

```bash
python -c "from search.search_wrapper import is_c_search_available; print(is_c_search_available())"
```

快速验证扫描功能：

```bash
python -c "from search.search_wrapper import scan_files; import os; print(len(scan_files(os.getcwd(), max_depth=1)))"
```

## 性能说明

C语言实现相比Python实现可以提供数倍到数十倍的性能提升，特别是在以下场景：
- 大型数据集（数万条以上的记录）
- 高频搜索操作
- 模糊搜索（计算编辑距离较耗时）

## 注意事项

1. 动态库文件名会根据平台自动选择，且需位于 `search/` 目录以便加载
2. 无编译器或动态库缺失时，模块会降级到 Python 实现，功能保持但性能较低
3. 非 Windows 平台默认扫描根目录 `/`，可根据需要改为 `os.path.expanduser('~')`
