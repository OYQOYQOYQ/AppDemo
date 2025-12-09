"""
搜索模块
提供高性能的C语言实现的搜索功能
"""

# 从wrapper中导出主要功能
from .search_wrapper import SearchWrapper, search, is_c_search_available

__all__ = [
    'SearchWrapper',
    'search',
    'is_c_search_available'
]
__version__ = '1.0.0'