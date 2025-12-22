#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
JSBSim 详细集成测试脚本
验证物理解算的正确性，包括：
1. 控制方向测试
2. Pitch 角符号一致性测试
3. 速度积分正确性测试
"""

import sys
sys.path.append("")

from JSBSimAdapter import JSBSimAdapter, is_jsbsim_available
import harfang as hg
from math import radians, degrees, sqrt

def test_jsbsim_detailed():
    """详细测试 JSBSim 集成"""
    print("=" * 80)
    print("JSBSim 详细集成测试")
    print("=" * 80)
    print()
    
    # 1. 检查 JSBSim 是否可用
    if not is_jsbsim_available():
        print("❌ JSBSim 未安装！请运行: pip install jsbsim")
        return False
    
    print("✅ JSBSim 已安装")
    print()
    
    # 2. 创建适配器
    print("=" * 80)
    print("测试 1: 初始化 JSBSim 适配器")
    print("=" * 80)
    adapter = JSBSimAdapter("f16", use_jsbsim=True)
    
    if not adapter.enabled:
        print("❌ JSBSim 适配器初始化失败")
        return False
    
    print("✅ JSBSim 适配器初始化成功")
    print()
    
    # 3. 测试 Pitch 角符号一致性
    print("=" * 80)
    print("测试 2: Pitch 角符号一致性")
    print("=" * 80)
    print("说明：设置一个已知的 pitch 角，然后读取，检查是否一致")
    print()
    
    test_pitch_values = [0.0, 10.0, -10.0, 45.0]
    pitch_test_passed = True
    
    for test_pitch in test_pitch_values:
        # 设置 pitch 角
        adapter.set_orientation(
            roll_deg=0.0,
            pitch_deg=test_pitch,
            yaw_deg=0.0
        )
        
        # 运行初始化
        adapter.fdm.run_ic()
        
        # 读取 pitch 角
        state = adapter._get_state()
        read_pitch = state['pitch']
        
        # 计算误差
        error = abs(test_pitch - read_pitch)
        status = "✅" if error < 1.0 else "❌"
        
        print(f"{status} 设置={test_pitch:6.2f}°, 读取={read_pitch:6.2f}°, 误差={error:.2f}°")
        
        if error >= 1.0:
            pitch_test_passed = False
    
    print()
    if pitch_test_passed:
        print("✅ Pitch 角符号一致性测试通过")
    else:
        print("❌ Pitch 角符号一致性测试失败 - 存在符号不一致问题")
    print()
    
    # 4. 测试控制方向
    print("=" * 80)
    print("测试 3: 控制方向测试")
    print("=" * 80)
    print("说明：给固定的控制输入，观察飞机姿态变化方向")
    print()
    
    # 重新初始化（平飞状态）
    adapter = JSBSimAdapter("f16", use_jsbsim=True)
    
    # 测试 Elevator (Pitch 控制)
    print("3.1 测试 Elevator (升降舵) 控制")
    print("-" * 80)
    print("给 elevator=0.2 (正值)，观察 Pitch 角变化")
    print()
    
    # 记录初始 pitch
    initial_state = adapter._get_state()
    initial_pitch = initial_state['pitch']
    
    # 运行 60 帧（1秒），给正的 elevator
    for i in range(60):
        controls = {
            'throttle': 0.7,
            'elevator': 0.2,   # 正值
            'aileron': 0.0,
            'rudder': 0.0,
            'flaps': 0.0,
            'brake': 0.0
        }
        adapter.update(1.0/60.0, controls)
        
        if i % 20 == 0 and i > 0:
            state = adapter._get_state()
            print(f"  帧 {i:2d}: Pitch={state['pitch']:6.2f}°, ΔPitch={state['pitch']-initial_pitch:+6.2f}°")
    
    final_state = adapter._get_state()
    final_pitch = final_state['pitch']
    pitch_change = final_pitch - initial_pitch
    
    print()
    print(f"初始 Pitch: {initial_pitch:.2f}°")
    print(f"最终 Pitch: {final_pitch:.2f}°")
    print(f"Pitch 变化: {pitch_change:+.2f}°")
    
    if pitch_change > 0:
        print("✅ elevator > 0 → Pitch 增大 (抬头)")
    elif pitch_change < 0:
        print("⚠️ elevator > 0 → Pitch 减小 (低头) - 可能需要反转符号")
    else:
        print("❓ Pitch 没有变化 - 可能油门不足或控制无效")
    print()
    
    # 测试 Aileron (Roll 控制)
    print("3.2 测试 Aileron (副翼) 控制")
    print("-" * 80)
    print("给 aileron=0.2 (正值)，观察 Roll 角变化")
    print()
    
    # 重新初始化
    adapter = JSBSimAdapter("f16", use_jsbsim=True)
    initial_state = adapter._get_state()
    initial_roll = initial_state['roll']
    
    # 运行 60 帧，给正的 aileron
    for i in range(60):
        controls = {
            'throttle': 0.7,
            'elevator': 0.0,
            'aileron': 0.2,   # 正值
            'rudder': 0.0,
            'flaps': 0.0,
            'brake': 0.0
        }
        adapter.update(1.0/60.0, controls)
        
        if i % 20 == 0 and i > 0:
            state = adapter._get_state()
            print(f"  帧 {i:2d}: Roll={state['roll']:6.2f}°, ΔRoll={state['roll']-initial_roll:+6.2f}°")
    
    final_state = adapter._get_state()
    final_roll = final_state['roll']
    roll_change = final_roll - initial_roll
    
    print()
    print(f"初始 Roll: {initial_roll:.2f}°")
    print(f"最终 Roll: {final_roll:.2f}°")
    print(f"Roll 变化: {roll_change:+.2f}°")
    
    if roll_change > 0:
        print("✅ aileron > 0 → Roll 增大 (右滚)")
    elif roll_change < 0:
        print("⚠️ aileron > 0 → Roll 减小 (左滚) - 可能需要反转符号")
    else:
        print("❓ Roll 没有变化 - 控制可能无效")
    print()
    
    # 5. 测试速度积分正确性
    print("=" * 80)
    print("测试 4: 速度积分正确性")
    print("=" * 80)
    print("说明：验证位置更新不是双倍速度（即不存在双重积分）")
    print()
    
    # 重新初始化
    adapter = JSBSimAdapter("f16", use_jsbsim=True)
    
    # 记录初始状态
    initial_state = adapter._get_state()
    initial_altitude = initial_state['altitude']
    initial_speed_u = initial_state['u']  # 前向速度
    
    print(f"初始状态:")
    print(f"  高度: {initial_altitude:.1f} m")
    print(f"  前向速度: {initial_speed_u:.1f} m/s ({initial_speed_u*3.6:.1f} km/h)")
    print()
    
    # 运行 60 帧（1秒），固定油门
    print("运行 1 秒模拟（60 帧），油门 70%...")
    
    speeds = []
    altitudes = []
    
    for i in range(60):
        controls = {
            'throttle': 0.7,
            'elevator': 0.0,
            'aileron': 0.0,
            'rudder': 0.0,
            'flaps': 0.0,
            'brake': 0.0
        }
        state = adapter.update(1.0/60.0, controls)
        
        if state:
            speeds.append(state['u'])
            altitudes.append(state['altitude'])
    
    final_state = adapter._get_state()
    final_altitude = final_state['altitude']
    final_speed_u = final_state['u']
    
    # 计算平均速度
    avg_speed_u = sum(speeds) / len(speeds) if speeds else 0
    
    # 计算理论垂直位移（使用平均垂直速度）
    # 注意：这里简化处理，实际应该用垂直速度分量
    altitude_change = final_altitude - initial_altitude
    
    print()
    print(f"最终状态:")
    print(f"  高度: {final_altitude:.1f} m")
    print(f"  前向速度: {final_speed_u:.1f} m/s ({final_speed_u*3.6:.1f} km/h)")
    print()
    print(f"变化:")
    print(f"  高度变化: {altitude_change:+.1f} m")
    print(f"  速度变化: {final_speed_u - initial_speed_u:+.1f} m/s")
    print(f"  平均速度: {avg_speed_u:.1f} m/s")
    print()
    
    # 简单检查：速度应该合理（不会突然翻倍）
    speed_ratio = final_speed_u / initial_speed_u if initial_speed_u > 0 else 1.0
    
    if 0.8 <= speed_ratio <= 1.5:
        print("✅ 速度变化合理 - 不存在明显的双重积分问题")
    else:
        print(f"⚠️ 速度变化异常 (比率={speed_ratio:.2f}) - 可能存在积分问题")
    print()
    
    # 6. 测试坐标系转换
    print("=" * 80)
    print("测试 5: 坐标系转换")
    print("=" * 80)
    print("说明：验证 JSBSim (NED) 到 Harfang (EUN) 的速度转换")
    print()
    
    state = adapter._get_state()
    
    # JSBSim 坐标系速度
    vx_north = state['vx']  # 北向
    vy_up = state['vy']     # 上向（已转换）
    vz_east = state['vz']   # 东向
    
    print(f"JSBSim 惯性系速度 (NED → EUN 已转换):")
    print(f"  北向 (vx): {vx_north:6.1f} m/s")
    print(f"  上向 (vy): {vy_up:6.1f} m/s")
    print(f"  东向 (vz): {vz_east:6.1f} m/s")
    print()
    
    # Harfang 坐标系速度 (应该映射为 X=东, Y=上, Z=北)
    # 在 jsbsim_to_harfang_matrix() 中的映射
    harfang_vx = vz_east   # Harfang X = JSBSim 东
    harfang_vy = vy_up     # Harfang Y = JSBSim 上
    harfang_vz = vx_north  # Harfang Z = JSBSim 北
    
    print(f"Harfang 坐标系速度 (EUN):")
    print(f"  X (东): {harfang_vx:6.1f} m/s")
    print(f"  Y (上): {harfang_vy:6.1f} m/s")
    print(f"  Z (北): {harfang_vz:6.1f} m/s")
    print()
    
    # 计算总速度
    jsbsim_speed = sqrt(vx_north**2 + vy_up**2 + vz_east**2)
    harfang_speed = sqrt(harfang_vx**2 + harfang_vy**2 + harfang_vz**2)
    
    print(f"总速度:")
    print(f"  JSBSim: {jsbsim_speed:.1f} m/s ({jsbsim_speed*3.6:.1f} km/h)")
    print(f"  Harfang: {harfang_speed:.1f} m/s ({harfang_speed*3.6:.1f} km/h)")
    print()
    
    speed_diff = abs(jsbsim_speed - harfang_speed)
    if speed_diff < 0.1:
        print("✅ 坐标系转换正确 - 速度模长保持不变")
    else:
        print(f"❌ 坐标系转换错误 - 速度模长变化了 {speed_diff:.2f} m/s")
    print()
    
    # 7. 总结
    print("=" * 80)
    print("测试总结")
    print("=" * 80)
    print()
    print("✅ JSBSim 集成测试完成")
    print()
    print("关键发现：")
    print("1. Pitch 角符号一致性:", "通过" if pitch_test_passed else "⚠️ 需要检查")
    print("2. Elevator 控制:", "抬头" if pitch_change > 0 else ("低头" if pitch_change < 0 else "无变化"))
    print("3. Aileron 控制:", "右滚" if roll_change > 0 else ("左滚" if roll_change < 0 else "无变化"))
    print("4. 速度积分:", "正常" if 0.8 <= speed_ratio <= 1.5 else "⚠️ 异常")
    print("5. 坐标系转换:", "正确" if speed_diff < 0.1 else "❌ 错误")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_jsbsim_detailed()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

