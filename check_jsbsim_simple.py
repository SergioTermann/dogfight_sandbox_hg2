#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
简单验证 JSBSim 配置
"""

import json

print("=" * 60)
print("JSBSim 配置快速检查")
print("=" * 60)
print()

# 检查 1: JSBSim 模块
print("[1/3] JSBSim 模块...")
try:
    import jsbsim
    print(f"  ✅ 已安装 (版本 {jsbsim.__version__ if hasattr(jsbsim, '__version__') else 'Unknown'})")
except ImportError:
    print("  ❌ 未安装")

print()

# 检查 2: 配置文件
print("[2/3] config.json 配置...")
with open('config.json', 'r') as f:
    config = json.load(f)

use_jsbsim = config.get('UseJSBSim', False)
aircraft = config.get('JSBSimAircraft', 'f16')

print(f"  UseJSBSim: {use_jsbsim}")
print(f"  JSBSimAircraft: {aircraft}")

if use_jsbsim:
    print("  ✅ JSBSim 已启用")
else:
    print("  ❌ JSBSim 未启用")

print()

# 检查 3: 代码是否有 JSBSim 支持
print("[3/3] 代码中的 JSBSim 支持...")
with open('source/Machines.py', 'r', encoding='utf-8') as f:
    code = f.read()
    
has_jsbsim_method = 'def update_kinetics_jsbsim' in code
has_jsbsim_check = 'if self.use_jsbsim and self.jsbsim_adapter' in code
has_jsbsim_call = 'self.update_kinetics_jsbsim(dts)' in code

print(f"  update_kinetics_jsbsim 方法: {'✅' if has_jsbsim_method else '❌'}")
print(f"  JSBSim 检查逻辑: {'✅' if has_jsbsim_check else '❌'}")
print(f"  JSBSim 调用: {'✅' if has_jsbsim_call else '❌'}")

print()
print("=" * 60)
print("结论")
print("=" * 60)
print()

if use_jsbsim and has_jsbsim_method and has_jsbsim_check:
    print("✅ 系统已配置为使用 JSBSim！")
    print()
    print("启动程序时应该看到:")
    print("  ✈️  飞机名: 已启用 JSBSim 真实飞行动力学 (型号: f16)")
    print()
    print("物理解算流程:")
    print("  每帧 → Aircraft.update_kinetics()")
    print("       → 检查 use_jsbsim")  
    print("       → 调用 update_kinetics_jsbsim()")
    print("       → JSBSimAdapter.update()")
    print("       → jsbsim.FGFDMExec.run() ← 真实物理解算!")
else:
    print("⚠️  配置可能有问题")

print()
print("=" * 60)
print("如何确认运行时真的在用 JSBSim:")
print("=" * 60)
print()
print("方法 1: 查看启动日志 (最简单)")
print("  运行 start.bat")
print("  在控制台查找: '✈️  XXX: 已启用 JSBSim...'")
print()
print("方法 2: 添加调试输出")
print("  编辑 source/Machines.py, 在第 1952 行后添加:")
print("  ")
print("    def update_kinetics(self, dts):")
print("        print(f'[DEBUG] {self.name}: use_jsbsim={self.use_jsbsim}')  # 添加这行")
print()
print("方法 3: 观察飞行特性差异")
print("  JSBSim (真实):")
print("    - 低速时容易失速")
print("    - 爬升需要保持足够速度")
print("    - 舵面响应有延迟")
print("    - 大迎角时升力下降")
print()
print("  简化物理:")
print("    - 几乎不会失速")
print("    - 爬升很容易")
print("    - 响应很灵敏")
print("    - 任何速度都能机动")
print()

