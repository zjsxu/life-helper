#!/usr/bin/env python3
"""
Launcher script for PL-DSS GUI
"""

import sys
import os

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add current directory to Python path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from pl_dss.gui import main
    main()
except ImportError as e:
    print("错误：无法导入 pl_dss 模块")
    print(f"详细信息：{e}")
    print("\n请确保：")
    print("1. 在项目根目录运行此脚本")
    print("2. pl_dss 目录存在且包含所需文件")
    print(f"\n当前目录：{os.getcwd()}")
    print(f"脚本目录：{script_dir}")
    sys.exit(1)
except Exception as e:
    print(f"启动 GUI 时出错：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
