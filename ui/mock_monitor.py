#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控模块，包含系统信息获取相关功能
"""

import logging
import random

logger = logging.getLogger(__name__)

def get_mock_system_info():
    """
    生成模拟的系统信息数据
    """
    return {
        "cpu_usage": random.randint(0, 100),
        "cpu_temp": random.randint(30, 70),
        "gpu_usage": random.randint(0, 100),
        "gpu_temp": random.randint(30, 80),
        "memory_usage": random.randint(0, 100),
        "disk_usage": random.randint(0, 100),
        "network_rx": random.randint(0, 1000),
        "network_tx": random.randint(0, 1000)
    }
