import os
import sys
import time
from datetime import datetime

# 导入Python系统监控库
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("警告: 未安装psutil库，无法获取真实系统数据")
    PSUTIL_AVAILABLE = False

# 尝试导入温度监控相关库
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    print("警告: 未安装wmi库，无法获取精确的CPU温度")
    WMI_AVAILABLE = False

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    print("警告: 未安装GPUtil库，无法获取精确的GPU信息")
    GPU_AVAILABLE = False

class SystemMonitor:
    def __init__(self):
        print("系统监控模块初始化中...")
        
        # 检查psutil是否可用
        if PSUTIL_AVAILABLE:
            self.initialized = True
            print("系统监控模块初始化成功，使用Python库获取真实系统数据")
            
            # 初始化网络监控的基准值
            self.last_net_io = psutil.net_io_counters()
            self.last_time = time.time()
            
            # 初始化WMI（如果可用）
            self.wmi_service = None
            if WMI_AVAILABLE:
                try:
                    self.wmi_service = wmi.WMI()
                except Exception as e:
                    print(f"WMI初始化失败: {e}")
                    self.wmi_service = None
            
            # 初始化GPU监控（如果可用）
            if GPU_AVAILABLE:
                try:
                    GPUtil.getGPUs()
                except Exception as e:
                    print(f"GPU监控初始化失败: {e}")
        else:
            print("使用模拟数据模式")
            self.initialized = False
        
        # 模拟数据的初始值（备用）
        self.sim_cpu_usage = 0
        self.sim_memory_usage = 0
        self.sim_disk_usage = 0
        self.sim_network_rx = 0
        self.sim_network_tx = 0
    
    def get_system_data(self):
        """获取系统监控数据"""
        
        # Python实现路径
        if self.initialized and PSUTIL_AVAILABLE:
            try:
                # 使用Python库获取真实数据
                data = self._get_real_system_data()
                # 添加时间戳
                data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return data
            except Exception as e:
                print(f"获取系统数据时出错: {e}")
                # 出错时返回模拟数据
                data = self._get_simulated_data()
                data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return data
        else:
            # 返回模拟数据
            data = self._get_simulated_data()
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return data
    

    
    def _get_real_system_data(self):
        """使用psutil获取真实的系统数据"""
        data = {}
        
        # 获取CPU使用率
        data['cpu_usage'] = psutil.cpu_percent(interval=0.1)
        
        # 获取内存使用率
        mem_info = psutil.virtual_memory()
        data['memory_usage'] = mem_info.percent
        
        # 获取磁盘使用率（主分区）
        disk_usage = psutil.disk_usage('/')
        data['disk_usage'] = disk_usage.percent
        
        # 计算网络速度
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_time
        
        if time_diff > 0:
            # 计算接收和发送速度（KB/s）
            rx_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024 / time_diff
            tx_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024 / time_diff
            
            # 更新基准值
            self.last_net_io = current_net_io
            self.last_time = current_time
        else:
            rx_speed = 0
            tx_speed = 0
        
        data['network_rx'] = rx_speed
        data['network_tx'] = tx_speed
        
        # 获取CPU温度
        data['cpu_temp'] = self._get_cpu_temperature()
        
        # 获取GPU信息
        gpu_info = self._get_gpu_info()
        data['gpu_usage'] = gpu_info['usage']
        data['gpu_temp'] = gpu_info['temp']
        
        # 四舍五入到合适的精度
        data['cpu_usage'] = round(data['cpu_usage'], 1)
        data['memory_usage'] = round(data['memory_usage'], 1)
        data['disk_usage'] = round(data['disk_usage'], 1)
        data['network_rx'] = round(data['network_rx'], 1)
        data['network_tx'] = round(data['network_tx'], 1)
        
        return data
    
    def _get_cpu_temperature(self):
        """获取CPU温度（跨平台实现）"""
        # Windows平台使用WMI
        if sys.platform == 'win32' and self.wmi_service:
            try:
                # 尝试获取CPU温度传感器数据
                temperature_info = self.wmi_service.Win32_PerfFormattedData_Counters_ThermalZoneInformation()
                for temp in temperature_info:
                    # 将开尔文转换为摄氏度（近似值）
                    celsius = int(100 - temp.Temperature)  # 这是一个近似值，实际需要根据具体传感器调整
                    if 0 < celsius < 100:  # 确保温度在合理范围内
                        return celsius
            except Exception as e:
                print(f"获取CPU温度失败: {e}")
        # macOS平台使用sysctl或ioreg
        elif sys.platform == 'darwin':
            try:
                # 使用ioreg命令获取温度
                import subprocess
                result = subprocess.run(['ioreg', '-rc', 'AppleSmartBattery'], capture_output=True, text=True)
                output = result.stdout
                # 查找温度信息
                for line in output.split('\n'):
                    if 'Temperature' in line:
                        temp_str = line.split('=')[1].strip()
                        # 温度值以0.1K为单位，转换为°C
                        celsius = int(float(temp_str) / 10 - 273.15)
                        if 0 < celsius < 100:
                            return celsius
            except Exception as e:
                print(f"获取macOS CPU温度失败: {e}")
        # Linux平台读取/sys/class/thermal/目录
        elif sys.platform.startswith('linux'):
            try:
                import glob
                # 查找所有thermal zone
                thermal_files = glob.glob('/sys/class/thermal/thermal_zone*/temp')
                for file_path in thermal_files:
                    try:
                        with open(file_path, 'r') as f:
                            temp_str = f.read().strip()
                            celsius = int(temp_str) // 1000  # 温度值以m°C为单位
                            if 0 < celsius < 100:
                                return celsius
                    except Exception as e:
                        print(f"读取温度文件失败 {file_path}: {e}")
            except Exception as e:
                print(f"获取Linux CPU温度失败: {e}")
        
        # 如果无法获取真实温度，返回一个合理的默认值
        return 45  # 默认45°C
    
    def _get_gpu_info(self):
        """获取GPU信息"""
        usage = 0
        temp = 50
        
        # 使用GPUtil尝试获取GPU信息
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    # 使用第一个GPU的数据
                    gpu = gpus[0]
                    usage = gpu.load * 100  # 转换为百分比
                    temp = gpu.temperature
            except Exception as e:
                print(f"获取GPU信息失败: {e}")
        
        return {
            'usage': round(usage, 1),
            'temp': int(temp)
        }
    
    def _get_simulated_data(self):
        """生成模拟的系统数据，用于测试"""
        # 简单的模拟数据变化
        import random
        
        # CPU使用率模拟 (10-90%之间随机变化)
        self.sim_cpu_usage = max(10, min(90, self.sim_cpu_usage + (random.random() - 0.5) * 5))
        
        # 内存使用率模拟 (30-80%之间随机变化)
        self.sim_memory_usage = max(30, min(80, self.sim_memory_usage + (random.random() - 0.5) * 2))
        
        # 磁盘使用率模拟 (50-85%之间)
        self.sim_disk_usage = max(50, min(85, self.sim_disk_usage + (random.random() - 0.5) * 0.5))
        
        # 网络速度模拟 (0-1000 KB/s之间)
        self.sim_network_rx = random.randint(0, 1000)
        self.sim_network_tx = random.randint(0, 200)
        
        return {
            'cpu_usage': round(self.sim_cpu_usage, 1),
            'cpu_temp': random.randint(35, 60),  # 模拟CPU温度
            'gpu_usage': random.randint(0, 100),  # 模拟GPU使用率
            'gpu_temp': random.randint(30, 70),  # 模拟GPU温度
            'memory_usage': round(self.sim_memory_usage, 1),
            'disk_usage': round(self.sim_disk_usage, 1),
            'network_rx': self.sim_network_rx,
            'network_tx': self.sim_network_tx
        }

# 创建监控实例
system_monitor = None

def init_monitor():
    """初始化系统监控模块"""
    global system_monitor
    system_monitor = SystemMonitor()
    # Python实现不需要额外的初始化调用
    return system_monitor

def get_system_info():
    """获取系统信息的便捷函数"""
    global system_monitor
    if system_monitor is None:
        system_monitor = init_monitor()
    return system_monitor.get_system_data()

def get_system_data():
    """获取系统监控数据（与旧接口兼容）"""
    data = get_system_info()
    # 返回与旧C接口相同格式的元组
    return (
        data['cpu_usage'],
        data['cpu_temp'],
        data['gpu_usage'],
        data['gpu_temp'],
        data['memory_usage'],
        data['disk_usage'],
        data['network_rx'],
        data['network_tx']
    )

# 获取当前实现类型
def get_implementation_type():
    """获取当前使用的实现类型"""
    global system_monitor
    if system_monitor is None:
        system_monitor = init_monitor()
    if system_monitor.initialized and PSUTIL_AVAILABLE:
        return "Python实现（psutil）"
    else:
        return "Python实现（模拟数据）"

# 测试代码
if __name__ == "__main__":
    monitor = init_monitor()
    data = get_system_info()
    print("系统信息:")
    for key, value in data.items():
        if key.endswith('usage'):
            print(f"{key}: {value}%")
        elif key.endswith('temp'):
            print(f"{key}: {value}°C")
        elif key.startswith('network'):
            print(f"{key}: {value} KB/s")
