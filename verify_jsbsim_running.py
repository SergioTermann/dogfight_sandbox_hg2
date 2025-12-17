#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
验证程序是否真的在使用 JSBSim
"""

import sys
import os

print("=" * 60)
print("JSBSim 运行状态检查")
print("=" * 60)
print()

# 检查 1: JSBSim 模块是否安装
print("[1/5] 检查 JSBSim 模块...")
try:
    import jsbsim
    print("  ✅ JSBSim 已安装")
    version = jsbsim.__version__ if hasattr(jsbsim, '__version__') else 'Unknown'
    print(f"     版本: {version}")
except ImportError:
    print("  ❌ JSBSim 未安装！")
    sys.exit(1)

print()

# 检查 2: 配置文件
print("[2/5] 检查配置文件...")
import json
with open('config.json', 'r') as f:
    config = json.load(f)

use_jsbsim = config.get('UseJSBSim', False)
aircraft_type = config.get('JSBSimAircraft', 'N/A')

print(f"  config.json:")
print(f"    UseJSBSim: {use_jsbsim}")
print(f"    JSBSimAircraft: {aircraft_type}")

if use_jsbsim:
    print("  ✅ JSBSim 已在配置中启用")
else:
    print("  ❌ JSBSim 在配置中未启用")

print()

# 检查 3: master.py 的默认配置
print("[3/5] 检查 master.py 全局配置...")
sys.path.insert(0, 'source')
try:
    from master import Main
    
    flag_use_jsbsim = Main.flag_use_jsbsim if hasattr(Main, 'flag_use_jsbsim') else False
    jsbsim_type = Main.jsbsim_aircraft_type if hasattr(Main, 'jsbsim_aircraft_type') else 'N/A'
    
    print(f"  Main.flag_use_jsbsim: {flag_use_jsbsim}")
    print(f"  Main.jsbsim_aircraft_type: {jsbsim_type}")
    
    if flag_use_jsbsim:
        print("  ✅ master.py 中 JSBSim 已启用")
    else:
        print("  ❌ master.py 中 JSBSim 未启用")
except Exception as e:
    print(f"  ⚠️  无法读取 master.py: {e}")

print()

# 检查 4: JSBSimAdapter 是否可用
print("[4/5] 检查 JSBSimAdapter...")
try:
    from JSBSimAdapter import JSBSimAdapter, is_jsbsim_available
    
    if is_jsbsim_available():
        print("  ✅ JSBSimAdapter 可用")
        
        # 尝试创建测试实例
        try:
            test_adapter = JSBSimAdapter("f16", use_jsbsim=True)
            if test_adapter.enabled:
                print("  ✅ 测试: 成功创建 JSBSim 适配器 (F-16)")
                print(f"     初始化状态: {test_adapter.initialized}")
            else:
                print("  ⚠️  测试: JSBSim 适配器创建但未启用")
        except Exception as e:
            print(f"  ⚠️  测试失败: {e}")
    else:
        print("  ❌ JSBSimAdapter 不可用")
except Exception as e:
    print(f"  ❌ 无法导入 JSBSimAdapter: {e}")

print()

# 检查 5: 代码路径验证
print("[5/5] 检查代码执行路径...")
print("  查看 Machines.py 中的 update_kinetics()...")

with open('source/Machines.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # 检查关键代码
    if 'def update_kinetics_jsbsim' in content:
        print("  ✅ 找到 update_kinetics_jsbsim() 方法")
    else:
        print("  ❌ 未找到 update_kinetics_jsbsim() 方法")
    
    if 'if self.use_jsbsim and self.jsbsim_adapter and self.jsbsim_adapter.enabled:' in content:
        print("  ✅ 找到 JSBSim 优先检查代码")
    else:
        print("  ⚠️  未找到 JSBSim 检查代码")
    
    if 'self.update_kinetics_jsbsim(dts)' in content:
        print("  ✅ 找到 JSBSim 更新调用")
    else:
        print("  ❌ 未找到 JSBSim 更新调用")

print()
print("=" * 60)
print("诊断总结")
print("=" * 60)
print()

# 总结
all_good = True

if not use_jsbsim:
    print("⚠️  config.json 中 JSBSim 未启用")
    all_good = False

if not flag_use_jsbsim:
    print("⚠️  master.py 中 JSBSim 未启用")
    all_good = False

if all_good:
    print("✅ 所有检查通过！")
    print()
    print("JSBSim 配置正确，程序启动时应该会：")
    print()
    print("1. 看到启动日志:")
    print("   ✈️  飞机名: 已启用 JSBSim 真实飞行动力学 (型号: f16)")
    print()
    print("2. 物理解算:")
    print("   - Aircraft.__init__() 创建 JSBSimAdapter")
    print("   - update_kinetics() 检查 use_jsbsim")
    print("   - 调用 update_kinetics_jsbsim()")
    print("   - JSBSimAdapter.update() 运行 FDM")
    print()
    print("运行程序并查看启动日志来确认！")
else:
    print("⚠️  配置可能有问题，请检查上面的警告")

print()
print("=" * 60)
print("如何确认程序运行时使用了 JSBSim:")
print("=" * 60)
print()
print("方法 1: 查看启动日志")
print("  运行 start.bat 并查看控制台输出")
print("  应该看到: '✈️  飞机名: 已启用 JSBSim...'")
print()
print("方法 2: 添加调试输出")
print("  在 source/Machines.py 的 update_kinetics() 开头添加:")
print("  print(f'DEBUG: {self.name} use_jsbsim={self.use_jsbsim}')")
print()
print("方法 3: 观察飞行特性")
print("  JSBSim 的真实物理 vs 简化物理:")
print("  - JSBSim: 失速更明显，俯仰响应更慢，需要更大空速")
print("  - 简化: 飞行更稳定，响应更快，不太会失速")
print()

