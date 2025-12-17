# Copyright (C) 2018-2021 Eric Kernin, NWNC HARFANG.


import harfang as hg
from Machines import *
from MachineDevice import *
from MathsSupp import *
from Sprites import *
from random import *
from overlays import *
from MissileLauncherS400 import *


class HUD:

	@classmethod
	def init(cls, resolution: hg.Vec2):

		cls.color_inactive = hg.Color(0.2, 0.2, 0.2, 0.5)
		cls.color_wait_connect = hg.Color(1, 0.8, 0.8, 1)
		cls.color_connected = hg.Color(0.3, 0.3, 0.3, 1)

	# Texts:
	@staticmethod
	def hud_convert_coords(x, y, resolution):
		ratio = resolution.x / resolution.y
		return (x - resolution.x / 2) / (resolution.x / 2) * ratio, (y - resolution.y / 2) / (resolution.y / 2)


class HUD_Radar:

	spr_radar = None
	spr_radar_light = None
	spr_radar_box = None
	aircrafts_plots = None
	missiles_plots = None
	ships_plots = None
	missile_launchers_plots = None
	dir_plots = None
	spr_noise = None

	@classmethod
	def init(cls, resolution:hg.Vec2):
		cls.spr_radar = Sprite(530, 530, "sprites/radar.png")
		cls.spr_radar_light = Sprite(530, 530, "sprites/radar_light.png")
		cls.spr_radar_box = Sprite(530, 530, "sprites/radar_box.png")
		cls.aircrafts_plots = []
		cls.missiles_plots = []
		cls.ships_plots = []
		cls.missile_launchers_plots = []
		cls.dir_plot = Sprite(32, 32, "sprites/plot_dir.png")
		cls.spr_noise = Sprite(256, 256, "sprites/noise.png")
		rs = (200 / 1600 * resolution.x) / cls.spr_radar.width
		cls.spr_radar.set_size(rs)
		cls.spr_radar_light.set_size(rs)
		cls.spr_radar_box.set_size(rs)
		cls.spr_noise.set_size((200 / 1600 * resolution.x) / cls.spr_noise.width)

	@classmethod
	def setup_plots(cls, resolution, num_aircrafts, num_missiles, num_ships, num_missile_launchers):
		cls.aircrafts_plots = []
		cls.missiles_plots = []
		cls.ships_plots = []
		cls.missile_launchers_plots = []
		for i in range(num_aircrafts):
			cls.aircrafts_plots.append(Sprite(40, 40, "sprites/plot.png"))
		for i in range(num_missiles):
			cls.missiles_plots.append(Sprite(40, 40, "sprites/plot_missile.png"))
		for i in range(num_ships):
			cls.ships_plots.append(Sprite(40, 40, "sprites/plot_ship.png"))
		for i in range(num_missile_launchers):
			cls.missile_launchers_plots.append(Sprite(40, 40, "sprites/plot_missile_launcher.png"))

	@classmethod
	def update(cls, Main, machine:Destroyable_Machine, targets):
		t = hg.time_to_sec_f(hg.GetClock())
		rx, ry = 150 / 1600 * Main.resolution.x, 150 / 900 * Main.resolution.y
		rm = 6 / 1600
		rs = cls.spr_radar.size

		radar_scale = 4000
		plot_size = 12 / 1600 * Main.resolution.x

		cls.spr_radar.set_position(rx, ry)
		cls.spr_radar.set_color(hg.Color(1, 1, 1, 1))
		Main.sprites_display_list.append(cls.spr_radar)

		mat, pos, rot, aX, aY, aZ = machine.decompose_matrix()
		aZ.y = 0
		aZ = hg.Normalize(aZ)
		if aY.y < 0:
			aY = hg.Vec3(0, -1, 0)
		else:
			aY = hg.Vec3(0, 1, 0)
		aX = hg.Cross(aY, aZ)
		matrot = hg.Mat3()
		hg.SetAxises(matrot, aX, aY, aZ)
		mat_trans = hg.InverseFast(hg.TransformationMat4(hg.GetT(mat), matrot))

		i_missile = 0
		i_ship = 0
		i_aircraft = 0
		i_missile_launcher = 0
		td = machine.get_device("TargettingDevice")

		for target in targets:
			if not target.wreck and target.activated:
				t_mat, t_pos, t_rot, aX, aY, aZ = target.decompose_matrix()
				aZ.y = 0
				aZ = hg.Normalize(aZ)
				aY = hg.Vec3(0, 1, 0)
				aX = hg.Cross(aY, aZ)
				matrot = hg.Mat3()
				hg.SetAxises(matrot, aX, aY, aZ)
				t_mat_trans = mat_trans * hg.TransformationMat4(t_pos, matrot)
				pos = hg.GetT(t_mat_trans)
				v2D = hg.Vec2(pos.x, pos.z) / radar_scale * rs / 2
				if abs(v2D.x) < rs / 2 - rm and abs(v2D.y) < rs / 2 - rm:

					if target.type == Destroyable_Machine.TYPE_MISSILE:
						plot = cls.missiles_plots[i_missile]
						i_missile += 1
					elif target.type == Destroyable_Machine.TYPE_AIRCRAFT:
						plot = cls.aircrafts_plots[i_aircraft]
						i_aircraft += 1
					elif target.type == Destroyable_Machine.TYPE_SHIP:
						plot = cls.ships_plots[i_ship]
						i_ship += 1
					elif target.type == Destroyable_Machine.TYPE_MISSILE_LAUNCHER:
						plot = cls.missile_launchers_plots[i_missile_launcher]
						i_missile_launcher += 1
					t_mat_rot = hg.GetRotationMatrix(t_mat_trans)
					a = 0.5 + 0.5 * abs(sin(t * uniform(1, 500)))
				else:
					if target.type == Destroyable_Machine.TYPE_MISSILE: continue
					dir = hg.Normalize(v2D)
					v2D = dir * (rs / 2 - rm)
					plot = cls.dir_plot
					aZ = hg.Vec3(dir.x, 0, dir.y)
					aX = hg.Cross(hg.Vec3.Up, aZ)
					t_mat_rot = hg.Mat3(aX, hg.Vec3.Up, aZ)
					a = 0.5 + 0.5 * abs(sin(t * uniform(1, 500)))

				v2D *= Main.resolution.y / 2
				cx, cy = rx + v2D.x, ry + v2D.y

				if td is not None and target == td.get_target():
					c = hg.Color(0.85, 1., 0.25, a)
				elif target.nationality == machine.nationality:
					c = hg.Color(0.25, 1., 0.25, a)
				else:
					c = hg.Color(1., 0.5, 0.5, a)

				rot = hg.ToEuler(t_mat_rot)
				plot.set_position(cx, cy)
				plot.rotation.z = -rot.y
				plot.set_size(plot_size / plot.width)
				plot.set_color(c)
				Main.sprites_display_list.append(plot)

		cls.spr_noise.set_position(rx, ry)
		cls.spr_noise.set_color(hg.Color(1, 1, 1, max(pow(1 - machine.health_level, 2), 0.05)))
		cls.spr_noise.set_uv_scale(hg.Vec2((0.75 + 0.25 * sin(t * 538)) - (0.25 + 0.25 * sin(t * 103)), (0.75 + 0.25 * cos(t * 120)) - ((0.65 + 0.35 * sin(t * 83)))))
		Main.sprites_display_list.append(cls.spr_noise)

		cls.spr_radar_light.set_position(rx, ry)
		cls.spr_radar_light.set_color(hg.Color(1, 1, 1, 0.3))
		Main.sprites_display_list.append(cls.spr_radar_light)

		cls.spr_radar_box.set_position(rx, ry)
		cls.spr_radar_box.set_color(hg.Color(1, 1, 1, 1))
		Main.sprites_display_list.append(cls.spr_radar_box)


class HUD_MachineGun:
	spr_machine_gun_sight = None

	@classmethod
	def init(cls, resolution:hg.Vec2):
		cls.spr_machine_gun_sight = Sprite(64, 64, "sprites/machine_gun_sight.png")
		cls.spr_machine_gun_sight.set_color(hg.Color(0.5, 1, 0.5, 1))

	@classmethod
	def update(cls, main, machine):
		mat, pos, rot, aX, aY, aZ = machine.decompose_matrix()
		aZ = hg.GetZ(mat)
		aZ = hg.Normalize(aZ)
		gp = hg.Vec3(0, 0, 0)
		for gs in machine.machine_gun_slots:
			gp = gp + hg.GetT(gs.GetTransform().GetWorld())
		gp = gp / len(machine.machine_gun_slots)
		p = gp + aZ * 500
		p2D = main.get_2d_hud(p)
		if p2D is not None:
			cls.spr_machine_gun_sight.set_position(p2D.x, p2D.y)
			main.sprites_display_list.append(cls.spr_machine_gun_sight)


class HUD_MissileTarget:
	spr_target_sight = None
	spr_missile_sight = None

	@classmethod
	def init(cls, resolution: hg.Vec2):
		cls.spr_target_sight = Sprite(64, 64, "sprites/target_sight.png")
		cls.spr_missile_sight = Sprite(64, 64, "sprites/missile_sight.png")

		cls.spr_target_sight.set_size((32 / 1600 * resolution.x) / cls.spr_target_sight.width)
		cls.spr_missile_sight.set_size((32 / 1600 * resolution.x) / cls.spr_missile_sight.width)

	@classmethod
	def display_selected_target(cls, main, selected_machine):
		mat, pos, rot, aX, aY, aZ = selected_machine.decompose_matrix()
		p2D = main.get_2d_hud(pos)
		if p2D is not None:
			msg = selected_machine.name
			x = (p2D.x / main.resolution.x - 12 / 1600)
			c = hg.Color(1, 1, 0.0, 1.0)
			cls.spr_target_sight.set_position(p2D.x, p2D.y)
			cls.spr_target_sight.set_color(c)
			main.sprites_display_list.append(cls.spr_target_sight)
			Overlays.add_text2D(msg, hg.Vec2(x, (p2D.y / main.resolution.y - 24 / 900)), 0.012, c, main.hud_font)

	@classmethod
	def update(cls, main, machine):
		tps = hg.time_to_sec_f(hg.GetClock())
		td = machine.get_device("TargettingDevice")
		if td is not None:
			target = td.get_target()
			f = 1  # Main.HSL_postProcess.GetL()
			if target is not None:
				p2D = main.get_2d_hud(target.get_parent_node().GetTransform().GetPos())
				if p2D is not None:
					a_pulse = 0.5 if (sin(tps * 20) > 0) else 0.75
					if td.target_locked:
						c = hg.Color(1., 0.5, 0.5, a_pulse)
						msg = "LOCKED - " + str(int(td.target_distance))
						x = (p2D.x / main.resolution.x - 32 / 1600)
						a = a_pulse
					else:
						msg = str(int(td.target_distance))
						x = (p2D.x / main.resolution.x - 12 / 1600)
						c = hg.Color(0.5, 1, 0.5, 0.75)

					c.a *= f
					cls.spr_target_sight.set_position(p2D.x, p2D.y)
					cls.spr_target_sight.set_color(c)
					main.sprites_display_list.append(cls.spr_target_sight)

					if td.target_out_of_range:
						Overlays.add_text2D("OUT OF RANGE", hg.Vec2(p2D.x / main.resolution.x - 40 / 1600, p2D.y / main.resolution.y - 24 / 900), 0.012, hg.Color(0.2, 1, 0.2, a_pulse * f), main.hud_font)
					else:
						Overlays.add_text2D(msg, hg.Vec2(x, (p2D.y / main.resolution.y - 24 / 900)), 0.012, c, main.hud_font)

					if td.target_locking_state > 0:
						t = sin(td.target_locking_state * pi - pi / 2) * 0.5 + 0.5
						p2D = hg.Vec2(0.5, 0.5) * (1 - t) + p2D * t
						cls.spr_missile_sight.set_position(p2D.x, p2D.y)
						cls.spr_missile_sight.set_color(c)
						main.sprites_display_list.append(cls.spr_missile_sight)

				c = hg.Color(0, 1, 0, f)

				Overlays.add_text2D("Target dist: %d" % (td.target_distance), hg.Vec2(0.05, 0.91), 0.016, c, main.hud_font)
				Overlays.add_text2D("Target heading: %d" % (td.target_heading),hg.Vec2(0.05, 0.89), 0.016, c, main.hud_font)
				Overlays.add_text2D("Target alt: %d" % (td.target_altitude), hg.Vec2(0.05, 0.87), 0.016, c, main.hud_font)


class HUD_Aircraft:

	@classmethod
	def draw_altitude_chart(cls, Main, aircraft: Aircraft):
		"""绘制实时高度曲线图 - 横轴时间，纵轴高度"""
		f = 1  # 亮度因子
		
		if not hasattr(aircraft, 'altitude_history'):
			return
		
		history = aircraft.altitude_history
		if len(history) < 2:
			return
		
		# 图表位置和尺寸 - 更大的图表
		chart_x = 0.60  # 右侧位置
		chart_y = 0.55  # 垂直位置
		chart_width = 0.38  # 图表宽度（更宽）
		chart_height = 0.35  # 图表高度（更高）
		
		# 绘制图表标题
		Overlays.add_text2D("ALTITUDE (高度)", hg.Vec2(chart_x + 0.0, chart_y + chart_height + 0.035), 0.014, hg.Color(1, 1, 1, 1) * f, Main.hud_font)
		Overlays.add_text2D("TIME (时间) →", hg.Vec2(chart_x + chart_width - 0.08, chart_y - 0.025), 0.012, hg.Color(0.8, 0.8, 0.8, 0.8) * f, Main.hud_font)
		
		# 计算高度范围
		if len(history) > 0:
			min_alt = min(history)
			max_alt = max(history)
			alt_range = max_alt - min_alt
			
			# 如果范围太小，设置一个最小范围
			if alt_range < 100:
				alt_range = 100
				min_alt = (max_alt + min_alt) / 2 - 50
				max_alt = min_alt + 100
			
			# 添加一些边距
			margin = alt_range * 0.15
			min_alt -= margin
			max_alt += margin
			alt_range = max_alt - min_alt
			
			# 显示当前高度（大号显示）
			current_alt = history[-1]
			Overlays.add_text2D("%.0f m" % current_alt, hg.Vec2(chart_x + 0.0, chart_y + chart_height + 0.015), 0.022, hg.Color(0.2, 1, 0.5, 1) * f, Main.hud_font)
			
			# Y轴刻度（高度）- 显示3个刻度
			Overlays.add_text2D("%.0f" % max_alt, hg.Vec2(chart_x - 0.05, chart_y + chart_height - 0.01), 0.012, hg.Color(0.8, 0.8, 0.8, 0.9) * f, Main.hud_font)
			mid_alt = (max_alt + min_alt) / 2
			Overlays.add_text2D("%.0f" % mid_alt, hg.Vec2(chart_x - 0.05, chart_y + chart_height/2 - 0.01), 0.012, hg.Color(0.8, 0.8, 0.8, 0.9) * f, Main.hud_font)
			Overlays.add_text2D("%.0f" % min_alt, hg.Vec2(chart_x - 0.05, chart_y - 0.01), 0.012, hg.Color(0.8, 0.8, 0.8, 0.9) * f, Main.hud_font)
			
			# 绘制坐标轴
			# Y轴（左侧）
			for i in range(int(chart_height * 100)):
				y_pos = chart_y + (i / 100.0)
				Overlays.add_text2D("│", hg.Vec2(chart_x, y_pos), 0.012, hg.Color(0.5, 0.5, 0.5, 0.4) * f, Main.hud_font)
			
			# X轴（底部）
			for i in range(int(chart_width * 50)):
				x_pos = chart_x + (i / 50.0)
				Overlays.add_text2D("─", hg.Vec2(x_pos, chart_y), 0.012, hg.Color(0.5, 0.5, 0.5, 0.4) * f, Main.hud_font)
			
			# 绘制水平参考线
			for i in range(5):
				y_ref = chart_y + (i * chart_height / 4)
				for j in range(int(chart_width * 30)):
					x_pos = chart_x + (j / 30.0)
					if j % 3 == 0:  # 虚线效果
						Overlays.add_text2D("·", hg.Vec2(x_pos, y_ref), 0.008, hg.Color(0.4, 0.4, 0.4, 0.3) * f, Main.hud_font)
			
			# 绘制曲线 - 更粗更明显
			num_points = len(history)
			step_x = chart_width / max(1, num_points - 1)
			
			# 转换历史数据为屏幕坐标并绘制
			prev_x = None
			prev_y = None
			
			for i in range(num_points):
				alt = history[i]
				# 归一化高度到图表范围
				normalized_alt = (alt - min_alt) / alt_range if alt_range > 0 else 0.5
				
				# 计算屏幕位置
				x = chart_x + (i * step_x)
				y = chart_y + normalized_alt * chart_height
				
				# 绘制点和线段
				if prev_x is not None and prev_y is not None:
					# 计算两点之间的距离
					dx = x - prev_x
					dy = y - prev_y
					distance = (dx * dx + dy * dy) ** 0.5
					
					# 在两点之间插入多个点来绘制平滑曲线
					segments = max(2, int(distance * 150))
					for j in range(segments):
						t = j / max(1, segments)
						interp_x = prev_x + dx * t
						interp_y = prev_y + dy * t
						
						# 根据时间位置选择颜色（从旧到新）
						age_factor = i / max(1, num_points - 1)
						if age_factor < 0.7:
							color = hg.Color(0.2, 0.6, 0.2, 0.7)  # 历史：暗绿色
						else:
							# 最近的数据用渐变的亮绿色
							brightness = 0.6 + 0.4 * ((age_factor - 0.7) / 0.3)
							color = hg.Color(0.3, brightness, 0.3, 1.0)
						
						# 绘制粗线（多个点重叠）
						Overlays.add_text2D("●", hg.Vec2(interp_x, interp_y), 0.012, color * f, Main.hud_font)
						Overlays.add_text2D("●", hg.Vec2(interp_x + 0.001, interp_y), 0.012, color * f, Main.hud_font)
				
				prev_x = x
				prev_y = y
			
			# 绘制当前高度标记（最后一个点）- 更大更醒目
			if prev_x is not None and prev_y is not None:
				Overlays.add_text2D("◆", hg.Vec2(prev_x, prev_y), 0.025, hg.Color(1, 1, 0, 1) * f, Main.hud_font)
				Overlays.add_text2D("◆", hg.Vec2(prev_x - 0.002, prev_y), 0.025, hg.Color(1, 1, 0, 0.5) * f, Main.hud_font)
				Overlays.add_text2D("◆", hg.Vec2(prev_x + 0.002, prev_y), 0.025, hg.Color(1, 1, 0, 0.5) * f, Main.hud_font)

	@classmethod
	def update(cls, Main, aircraft: Aircraft, targets):
		f = 1  # Main.HSL_postProcess.GetL()
		tps = hg.time_to_sec_f(hg.GetClock())
		a_pulse = 0.1 if (sin(tps * 25) > 0) else 0.9
		hs, vs = aircraft.get_world_speed()
		if Main.flag_network_mode:
			if Main.flag_client_connected:
				Overlays.add_text2D("Client connected", hg.Vec2(0.05, 0.98), 0.016, HUD.color_connected * f, Main.hud_font)
			else:
				h, p = Main.get_network()
				Overlays.add_text2D("Host: " + h + " Port: " + str(p), hg.Vec2(0.05, 0.98), 0.016, HUD.color_wait_connect * f, Main.hud_font)

		if aircraft.flag_custom_physics_mode:
			Overlays.add_text2D("Custom physics", hg.Vec2(0.05, 0.92), 0.016, hg.Color.White * f, Main.hud_font)

		# 只显示关键信息
		Overlays.add_text2D("Health: %d%%" % (aircraft.health_level * 100), hg.Vec2(0.05, 0.96), 0.018, (hg.Color.White * aircraft.health_level + hg.Color.Red * (1 - aircraft.health_level)) * f, Main.hud_font)
		Overlays.add_text2D("Speed: %d km/h" % (aircraft.get_linear_speed() * 3.6), hg.Vec2(0.05, 0.94), 0.018, hg.Color.White * f, Main.hud_font)
		
		# 显示仿真速度（如果不是1.0x）
		if Main.simulation_speed != 1.0:
			speed_color = hg.Color(1, 0.8, 0, 1) if Main.simulation_speed < 3 else hg.Color(1, 0.5, 0, 1)
			Overlays.add_text2D("SIM: %.1fx" % Main.simulation_speed, hg.Vec2(0.05, 0.90), 0.020, speed_color * f, Main.hud_font)
		
		# 显示性能监控信息
		if Main.flag_show_performance:
			y_pos = 0.88 if Main.simulation_speed != 1.0 else 0.90
			Overlays.add_text2D("=== PERFORMANCE ===", hg.Vec2(0.05, y_pos), 0.014, hg.Color(1, 1, 0, 1) * f, Main.hud_font)
			Overlays.add_text2D("Physics: %.1f ms" % Main.perf_physics_time, hg.Vec2(0.05, y_pos - 0.02), 0.013, hg.Color(0.5, 1, 0.5, 1) * f, Main.hud_font)
			Overlays.add_text2D("Render: %.1f ms" % Main.perf_render_time, hg.Vec2(0.05, y_pos - 0.04), 0.013, hg.Color(0.5, 0.8, 1, 1) * f, Main.hud_font)
			Overlays.add_text2D("Total: %.1f ms" % Main.perf_total_time, hg.Vec2(0.05, y_pos - 0.06), 0.013, hg.Color(1, 1, 1, 1) * f, Main.hud_font)
			target_fps = 60
			frame_time = 1000.0 / target_fps
			efficiency = min(100, (frame_time / max(0.01, Main.perf_total_time)) * 100)
			eff_color = hg.Color(0.5, 1, 0.5, 1) if efficiency > 80 else hg.Color(1, 1, 0, 1) if efficiency > 50 else hg.Color(1, 0.5, 0.5, 1)
			Overlays.add_text2D("Efficiency: %.0f%%" % efficiency, hg.Vec2(0.05, y_pos - 0.08), 0.013, eff_color * f, Main.hud_font)

		# 简化起落架显示
		gear = aircraft.get_device("Gear")
		if gear is not None and gear.activated:
			Overlays.add_text2D("⚠ GEAR", hg.Vec2(0.05, 0.92), 0.016, hg.Color(0.8, 1, 0.2, 1) * f, Main.hud_font)
		
		flag_internal_physics = not aircraft.get_custom_physics_mode()

		# 简化警告信息
		if flag_internal_physics and aircraft.playfield_distance > Destroyable_Machine.playfield_safe_distance:
			Overlays.add_text2D("⚠ OUT OF BOUNDS", hg.Vec2(0.42, 0.50), 0.020, hg.Color.Red * a_pulse * f, Main.hud_font)


		alt = aircraft.get_altitude()
		terrain_alt = aircraft.terrain_altitude
		
		# 只显示关键警告信息
		if alt > aircraft.max_safe_altitude and flag_internal_physics:
			Overlays.add_text2D("⚠ AIR DENSITY LOW", hg.Vec2(0.42, 0.52), 0.018, hg.Color.Red * a_pulse * f, Main.hud_font)

		ls = aircraft.get_linear_speed() * 3.6

		# 只显示关键状态警告
		if ls < aircraft.minimum_flight_speed and not aircraft.flag_landed:
			Overlays.add_text2D("⚠ LOW SPEED", hg.Vec2(0.45, 0.08), 0.020, hg.Color(1., 0, 0, a_pulse) * f, Main.hud_font)
		if aircraft.flag_landed:
			Overlays.add_text2D("LANDED", hg.Vec2(0.46, 0.08), 0.018, hg.Color(0.2, 1, 0.2, a_pulse) * f, Main.hud_font)

		# 加速度显示 - 简化显示
		acc = aircraft.get_linear_acceleration()
		# 根据加速度大小选择颜色
		if abs(acc) < 2:
			acc_color = hg.Color(0.5, 1, 0.5, 1)  # 绿色
		elif abs(acc) < 5:
			acc_color = hg.Color(1, 1, 0, 1)  # 黄色
		elif abs(acc) < 8:
			acc_color = hg.Color(1, 0.6, 0, 1)  # 橙色
		else:
			acc_color = hg.Color(1, 0.2, 0.2, 1)  # 红色
		
		# 底部简洁显示关键信息
		Overlays.add_text2D("ACC: %.1f m/s²" % acc, hg.Vec2(0.42, 0.04), 0.018, acc_color * f, Main.hud_font)
		Overlays.add_text2D("Thrust: %d%%" % (aircraft.get_thrust_level() * 100), hg.Vec2(0.53, 0.04), 0.018, hg.Color.White * f, Main.hud_font)

		# 移除垂直加速度指示器，保持界面简洁

		# 绘制高度曲线图
		cls.draw_altitude_chart(Main, aircraft)
		
		HUD_Radar.update(Main, aircraft, targets)
		HUD_MissileTarget.update(Main, aircraft)

		if not Main.satellite_view:
			HUD_MachineGun.update(Main, aircraft)


class HUD_MissileLauncher:

	@classmethod
	def update(cls, Main, aircraft:MissileLauncherS400, targets):
		f = 1  # Main.HSL_postProcess.GetL()
		tps = hg.time_to_sec_f(hg.GetClock())
		a_pulse = 0.1 if (sin(tps * 25) > 0) else 0.9
		if Main.flag_network_mode:
			if Main.flag_client_connected:
				Overlays.add_text2D("Client connected", hg.Vec2(0.05, 0.98), 0.016, HUD.color_connected * f, Main.hud_font)
			else:
				h, p = Main.get_network()
				Overlays.add_text2D("Host: " + h + " Port: " + str(p), hg.Vec2(0.05, 0.98), 0.016, HUD.color_wait_connect * f, Main.hud_font)

		if aircraft.flag_custom_physics_mode:
			Overlays.add_text2D("Custom physics", hg.Vec2(0.05, 0.92), 0.016, hg.Color.White * f, Main.hud_font)

		Overlays.add_text2D("Health: %d" % (aircraft.health_level * 100), hg.Vec2(0.05, 0.96), 0.016, (hg.Color.White * aircraft.health_level + hg.Color.Red * (1 - aircraft.health_level)) * f, Main.hud_font)

		Overlays.add_text2D("Heading: %d" % (aircraft.get_heading()), hg.Vec2(0.49, 0.96), 0.016, hg.Color.White * f, Main.hud_font)

		iactrl = aircraft.get_device("IAControlDevice")
		if iactrl is not None:
			if iactrl.is_activated():
				c = hg.Color.Orange
			else:
				c = HUD.color_inactive
			Overlays.add_text2D("IA Activated", hg.Vec2(0.45, 0.94), 0.015, c * f, Main.hud_font)

		flag_internal_physics = not aircraft.get_custom_physics_mode()

		if flag_internal_physics and aircraft.playfield_distance > Destroyable_Machine.playfield_safe_distance:
			Overlays.add_text2D("Position Out of battle field !", hg.Vec2(0.43, 0.52), 0.018, hg.Color.Red * f, Main.hud_font)
			Overlays.add_text2D("Turn back now or you'll be destroyed !", hg.Vec2(0.405, 0.48), 0.018, hg.Color.Red * a_pulse * f, Main.hud_font)

		alt = aircraft.get_altitude()
		terrain_alt = aircraft.terrain_altitude
		c = hg.Color.White
		Overlays.add_text2D("Altitude (m): %d" % (alt),  hg.Vec2(0.8, 0.93), 0.016, c * f, Main.hud_font)
		Overlays.add_text2D("Ground (m): %d" % (terrain_alt),  hg.Vec2(0.8, 0.91), 0.016, c * f, Main.hud_font)

		Overlays.add_text2D("Pitch attitude: %d" % (aircraft.get_pitch_attitude()), hg.Vec2(0.8, 0.14), 0.016, hg.Color.White * f, Main.hud_font)
		Overlays.add_text2D("Roll attitude: %d" % (aircraft.get_roll_attitude()), hg.Vec2(0.8, 0.12), 0.016, hg.Color.White * f, Main.hud_font)

		ls = aircraft.get_linear_speed() * 3.6

		Overlays.add_text2D("Linear speed (km/h): %d" % (ls), hg.Vec2(0.8, 0.06), 0.016, hg.Color.White * f, Main.hud_font)

		# 加速度显示 - 带颜色编码
		acc = aircraft.get_linear_acceleration()
		# 根据加速度大小选择颜色
		if abs(acc) < 2:
			acc_color = hg.Color(0.5, 1, 0.5, 1)  # 绿色 - 低加速度
		elif abs(acc) < 5:
			acc_color = hg.Color(1, 1, 0, 1)  # 黄色 - 中等加速度
		elif abs(acc) < 8:
			acc_color = hg.Color(1, 0.6, 0, 1)  # 橙色 - 高加速度
		else:
			acc_color = hg.Color(1, 0.2, 0.2, 1)  # 红色 - 极高加速度
		
		# 大号加速度数值显示（屏幕中上方）
		Overlays.add_text2D("ACCELERATION", hg.Vec2(0.42, 0.92), 0.016, hg.Color(0.8, 0.8, 0.8, 1) * f, Main.hud_font)
		Overlays.add_text2D("%.2f m/s²" % acc, hg.Vec2(0.435, 0.88), 0.028, acc_color * f, Main.hud_font)
		
		# 左上角也显示（备用位置）
		Overlays.add_text2D("ACC: %.2f m/s²" % acc, hg.Vec2(0.05, 0.85), 0.018, acc_color * f, Main.hud_font)
		
		Overlays.add_text2D("Linear acceleration (m.s2): %.2f" % acc, hg.Vec2(0.8, 0.02), 0.016, hg.Color.White * f, Main.hud_font)
		Overlays.add_text2D("Thrust: %d %%" % (aircraft.get_thrust_level() * 100), hg.Vec2(0.47, 0.1), 0.016, hg.Color.White * f, Main.hud_font)

		if aircraft.brake_level > 0:
			Overlays.add_text2D("Brake: %d %%" % (aircraft.get_brake_level() * 100), hg.Vec2(0.43, 0.046), 0.016, hg.Color(1, 0.4, 0.4) * f, Main.hud_font)

		HUD_Radar.update(Main, aircraft, targets)
		HUD_MissileTarget.update(Main, aircraft)
