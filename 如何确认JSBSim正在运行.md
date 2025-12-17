# 如何确认 JSBSim 正在运行

## ✅ 配置验证结果

刚才运行的检查脚本显示：

```
✅ JSBSim 模块已安装 (版本 1.2.3)
✅ config.json 中 JSBSim 已启用
✅ 代码中有完整的 JSBSim 支持
```

**结论：系统已正确配置为使用 JSBSim！**

---

## 🔍 如何确认程序运行时真的在用 JSBSim

### 方法 1: 查看启动日志（最直接）

运行 `start.bat`，在控制台输出中查找：

```
✈️  Rafale_0: 已启用 JSBSim 真实飞行动力学 (型号: f16)
🚀 [Rafale_0] 正在使用 JSBSim 进行物理解算
✈️  Eurofighter_1: 已启用 JSBSim 真实飞行动力学 (型号: f16)
🚀 [Eurofighter_1] 正在使用 JSBSim 进行物理解算
```

**如果看到这些消息，说明 JSBSim 正在运行！**

我刚才在代码中添加了调试输出：
- 飞机创建时：显示 "✈️ 已启用 JSBSim..."
- 第一次物理更新时：显示 "🚀 正在使用 JSBSim 进行物理解算"

---

### 方法 2: 观察飞行特性（最明显）

JSBSim 真实物理和简化物理有**显著差异**：

#### JSBSim（真实飞行动力学）特征：

1. **失速效应明显**
   - 低速时（< 200 km/h）飞机会失速掉高度
   - 大迎角时升力急剧下降
   - 需要保持足够空速才能爬升

2. **舵面响应延迟**
   - 按方向键后，飞机不会立即响应
   - 有明显的气动延迟
   - 需要提前量操作

3. **能量管理重要**
   - 爬升会损失速度
   - 俯冲会增加速度
   - 需要平衡速度和高度

4. **地面效应**
   - 接近地面时升力增加
   - 起飞需要足够滑跑距离

#### 简化物理特征：

1. **几乎不失速**
   - 任何速度都能飞
   - 可以悬停

2. **响应灵敏**
   - 按键立即响应
   - 没有延迟

3. **能量无限**
   - 可以垂直爬升
   - 速度不受影响

4. **无地面效应**
   - 可以瞬间起飞

---

### 方法 3: 物理解算流程验证

JSBSim 的执行流程：

```
每帧 (60 FPS)
  ↓
Main.update()
  ↓
states.update_main_phase(dts)
  ↓
Main.update_kinetics(dts)
  ↓
Aircraft.update_kinetics(dts)
  ↓
检查: if self.use_jsbsim and self.jsbsim_adapter.enabled:
  ↓ YES → 使用 JSBSim
Aircraft.update_kinetics_jsbsim(dts)
  ↓
JSBSimAdapter.update(dts, controls)
  ↓
self.fdm.set_property_value('fcs/throttle-cmd-norm', ...)
self.fdm.set_property_value('fcs/elevator-cmd-norm', ...)
self.fdm.set_property_value('fcs/aileron-cmd-norm', ...)
  ↓
self.fdm.run()  ← 这里！JSBSim 真实物理计算！
  ↓
读取状态: altitude, roll, pitch, yaw, velocities, accelerations
  ↓
转换为 Harfang 坐标系
  ↓
更新飞机位置和姿态
```

---

## 🧪 快速测试

### 测试 1: 失速测试

1. 启动程序
2. 起飞后，按 `S` 键减速到 150 km/h 以下
3. 尝试爬升（按 `↓` 抬头）

**JSBSim 表现：**
- 飞机会失速
- 机头下沉
- 高度下降
- 需要加速恢复

**简化物理表现：**
- 飞机正常爬升
- 不会失速

### 测试 2: 大迎角测试

1. 保持 300 km/h 速度
2. 猛拉机头向上（按住 `↓`）
3. 观察飞机响应

**JSBSim 表现：**
- 开始爬升
- 速度快速下降
- 到达失速迎角后升力消失
- 机头下沉

**简化物理表现：**
- 持续爬升
- 速度下降很慢
- 不会失速

### 测试 3: 响应延迟测试

1. 平飞状态
2. 快速按 `←` 然后 `→`（左右滚转）
3. 观察响应

**JSBSim 表现：**
- 有明显延迟
- 滚转速度受空速影响
- 动作平滑但慢

**简化物理表现：**
- 立即响应
- 滚转很快
- 几乎没有延迟

---

## 📊 对比总结

| 特征 | JSBSim (真实) | 简化物理 |
|------|--------------|----------|
| 失速 | ✅ 会失速 | ❌ 不失速 |
| 响应延迟 | ✅ 有延迟 | ❌ 立即响应 |
| 能量守恒 | ✅ 爬升损失速度 | ❌ 能量无限 |
| 地面效应 | ✅ 有 | ❌ 无 |
| 起飞距离 | ✅ 需要滑跑 | ❌ 瞬间起飞 |
| 操控难度 | ⭐⭐⭐⭐ 真实 | ⭐⭐ 简单 |
| 适用场景 | 训练、研究 | 游戏、演示 |

---

## 🎯 最终确认方法

**运行程序，在启动日志中查找：**

```
✈️  XXX: 已启用 JSBSim 真实飞行动力学 (型号: f16)
🚀 [XXX] 正在使用 JSBSim 进行物理解算
```

**如果看到这些，100% 确认在使用 JSBSim！**

如果没看到，可能是：
1. conda 环境中 JSBSim 未安装 → 运行 `conda activate bh && pip install jsbsim`
2. 配置被修改 → 检查 `config.json`

---

## 💡 提示

现在您的系统已经：
- ✅ 配置为使用 JSBSim
- ✅ 代码中有调试输出
- ✅ 可以通过日志确认

**直接运行 `start.bat` 查看启动日志即可确认！**

