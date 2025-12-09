#!/usr/bin/env python3
"""
编译搜索库脚本
用于将C语言实现的搜索算法编译为动态链接库
"""
import os
import sys
import subprocess
import platform

def build_library():
    """根据平台编译动态链接库"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # C源文件和头文件
    source_files = ['search.c', 'directory_scanner.c']
    header_files = ['search.h', 'directory_scanner.h']
    
    # 根据平台设置输出文件名和编译命令
    if platform.system() == 'Windows':
        output_name = 'search.dll'
        compiler = 'gcc' if check_command('gcc') else 'cl'
        
        if compiler == 'gcc':
            cmd = [
                'gcc',
                '-shared',
                '-o', output_name,
                '-Wl,--out-implib,libsearch.a',
                '-Wl,--export-all-symbols',
                '-Wl,--enable-auto-import',
                '-O2',
                *source_files
            ]
        else:  # MSVC cl
            cmd = [
                'cl',
                '/LD',
                '/Fe:' + output_name,
                '/Ox',
                *source_files
            ]
    elif platform.system() == 'Darwin':
        output_name = 'libsearch.dylib'
        cmd = [
            'gcc',
            '-shared',
            '-o', output_name,
            '-fPIC',
            '-O2',
            *source_files
        ]
    else:  # Linux
        output_name = 'libsearch.so'
        cmd = [
            'gcc',
            '-shared',
            '-o', output_name,
            '-fPIC',
            '-O2',
            *source_files
        ]
    
    # 检查源文件是否存在
    for file in source_files + header_files:
        if not os.path.exists(os.path.join(current_dir, file)):
            print(f"错误: 文件不存在: {file}")
            return False
    
    # 执行编译命令
    print(f"开始编译搜索库: {output_name}")
    print(f"编译命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, cwd=current_dir, check=True)
        print(f"编译成功! 输出文件: {os.path.join(current_dir, output_name)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"编译失败! 错误代码: {e.returncode}")
        print("请确保已安装编译器 (gcc 或 MSVC)")
        return False
    except Exception as e:
        print(f"编译出错: {e}")
        return False

def check_command(command):
    """检查命令是否可用"""
    try:
        subprocess.run([command, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def main():
    print("搜索库编译工具")
    print("=" * 50)
    
    # 检查是否需要安装编译器
    if platform.system() == 'Windows':
        if not check_command('gcc') and not check_command('cl'):
            print("提示: 未找到编译器。请安装MinGW (gcc) 或 Visual Studio (cl)。")
            print("建议安装MinGW-w64，然后将其bin目录添加到系统PATH中。")
            return 1
    else:
        if not check_command('gcc'):
            print("提示: 未找到gcc编译器。请先安装gcc。")
            print("Linux/Debian/Ubuntu: sudo apt-get install gcc")
            print("macOS: xcode-select --install")
            return 1
    
    # 执行编译
    if build_library():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
