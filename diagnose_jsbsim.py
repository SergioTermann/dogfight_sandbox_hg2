#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
JSBSim 安装诊断工具
帮助找出 JSBSim 的数据文件位置和可用飞机
"""

import os
import sys

print("=" * 70)
print("JSBSim 安装诊断工具")
print("=" * 70)
print()

# 1. 检查 JSBSim 是否安装
print("1. 检查 JSBSim 安装...")
try:
    import jsbsim
    print(f"   ✅ JSBSim 已安装")
    if hasattr(jsbsim, '__version__'):
        print(f"   版本: {jsbsim.__version__}")
    else:
        print(f"   版本: Unknown (可能是旧版本)")
except ImportError:
    print("   ❌ JSBSim 未安装")
    print("   请运行: pip install jsbsim")
    sys.exit(1)

print()

# 2. 查找 JSBSim 模块路径
print("2. JSBSim 模块路径...")
jsbsim_path = os.path.dirname(jsbsim.__file__)
print(f"   {jsbsim_path}")
print()

# 3. 查找数据目录
print("3. 查找 JSBSim 数据目录...")
possible_paths = [
    jsbsim_path,
    os.path.join(jsbsim_path, 'data'),
    os.path.join(jsbsim_path, '..', 'JSBSim'),
    os.path.join(jsbsim_path, '..', 'share', 'jsbsim'),
]

data_dirs = []
for path in possible_paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        # 检查是否有 aircraft 目录
        aircraft_dir = os.path.join(abs_path, 'aircraft')
        if os.path.exists(aircraft_dir):
            data_dirs.append(abs_path)
            print(f"   ✅ 找到: {abs_path}")

if not data_dirs:
    print("   ❌ 未找到数据目录！")
    print()
    print("   可能的原因：")
    print("   1. JSBSim 安装不完整")
    print("   2. 需要单独下载数据文件")
    print()
    print("   解决方案：")
    print("   1. 重新安装: pip uninstall jsbsim && pip install jsbsim")
    print("   2. 或从 GitHub 下载数据: https://github.com/JSBSim-Team/jsbsim")
    sys.exit(1)

print()

# 4. 列出可用飞机
print("4. 扫描可用飞机型号...")
all_aircraft = set()

for data_dir in data_dirs:
    aircraft_dir = os.path.join(data_dir, 'aircraft')
    if os.path.exists(aircraft_dir):
        try:
            for item in os.listdir(aircraft_dir):
                item_path = os.path.join(aircraft_dir, item)
                if os.path.isdir(item_path):
                    # 检查是否有对应的 .xml 文件
                    xml_file = os.path.join(item_path, f"{item}.xml")
                    if os.path.exists(xml_file):
                        all_aircraft.add(item)
                        print(f"   ✅ {item} ({xml_file})")
        except Exception as e:
            print(f"   ⚠️ 扫描 {aircraft_dir} 失败: {e}")

if not all_aircraft:
    print("   ❌ 未找到任何飞机配置文件！")
    print()
    print("   JSBSim 安装可能不完整，建议重新安装。")
    sys.exit(1)

print()
print(f"   找到 {len(all_aircraft)} 个飞机型号")
print()

# 5. 测试加载飞机
print("5. 测试加载飞机...")
test_aircraft = list(all_aircraft)[:3]  # 测试前3个

fdm = jsbsim.FGFDMExec(None)
fdm.set_root_dir(data_dirs[0])

success_count = 0
for aircraft_name in test_aircraft:
    try:
        if fdm.load_model(aircraft_name):
            print(f"   ✅ {aircraft_name} 加载成功")
            success_count += 1
            # 重新创建 FDM 用于下一个测试
            fdm = jsbsim.FGFDMExec(None)
            fdm.set_root_dir(data_dirs[0])
        else:
            print(f"   ❌ {aircraft_name} 加载失败")
    except Exception as e:
        print(f"   ❌ {aircraft_name} 加载失败: {e}")

print()

# 6. 总结和建议
print("=" * 70)
print("诊断结果总结")
print("=" * 70)
print()

if success_count > 0:
    print("✅ JSBSim 工作正常！")
    print()
    print("推荐使用的飞机型号：")
    recommended = ["c172p", "c172", "f16", "x15", "737"]
    for rec in recommended:
        if rec in all_aircraft:
            print(f"  - {rec}")
    print()
    print("在程序中启用 JSBSim：")
    print("  1. 运行程序")
    print("  2. 按 F12 打开设置")
    print("  3. 勾选 'Use JSBSim'")
    print("  4. 选择飞机型号")
    print("  5. 重启任务")
else:
    print("❌ JSBSim 无法正常加载飞机")
    print()
    print("建议：")
    print("  1. 重新安装 JSBSim:")
    print("     pip uninstall jsbsim")
    print("     pip install jsbsim")
    print()
    print("  2. 如果仍然失败，使用简化物理模型（不启用 JSBSim）")

print()
print("=" * 70)

# 7. 生成配置建议
if success_count > 0:
    print()
    print("建议的配置（source/master.py）：")
    print("-" * 70)
    print("flag_use_jsbsim = True")
    if "c172p" in all_aircraft:
        print('jsbsim_aircraft_type = "c172p"  # 推荐：稳定易飞')
    elif "f16" in all_aircraft:
        print('jsbsim_aircraft_type = "f16"  # 战斗机')
    else:
        first_aircraft = list(all_aircraft)[0]
        print(f'jsbsim_aircraft_type = "{first_aircraft}"')
    print("-" * 70)


