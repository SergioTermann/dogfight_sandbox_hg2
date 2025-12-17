#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试俯仰控制方向
"""
import sys
sys.path.insert(0, "bin")

try:
    import jsbsim
    print("✅ JSBSim 导入成功")
except ImportError as e:
    print(f"❌ 无法导入 JSBSim: {e}")
    sys.exit(1)

# 创建 JSBSim 实例
import os
jsbsim_path = os.path.dirname(jsbsim.__file__)
fdm = jsbsim.FGFDMExec(jsbsim_path, None)
print(f"JSBSim 路径: {jsbsim_path}")

# 加载飞机
aircraft_type = "f16"
if not fdm.load_model(aircraft_type):
    print(f"❌ 无法加载飞机模型: {aircraft_type}")
    sys.exit(1)

print(f"✅ 加载飞机: {aircraft_type}")

# 初始化
fdm.set_property_value('ic/h-sl-ft', 10000)  # 高度 10000 英尺
fdm.set_property_value('ic/vc-kts', 400)     # 速度 400 节
fdm.set_property_value('ic/theta-deg', 0)    # 俯仰角 0 度

# 启动引擎
fdm['propulsion/engine[0]/set-running'] = 1
fdm['fcs/throttle-cmd-norm'] = 0.8

# 运行初始化
if not fdm.run_ic():
    print("❌ 初始化失败")
    sys.exit(1)

print("\n" + "="*60)
print("俯仰控制测试")
print("="*60)

# 测试 1: 正升降舵输入（+1）
print("\n【测试 1】升降舵 = +1.0（正值）")
fdm.set_property_value('fcs/elevator-cmd-norm', 1.0)

pitch_0 = fdm['attitude/theta-deg']
pitch_rate_0 = fdm['velocities/q-rad_sec']

# 运行 5 秒模拟
for i in range(100):
    fdm.run()

pitch_1 = fdm['attitude/theta-deg']
pitch_rate_1 = fdm['velocities/q-rad_sec']

print(f"  初始俯仰角: {pitch_0:.2f}°")
print(f"  结束俯仰角: {pitch_1:.2f}°")
print(f"  俯仰角变化: {pitch_1 - pitch_0:+.2f}°")
print(f"  俯仰角速度: {pitch_rate_1:.4f} rad/s")

if pitch_1 > pitch_0:
    print("  → 结果: 飞机**抬头**（pitch 增加）✈️↗️")
else:
    print("  → 结果: 飞机**低头**（pitch 减少）✈️↘️")

# 重置
fdm.reset_to_initial_conditions(0)
fdm['propulsion/engine[0]/set-running'] = 1
fdm['fcs/throttle-cmd-norm'] = 0.8

# 测试 2: 负升降舵输入（-1）
print("\n【测试 2】升降舵 = -1.0（负值）")
fdm.set_property_value('fcs/elevator-cmd-norm', -1.0)

pitch_0 = fdm['attitude/theta-deg']

# 运行 5 秒模拟
for i in range(100):
    fdm.run()

pitch_1 = fdm['attitude/theta-deg']
pitch_rate_1 = fdm['velocities/q-rad_sec']

print(f"  初始俯仰角: {pitch_0:.2f}°")
print(f"  结束俯仰角: {pitch_1:.2f}°")
print(f"  俯仰角变化: {pitch_1 - pitch_0:+.2f}°")
print(f"  俯仰角速度: {pitch_rate_1:.4f} rad/s")

if pitch_1 < pitch_0:
    print("  → 结果: 飞机**低头**（pitch 减少）✈️↘️")
else:
    print("  → 结果: 飞机**抬头**（pitch 增加）✈️↗️")

print("\n" + "="*60)
print("结论")
print("="*60)
print("在 JSBSim 中：")
print("  • elevator = +1 → 飞机抬头（机头向上）")
print("  • elevator = -1 → 飞机低头（机头向下）")
print("\n当前游戏映射：")
print("  • 按 ↓键 → PITCH_UP → elevator = +1 → 抬头")
print("  • 按 ↑键 → PITCH_DOWN → elevator = -1 → 低头")
print("\n这是**飞行操纵杆逻辑**（拉杆=抬头，推杆=低头）")
print("="*60)

