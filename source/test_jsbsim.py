#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
JSBSim 集成测试脚本
用于验证 JSBSim 是否正确安装和配置
"""

import sys
sys.path.append("")

from JSBSimAdapter import JSBSimAdapter, is_jsbsim_available, print_jsbsim_info

def test_jsbsim():
    """测试 JSBSim 功能"""
    print("=" * 60)
    print("JSBSim 集成测试")
    print("=" * 60)
    print()
    
    # 1. 检查 JSBSim 是否可用
    print("1. 检查 JSBSim 安装状态...")
    print_jsbsim_info()
    print()
    
    if not is_jsbsim_available():
        print("❌ JSBSim 未安装！")
        print("请运行: pip install jsbsim")
        return False
    
    print("✅ JSBSim 已安装")
    print()
    
    # 2. 测试 F-16
    print("2. 测试 F-16 飞行动力学模型...")
    adapter_f16 = JSBSimAdapter("f16", use_jsbsim=True)
    
    if not adapter_f16.enabled:
        print("❌ F-16 模型加载失败")
        return False
    
    print("✅ F-16 模型加载成功")
    
    # 运行几帧模拟
    print("\n模拟 F-16 飞行（60帧）：")
    print("-" * 60)
    print(f"{'帧数':<8} {'高度(m)':<12} {'速度(m/s)':<12} {'俯仰角':<12}")
    print("-" * 60)
    
    for i in range(60):
        controls = {
            'throttle': 0.8,      # 80% 油门
            'elevator': 0.0,      # 保持平飞
            'aileron': 0.0,       # 不滚转
            'rudder': 0.0,        # 不偏航
            'flaps': 0.0,         # 襟翼收起
            'brake': 0.0          # 无刹车
        }
        
        state = adapter_f16.update(1.0/60.0, controls)
        
        if state and i % 10 == 0:  # 每10帧输出一次
            print(f"{i:<8} {state['altitude']:<12.1f} {state['u']:<12.1f} {state['pitch']:<12.2f}")
    
    print("-" * 60)
    print("✅ F-16 模拟测试通过")
    print()
    
    # 3. 测试 Cessna 172
    print("3. 测试 Cessna 172 飞行动力学模型...")
    adapter_c172 = JSBSimAdapter("c172", use_jsbsim=True)
    
    if not adapter_c172.enabled:
        print("⚠️ Cessna 172 模型加载失败（可能不可用）")
    else:
        print("✅ Cessna 172 模型加载成功")
        
        # 简单测试
        state = adapter_c172.update(1.0/60.0, {
            'throttle': 0.5,
            'elevator': 0.0,
            'aileron': 0.0,
            'rudder': 0.0,
            'flaps': 0.0,
            'brake': 0.0
        })
        
        if state:
            print(f"  初始状态: 高度={state['altitude']:.1f}m, 速度={state['u']:.1f}m/s")
    
    print()
    
    # 4. 总结
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print()
    print("✅ JSBSim 工作正常，可以在程序中使用")
    print()
    print("启用方法：")
    print("  1. 运行程序")
    print("  2. 按 F12 打开设置")
    print("  3. 勾选 'Use JSBSim (Restart Required)'")
    print("  4. 选择飞机型号（F-16, C172, 737）")
    print("  5. 重启程序或重新创建飞机")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_jsbsim()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

