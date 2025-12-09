# 高性能搜索模块

本模块提供了基于C语言实现的高性能搜索算法，支持精确搜索、模糊搜索和二分搜索，并包含Python回退实现，确保在无法使用C编译的环境中也能正常工作。

## 功能特点

- **多种搜索算法**：支持线性搜索、二分搜索和模糊搜索
- **高性能实现**：核心算法使用C语言实现，提供更快的搜索速度
- **自动回退机制**：当C语言动态链接库不可用时，自动切换到Python回退实现
- **模糊搜索**：支持基于编辑距离的模糊匹配
- **跨平台支持**：提供了跨平台的编译脚本

## 目录结构

```
search/
├── search.c            # C语言实现的搜索算法
├── search.h            # C语言头文件
├── search_wrapper.py   # Python与C交互的封装层
├── build_search_lib.py # 编译脚本
├── test_search.py      # 测试脚本
├── __init__.py         # Python模块初始化文件
└── README.md           # 本说明文件
```

## 使用方法

### 基本使用

```python
from search import search, is_c_search_available

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
- `query`: 搜索关键词
- `is_sorted`: 指示items是否已排序，如果为True且use_fuzzy为False，将使用二分搜索
- `use_fuzzy`: 是否启用模糊搜索
- `max_distance`: 模糊搜索时的最大编辑距离，默认为1

## 编译C语言实现

### Windows平台

1. 安装MinGW-w64或Visual Studio
2. 将编译器添加到系统PATH
3. 运行编译脚本：

```bash
python search/build_search_lib.py
```

### Linux/macOS平台

1. 安装gcc
2. 运行编译脚本：

```bash
python search/build_search_lib.py
```

## 测试

运行测试脚本验证功能正确性：

```bash
python search/test_search.py
```

测试包括：
- 搜索功能正确性测试
- Python回退机制测试
- 边缘情况测试
- 性能测试（仅在C语言实现可用时运行）

## 性能说明

C语言实现相比Python实现可以提供数倍到数十倍的性能提升，特别是在以下场景：
- 大型数据集（数万条以上的记录）
- 高频搜索操作
- 模糊搜索（计算编辑距离较耗时）

## 注意事项

1. C语言动态链接库文件名会根据平台自动调整：
   - Windows: search.dll
   - macOS: libsearch.dylib
   - Linux: libsearch.so

2. 如果没有安装C编译器，模块会自动使用Python回退实现，保证功能正常但性能较低

3. 对于非常大的数据集，建议使用二分搜索（需要先排序）以获得最佳性能
