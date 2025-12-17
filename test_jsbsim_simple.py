#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
JSBSim 简单测试（不依赖 Harfang）
"""

# 测试 JSBSim 是否可用
try:
    import jsbsim
    print("✅ JSBSim 已安装")
    print(f"   版本: {jsbsim.__version__ if hasattr(jsbsim, '__version__') else 'Unknown'}")
except ImportError:
    print("❌ JSBSim 未安装")
    print("   请运行: pip install jsbsim")
    exit(1)

print("\n" + "=" * 60)
print("测试 JSBSim 基本功能")
print("=" * 60 + "\n")

# 创建 FDM 实例
fdm = jsbsim.FGFDMExec(None)
print("1. ✅ FDM 实例创建成功")

# 设置根目录
import os
jsbsim_root = os.path.dirname(jsbsim.__file__)
fdm.set_root_dir(jsbsim_root)
print(f"2. ✅ JSBSim 根目录: {jsbsim_root}")

# 加载飞机
aircraft_name = "f16"
print(f"\n3. 尝试加载飞机: {aircraft_name}")
if fdm.load_model(aircraft_name):
    print(f"   ✅ {aircraft_name} 加载成功")
else:
    print(f"   ❌ {aircraft_name} 加载失败")
    exit(1)

# 设置初始条件
print("\n4. 设置初始条件...")
try:
    fdm.set_property_value('ic/h-sl-ft', 10000.0)
    fdm.set_property_value('ic/u-fps', 300.0)
    print("   ✅ 初始条件设置成功")
except Exception as e:
    print(f"   ❌ 设置失败: {e}")
    exit(1)

# 运行初始化
print("\n5. 运行初始化...")
if fdm.run_ic():
    print("   ✅ 初始化成功")
else:
    print("   ❌ 初始化失败")
    exit(1)

# 读取状态
print("\n6. 读取飞机状态...")
try:
    altitude = fdm.get_property_value('position/h-sl-ft')
    speed = fdm.get_property_value('velocities/u-fps')
    print(f"   ✅ 高度: {altitude:.0f} ft")
    print(f"   ✅ 速度: {speed:.0f} ft/s")
except Exception as e:
    print(f"   ❌ 读取失败: {e}")
    exit(1)

# 运行几帧模拟
print("\n7. 运行模拟...")
fdm.set_dt(1.0/60.0)
for i in range(10):
    # 设置控制
    try:
        fdm.set_property_value('fcs/throttle-cmd-norm', 0.8)
        fdm.set_property_value('fcs/elevator-cmd-norm', 0.0)
    except:
        pass
    
    # 运行一帧
    fdm.run()
    
    if i == 9:
        try:
            alt = fdm.get_property_value('position/h-sl-ft')
            spd = fdm.get_property_value('velocities/u-fps')
            print(f"   第10帧: 高度={alt:.0f} ft, 速度={spd:.0f} ft/s")
        except:
            print("   读取状态失败，但模拟继续运行")

print("\n" + "=" * 60)
print("✅ 所有测试通过！")
print("=" * 60)
print("\nJSBSim 工作正常，可以在程序中使用。")
print("\n启用方法：")
print("  1. 运行程序")
print("  2. 按 F12 打开设置")
print("  3. 勾选 'Use JSBSim (Restart Required)'")
print("  4. 选择飞机型号（F-16）")
print("  5. 重启程序或重新创建飞机")

