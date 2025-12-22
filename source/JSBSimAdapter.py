# -*- coding:utf-8 -*-
"""
JSBSim 飞行动力学引擎适配器
将 JSBSim 集成到现有的 Harfang 3D 飞行模拟器中
"""

import harfang as hg
from math import radians, degrees
import os

# JSBSim 导入（如果未安装会给出友好提示）
try:
    import jsbsim
    JSBSIM_AVAILABLE = True
except ImportError:
    JSBSIM_AVAILABLE = False
    print("=" * 60)
    print("WARNING: JSBSim 未安装！")
    print("请运行: pip install jsbsim")
    print("或者: pip install jsbsim==1.1.13")
    print("=" * 60)


class JSBSimAdapter:
    """
    JSBSim 适配器类
    负责：
    1. 初始化 JSBSim FDM（飞行动力学模型）
    2. 与 Harfang 坐标系转换
    3. 输入控制信号到 JSBSim
    4. 从 JSBSim 读取姿态和速度
    """
    
    def __init__(self, aircraft_name="f16", use_jsbsim=False):
        """
        初始化 JSBSim 适配器
        
        Args:
            aircraft_name: 飞机型号名称（对应 JSBSim 的飞机配置文件）
            use_jsbsim: 是否启用 JSBSim（如果为 False，则使用简化物理）
        """
        self.enabled = use_jsbsim and JSBSIM_AVAILABLE
        self.fdm = None  # Flight Dynamics Model
        self.initialized = False
        
        if self.enabled:
            try:
                self._init_jsbsim(aircraft_name)
            except Exception as e:
                print(f"JSBSim 初始化失败: {e}")
                print("回退到简化物理模型")
                self.enabled = False
    
    def _init_jsbsim(self, aircraft_name):
        """初始化 JSBSim 引擎"""
        # 创建 FDM 实例
        self.fdm = jsbsim.FGFDMExec(None)
        
        # 查找 JSBSim 数据路径
        # 尝试多个可能的位置
        jsbsim_module_path = os.path.dirname(jsbsim.__file__)
        
        possible_roots = [
            jsbsim_module_path,  # site-packages/jsbsim
            os.path.join(jsbsim_module_path, 'data'),  # site-packages/jsbsim/data
            os.path.join(os.path.dirname(jsbsim_module_path), 'JSBSim'),  # site-packages/JSBSim
        ]
        
        # 尝试每个路径
        root_found = False
        for root_path in possible_roots:
            if os.path.exists(root_path):
                # 检查是否有 aircraft 目录
                aircraft_dir = os.path.join(root_path, 'aircraft')
                if os.path.exists(aircraft_dir):
                    print(f"找到 JSBSim 数据目录: {root_path}")
                    self.fdm.set_root_dir(root_path)
                    root_found = True
                    break
        
        if not root_found:
            # 如果找不到数据目录，使用默认路径并继续尝试
            print(f"警告：未找到 JSBSim 数据目录，使用默认路径")
            self.fdm.set_root_dir(jsbsim_module_path)
        
        # 飞机配置映射
        # 注意：不同的 JSBSim 安装可能有不同的可用飞机
        available_aircraft = {
            "f16": "f16",
            "f-16": "f16",
            "c172": "c172p",  # 尝试 c172p (带 'p' 后缀)
            "c172p": "c172p",
            "cessna": "c172p",
            "737": "737",
            "boeing": "737",
            "simple": "c172p"  # 使用 c172p 作为简单模型
        }
        
        aircraft_config = available_aircraft.get(aircraft_name.lower(), "c172p")
        
        print(f"正在加载 JSBSim 飞机配置: {aircraft_config}")
        
        # 尝试加载飞机
        if not self.fdm.load_model(aircraft_config):
            # 如果失败，尝试备用方案
            print(f"警告：无法加载 {aircraft_config}，尝试备用方案...")
            
            # 尝试列表中的其他飞机
            fallback_aircraft = ["c172p", "c172", "f16", "x15"]
            loaded = False
            
            for fallback in fallback_aircraft:
                if fallback != aircraft_config:
                    print(f"  尝试加载 {fallback}...")
                    if self.fdm.load_model(fallback):
                        print(f"  ✅ 成功加载 {fallback}")
                        aircraft_config = fallback
                        loaded = True
                        break
            
            if not loaded:
                raise Exception(
                    f"无法加载任何飞机模型！\n"
                    f"  请求的型号: {aircraft_config}\n"
                    f"  JSBSim 路径: {jsbsim_module_path}\n"
                    f"  \n"
                    f"  解决方案：\n"
                    f"  1. 重新安装 JSBSim: pip uninstall jsbsim && pip install jsbsim\n"
                    f"  2. 或禁用 JSBSim（使用简化物理模型）\n"
                    f"  3. 检查 JSBSim 版本: python -c \"import jsbsim; print(jsbsim.__version__)\""
                )
        
        # 初始化飞行条件
        self.fdm.set_dt(1.0 / 60.0)  # 60 FPS
        
        # 设置初始位置和姿态（安全模式）
        # JSBSim 使用地理坐标系（纬度、经度、海拔）
        try:
            self.fdm.set_property_value('ic/lat-geod-deg', 0.0)  # 纬度
            self.fdm.set_property_value('ic/long-gc-deg', 0.0)   # 经度
            self.fdm.set_property_value('ic/h-sl-ft', 10000.0)   # 海拔（英尺）
            
            # 初始速度和姿态（提高初始速度以避免失速）
            self.fdm.set_property_value('ic/u-fps', 650.0)  # X轴速度（英尺/秒）≈ 198 m/s ≈ 713 km/h
            self.fdm.set_property_value('ic/v-fps', 0.0)    # Y轴速度
            self.fdm.set_property_value('ic/w-fps', 0.0)    # Z轴速度
            
            self.fdm.set_property_value('ic/phi-deg', 0.0)      # Roll (滚转)
            self.fdm.set_property_value('ic/theta-deg', 0.0)    # Pitch (俯仰)
            self.fdm.set_property_value('ic/psi-deg', 0.0)      # Yaw (偏航)
            
            # 初始化引擎（某些飞机可能没有引擎）
            try:
                self.fdm.set_property_value('propulsion/engine[0]/set-running', 1)
            except:
                pass  # 某些飞机配置可能没有引擎属性
        except Exception as e:
            raise Exception(f"JSBSim 初始化参数设置失败: {e}")
        
        # 运行初始化
        if not self.fdm.run_ic():
            raise Exception("JSBSim 初始化条件设置失败")
        
        self.initialized = True
        print("JSBSim 初始化成功！")
        print(f"  飞机型号: {aircraft_config}")
        
        # 安全读取属性（某些属性可能不存在）
        try:
            num_engines = self.fdm['propulsion/num-engines']
            print(f"  引擎数量: {num_engines}")
        except:
            print(f"  引擎数量: N/A")
        
        try:
            altitude = self.fdm['position/h-sl-ft']
            print(f"  初始高度: {altitude:.0f} ft")
        except:
            print(f"  初始高度: 10000 ft (默认)")
    
    def update(self, dt, controls):
        """
        更新 JSBSim 物理模拟一帧
        
        Args:
            dt: 时间步长（秒）
            controls: 控制输入字典，包含：
                - throttle: 油门 (0-1)
                - elevator: 升降舵 (-1到1, 俯仰控制)
                - aileron: 副翼 (-1到1, 滚转控制)
                - rudder: 方向舵 (-1到1, 偏航控制)
                - flaps: 襟翼 (0-1)
                - brake: 刹车 (0-1)
        
        Returns:
            dict: 包含飞机状态的字典
        """
        if not self.enabled or not self.initialized:
            return None
        
        try:
            # 设置 JSBSim 时间步长
            self.fdm.set_dt(dt)
            
            # 输入控制信号到 JSBSim（安全模式）
            # JSBSim 使用规范化的控制输入 (-1 到 1 或 0 到 1)
            throttle_value = controls.get('throttle', 0.0)
            elevator_value = controls.get('elevator', 0.0)
            aileron_value = controls.get('aileron', 0.0)
            rudder_value = controls.get('rudder', 0.0)
            flaps_value = controls.get('flaps', 0.0)
            
            try:
                self.fdm.set_property_value('fcs/throttle-cmd-norm', throttle_value)
                self.fdm.set_property_value('fcs/elevator-cmd-norm', elevator_value)
                self.fdm.set_property_value('fcs/aileron-cmd-norm', aileron_value)
                self.fdm.set_property_value('fcs/rudder-cmd-norm', rudder_value)
                self.fdm.set_property_value('fcs/flap-cmd-norm', flaps_value)
                self.fdm.set_property_value('fcs/brake-cmd-norm', controls.get('brake', 0.0))
            except Exception as e:
                # 某些控制可能不存在，继续运行
                pass
            
            # 调试：显示输入到 JSBSim 的所有舵面控制（前5帧）
            if not hasattr(self, '_jsbsim_debug_count'):
                self._jsbsim_debug_count = 0
            if self._jsbsim_debug_count < 5:
                print(f"  → JSBSim 舵面输入:")
                print(f"     油门={throttle_value:.2f}, 升降舵={elevator_value:.3f}, 副翼={aileron_value:.3f}, 方向舵={rudder_value:.3f}")
                self._jsbsim_debug_count += 1
            
            # 运行一帧物理模拟 ← 这里！JSBSim 真实物理计算
            self.fdm.run()
            
            # 从 JSBSim 读取状态
            state = self._get_state()
            
            # 调试：显示完整的闭环系统（前5帧）
            if hasattr(self, '_jsbsim_debug_count') and self._jsbsim_debug_count <= 5:
                if state:
                    # 速度和加速度
                    u = state.get('u', 0)  # 前向速度
                    v = state.get('v', 0)  # 侧向速度
                    w = state.get('w', 0)  # 垂直速度
                    speed_kmh = u * 3.6
                    
                    # 姿态角
                    roll = state.get('roll', 0)
                    pitch = state.get('pitch', 0)
                    yaw = state.get('yaw', 0)
                    
                    # 角速度（姿态变化率）
                    p = state.get('p', 0)  # Roll rate
                    q = state.get('q', 0)  # Pitch rate
                    r = state.get('r', 0)  # Yaw rate
                    
                    # 气动参数
                    alpha = state.get('alpha', 0)  # 迎角
                    beta = state.get('beta', 0)    # 侧滑角
                    
                    print(f"  ← JSBSim 闭环输出:")
                    print(f"     速度: u={u:.1f} m/s ({speed_kmh:.1f} km/h), v={v:.1f}, w={w:.1f}")
                    print(f"     姿态: Roll={roll:.2f}°, Pitch={pitch:.2f}°, Yaw={yaw:.2f}°")
                    print(f"     气流角: 迎角α={alpha:.2f}°, 侧滑角β={beta:.2f}°  ← 由姿态决定！")
                    print(f"     角速度: p={p:.3f}, q={q:.3f}, r={r:.3f} rad/s  ← 由气动力矩产生！")
            
            return state
            
        except Exception as e:
            print(f"JSBSim 更新错误: {e}")
            return None
    
    def _get_state(self):
        """从 JSBSim 读取当前飞机状态（安全模式）"""
        if not self.fdm:
            return None
        
        try:
            # 位置（转换为米）
            # JSBSim 使用英尺和经纬度，需要转换
            altitude_m = self.fdm.get_property_value('position/h-sl-meters')  # 海拔（米）
            
            # 欧拉角（度）
            # 坐标系说明：
            # - JSBSim: 右手坐标系，pitch 向上为正，roll 右侧向下为正
            # - Harfang: pitch 和 roll 符号相反
            # 
            # 🔧 修复：反转 pitch 和 roll 符号用于显示
            # Pitch:
            # - JSBSim pitch > 0 (抬头) → Harfang pitch < 0 (显示为抬头)
            # - JSBSim pitch < 0 (低头) → Harfang pitch > 0 (显示为低头)
            # Roll:
            # - JSBSim roll > 0 (右滚) → Harfang roll < 0 (显示为右滚)
            # - JSBSim roll < 0 (左滚) → Harfang roll > 0 (显示为左滚)
            roll_deg = -self.fdm.get_property_value('attitude/roll-rad') * 180.0 / 3.14159  # 🔧 反转符号！
            pitch_deg = -self.fdm.get_property_value('attitude/pitch-rad') * 180.0 / 3.14159  # 🔧 反转符号！
            yaw_deg = self.fdm.get_property_value('attitude/heading-true-rad') * 180.0 / 3.14159
            
            # 机体坐标系速度
            u_mps = self.fdm.get_property_value('velocities/u-fps') * 0.3048  # X轴速度
            v_mps = self.fdm.get_property_value('velocities/v-fps') * 0.3048  # Y轴速度
            w_mps = self.fdm.get_property_value('velocities/w-fps') * 0.3048  # Z轴速度
            
            # 安全检查：防止无穷大或 NaN
            import math
            if not math.isfinite(u_mps):
                print(f"警告：u 异常 = {u_mps}，重置为 0")
                u_mps = 0.0
            if not math.isfinite(v_mps):
                print(f"警告：v 异常 = {v_mps}，重置为 0")
                v_mps = 0.0
            if not math.isfinite(w_mps):
                print(f"警告：w 异常 = {w_mps}，重置为 0")
                w_mps = 0.0
            
            # 线速度（惯性系）
            vx = self.fdm.get_property_value('velocities/v-north-fps') * 0.3048
            vy = self.fdm.get_property_value('velocities/v-down-fps') * 0.3048 * -1  # JSBSim down是负的
            vz = self.fdm.get_property_value('velocities/v-east-fps') * 0.3048
            
            # 安全检查：防止无穷大或 NaN
            import math
            if not math.isfinite(vx):
                print(f"警告：vx 异常 = {vx}，重置为 0")
                vx = 0.0
            if not math.isfinite(vy):
                print(f"警告：vy 异常 = {vy}，重置为 0")
                vy = 0.0
            if not math.isfinite(vz):
                print(f"警告：vz 异常 = {vz}，重置为 0")
                vz = 0.0
            
            # 角速度（弧度/秒）
            p = self.fdm.get_property_value('velocities/p-rad_sec')  # Roll rate
            q = self.fdm.get_property_value('velocities/q-rad_sec')  # Pitch rate
            r = self.fdm.get_property_value('velocities/r-rad_sec')  # Yaw rate
            
            # 加速度（m/s²）
            ax = self.fdm.get_property_value('accelerations/udot-ft_sec2') * 0.3048
            ay = self.fdm.get_property_value('accelerations/vdot-ft_sec2') * 0.3048
            az = self.fdm.get_property_value('accelerations/wdot-ft_sec2') * 0.3048
            
            # 气动参数（可选，可能不存在）
            try:
                alpha_deg = self.fdm.get_property_value('aero/alpha-deg')  # 迎角
            except:
                alpha_deg = 0.0
            
            try:
                beta_deg = self.fdm.get_property_value('aero/beta-deg')    # 侧滑角
            except:
                beta_deg = 0.0
            
            try:
                mach = self.fdm.get_property_value('velocities/mach')      # 马赫数
            except:
                mach = 0.0
        
        except Exception as e:
            print(f"JSBSim 状态读取错误: {e}")
            return None
        
        return {
            # 位置
            'altitude': altitude_m,
            
            # 姿态（度）
            'roll': roll_deg,
            'pitch': pitch_deg,
            'yaw': yaw_deg,
            
            # 速度（机体坐标系，m/s）
            'u': u_mps,
            'v': v_mps,
            'w': w_mps,
            
            # 速度（惯性坐标系，m/s）
            'vx': vx,
            'vy': vy,
            'vz': vz,
            
            # 角速度（rad/s）
            'p': p,
            'q': q,
            'r': r,
            
            # 加速度（m/s²）
            'ax': ax,
            'ay': ay,
            'az': az,
            
            # 气动参数
            'alpha': alpha_deg,
            'beta': beta_deg,
            'mach': mach
        }
    
    def set_position(self, position_hg):
        """
        设置飞机位置（Harfang 坐标 -> JSBSim）
        
        Args:
            position_hg: hg.Vec3 位置向量（Harfang 坐标系）
        """
        if not self.enabled or not self.initialized:
            return
        
        try:
            # Harfang Y 是高度
            altitude_m = position_hg.y
            altitude_ft = altitude_m * 3.28084
            
            self.fdm.set_property_value('position/h-sl-ft', altitude_ft)
            
            # X, Z 可以映射到经纬度偏移（简化处理）
            # 1度纬度 ≈ 111 km
            # 这里简化为局部坐标
            lat_offset = position_hg.z / 111000.0
            lon_offset = position_hg.x / 111000.0
            
            self.fdm.set_property_value('position/lat-geod-deg', lat_offset)
            self.fdm.set_property_value('position/long-gc-deg', lon_offset)
        except Exception as e:
            print(f"JSBSim 设置位置错误: {e}")
    
    def set_velocity(self, velocity_hg):
        """
        设置飞机速度（Harfang -> JSBSim）
        
        Args:
            velocity_hg: hg.Vec3 速度向量（m/s）
        """
        if not self.enabled or not self.initialized:
            return
        
        try:
            # 转换为英尺/秒
            u_fps = velocity_hg.z * 3.28084  # Forward
            v_fps = velocity_hg.x * 3.28084  # Right
            w_fps = -velocity_hg.y * 3.28084  # Down (注意符号)
            
            self.fdm.set_property_value('ic/u-fps', u_fps)
            self.fdm.set_property_value('ic/v-fps', v_fps)
            self.fdm.set_property_value('ic/w-fps', w_fps)
        except Exception as e:
            print(f"JSBSim 设置速度错误: {e}")
    
    def set_orientation(self, roll_deg, pitch_deg, yaw_deg):
        """
        设置飞机姿态
        
        Args:
            roll_deg: 滚转角（度）
            pitch_deg: 俯仰角（度）
            yaw_deg: 偏航角（度）
        """
        if not self.enabled or not self.initialized:
            return
        
        try:
            self.fdm.set_property_value('ic/phi-deg', roll_deg)
            self.fdm.set_property_value('ic/theta-deg', pitch_deg)
            self.fdm.set_property_value('ic/psi-deg', yaw_deg)
        except Exception as e:
            print(f"JSBSim 设置姿态错误: {e}")
    
    def harfang_to_jsbsim_controls(self, aircraft):
        """
        将 Harfang 飞机控制转换为 JSBSim 控制格式
        
        Args:
            aircraft: Aircraft 对象
        
        Returns:
            dict: JSBSim 控制输入
        """
        # 映射控制输入
        # Harfang 的 angular_levels: x=pitch, y=yaw, z=roll
        # JSBSim: elevator=pitch, rudder=yaw, aileron=roll
        # 
        # 🔧 符号修正：
        # - JSBSim elevator: 正值=抬头, 负值=低头
        # - Harfang angular_levels.x: 正值=抬头命令, 负值=低头命令
        # - 因此直接映射，不需要反转符号！
        # 
        # 之前的 bug：使用了负号 (-aircraft.angular_levels.x)
        # → 导致低头命令变成抬头，抬头命令变成低头
        # → 飞机低头时，elevator变正值，JSBSim抬头，高度上升 ✗
        
        controls = {
            'throttle': aircraft.thrust_level,
            'elevator': aircraft.angular_levels.x,    # 🔧 修复：去掉负号！
            'aileron': aircraft.angular_levels.z,     # Roll
            'rudder': aircraft.angular_levels.y,      # Yaw
            'flaps': aircraft.flaps_level if hasattr(aircraft, 'flaps_level') else 0.0,
            'brake': aircraft.brake_level if hasattr(aircraft, 'brake_level') else 0.0
        }
        
        return controls
    
    def jsbsim_to_harfang_matrix(self, state, current_pos):
        """
        将 JSBSim 状态转换为 Harfang 矩阵和速度
        
        Args:
            state: JSBSim 状态字典
            current_pos: 当前 Harfang 位置（用于平滑过渡）
        
        Returns:
            tuple: (matrix, velocity_hg)
        
        📌 重要说明：坐标系差异与位置更新
        
        JSBSim 使用地理坐标系：
        - 位置：经度(deg)、纬度(deg)、高度(m)
        - JSBSim 内部积分这些地理坐标
        
        Harfang 使用笛卡尔坐标系：
        - 位置：X(m)、Y(m)、Z(m)
        
        因此策略是：
        1. 从 JSBSim 读取惯性系速度（北/上/东）
        2. 转换为 Harfang 坐标系速度（东/上/北）
        3. 外部调用者用这个速度积分笛卡尔位置
        4. 高度直接使用 JSBSim 的精确值
        """
        if state is None:
            return None, None
        
        # 位置：只更新高度，水平位置保持不变（由外部用速度积分）
        # 这不是"双重积分"，因为 JSBSim 积分的是经纬度，我们积分的是 XYZ 米
        pos = hg.Vec3(current_pos.x, state['altitude'], current_pos.z)
        
        # 姿态（欧拉角 -> 旋转矩阵）
        # JSBSim: Roll, Pitch, Yaw
        # Harfang: X=pitch, Y=yaw, Z=roll
        # 
        # 注意：state['pitch'] 已经在 _get_state() 中反转过符号了
        # 所以这里直接使用即可
        rot = hg.Vec3(
            radians(state['pitch']),  # 已反转符号
            radians(state['yaw']),
            radians(state['roll'])
        )
        
        # 构建变换矩阵
        matrix = hg.TransformationMat4(pos, rot)
        
        # 速度（直接使用 JSBSim 的惯性系速度）
        # JSBSim 惯性系：vx (北), vy (上), vz (东)
        # Harfang 坐标系：X (东), Y (上), Z (北)
        velocity = hg.Vec3(state['vz'], state['vy'], state['vx'])
        
        return matrix, velocity


# =============== 工具函数 ===============

def is_jsbsim_available():
    """检查 JSBSim 是否可用"""
    return JSBSIM_AVAILABLE


def print_jsbsim_info():
    """打印 JSBSim 信息"""
    if JSBSIM_AVAILABLE:
        print("=" * 60)
        print("JSBSim 可用")
        print(f"版本: {jsbsim.__version__ if hasattr(jsbsim, '__version__') else 'Unknown'}")
        print("支持的飞机型号: f16, c172, 737, 等")
        print("=" * 60)
    else:
        print("=" * 60)
        print("JSBSim 未安装")
        print("安装方法:")
        print("  pip install jsbsim")
        print("  或")
        print("  pip install jsbsim==1.1.13")
        print("=" * 60)


def create_jsbsim_config():
    """创建 JSBSim 配置示例"""
    config = """
# JSBSim 配置说明

## 安装 JSBSim

```bash
pip install jsbsim
```

## 可用飞机型号

JSBSim 自带多个飞机模型：
- f16: F-16 战斗机
- c172: Cessna 172（小型飞机）
- 737: Boeing 737 客机
- 更多型号请参考 JSBSim 文档

## 启用 JSBSim

在创建飞机时设置 use_jsbsim=True：

```python
aircraft = Aircraft(
    name="player",
    model_name="Rafale",
    use_jsbsim=True,
    jsbsim_aircraft="f16"
)
```

## 控制映射

| Harfang 控制 | JSBSim 控制 | 说明 |
|-------------|-------------|------|
| thrust_level | throttle | 油门 (0-1) |
| angular_levels.x | elevator | 升降舵/俯仰 (-1到1) |
| angular_levels.z | aileron | 副翼/滚转 (-1到1) |
| angular_levels.y | rudder | 方向舵/偏航 (-1到1) |
| flaps_level | flaps | 襟翼 (0-1) |
| brake_level | brake | 刹车 (0-1) |

## 注意事项

1. JSBSim 使用真实物理，飞行特性会更真实但也更难控制
2. 需要根据具体飞机型号调整控制参数
3. JSBSim 计算开销比简化物理大，可能影响性能
"""
    return config

