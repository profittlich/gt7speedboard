import struct
from datetime import timedelta as td
from sb.crypt import salsa20_dec, salsa20_enc

class Point:

    def __init__(self, ddata, encRaw):
        self.raw = encRaw

        self.unknown = []

	# TODO handle indexes 0, 0x40 and 0x100
        self.magic = struct.unpack('i', ddata[0x00:0x00 + 4])[0] # 0x47375330

        # based on https://github.com/snipem/gt7dashboard/blob/main/gt7dashboard/gt7communication.py
        # additional info from https://github.com/Nenkai/PDTools/blob/8df793cd8ce46dbbcb202fde75f87b3989ca7782/PDTools.SimulatorInterface/SimulatorPacketG7S0.cs
        self.position_x = struct.unpack('f', ddata[0x04:0x04 + 4])[0]  # pos X
        self.position_y = struct.unpack('f', ddata[0x08:0x08 + 4])[0]  # pos Y
        self.position_z = struct.unpack('f', ddata[0x0C:0x0C + 4])[0]  # pos Z

        self.velocity_x = struct.unpack('f', ddata[0x10:0x10 + 4])[0]  # velocity X
        self.velocity_y = struct.unpack('f', ddata[0x14:0x14 + 4])[0]  # velocity Y
        self.velocity_z = struct.unpack('f', ddata[0x18:0x18 + 4])[0]  # velocity Z

        self.rotation_pitch = struct.unpack('f', ddata[0x1C:0x1C + 4])[0]  # rot Pitch
        self.rotation_yaw = struct.unpack('f', ddata[0x20:0x20 + 4])[0]  # rot Yaw
        self.rotation_roll = struct.unpack('f', ddata[0x24:0x24 + 4])[0]  # rot Roll

	# TODO store index along with value
        self.unknown.append( struct.unpack('f', ddata[0x28:0x28+4])[0])					# rot ??? (TODO RelativeOrientationToNorth????)

        self.angular_velocity_x = struct.unpack('f', ddata[0x2C:0x2C + 4])[0]  # angular velocity X
        self.angular_velocity_y = struct.unpack('f', ddata[0x30:0x30 + 4])[0]  # angular velocity Y
        self.angular_velocity_z = struct.unpack('f', ddata[0x34:0x34 + 4])[0]  # angular velocity Z
        
        self.ride_height = 1000 * struct.unpack('f', ddata[0x38:0x38 + 4])[0]  # ride height
        self.rpm = struct.unpack('f', ddata[0x3C:0x3C + 4])[0]  # rpm

        self.unknown.append(struct.unpack('I', ddata[0x40:0x40+4])[0])		# Unknown/empty?

        self.current_fuel = struct.unpack('f', ddata[0x44:0x44 + 4])[0]  # fuel
        self.fuel_capacity = struct.unpack('f', ddata[0x48:0x48 + 4])[0]
        self.car_speed = 3.6 * struct.unpack('f', ddata[0x4C:0x4C + 4])[0] # m/s to km/h
        self.boost = struct.unpack('f', ddata[0x50:0x50 + 4])[0] - 1  # boost
        self.oil_pressure = struct.unpack('f', ddata[0x54:0x54 + 4])[0]  # oil pressure
        self.water_temp = struct.unpack('f', ddata[0x58:0x58 + 4])[0]  # water temp
        self.oil_temp = struct.unpack('f', ddata[0x5C:0x5C + 4])[0]  # oil temp

        self.tyre_temp_FL = struct.unpack('f', ddata[0x60:0x60 + 4])[0]  # tyre temp FL
        self.tyre_temp_FR = struct.unpack('f', ddata[0x64:0x64 + 4])[0]  # tyre temp FR
        self.tyre_temp_RL = struct.unpack('f', ddata[0x68:0x68 + 4])[0]  # tyre temp RL
        self.tyre_temp_RR = struct.unpack('f', ddata[0x6C:0x6C + 4])[0]  # tyre temp RR

        self.package_id = struct.unpack('i', ddata[0x70:0x70 + 4])[0]
        self.current_lap = struct.unpack('h', ddata[0x74:0x74 + 2])[0]
        self.total_laps = struct.unpack('h', ddata[0x76:0x76 + 2])[0]  # total laps
        self.best_lap = struct.unpack('i', ddata[0x78:0x78 + 4])[0]
        self.last_lap = struct.unpack('i', ddata[0x7C:0x7C + 4])[0]

        self.raw_time_on_track = struct.unpack('i', ddata[0x80:0x80 + 4])[0]
        self.time_on_track = td(seconds=round(struct.unpack('i', ddata[0x80:0x80 + 4])[0] / 1000))  # time of day on track

        self.current_position = struct.unpack('h', ddata[0x84:0x84 + 2])[0]  # current position (TODO PreRaceStartPositionOrQualiPos????)
        self.total_positions = struct.unpack('h', ddata[0x86:0x86 + 2])[0]  # total positions

        self.rpm_rev_warning = struct.unpack('H', ddata[0x88:0x88 + 2])[0]  # rpm rev warning
        self.rpm_rev_limiter = struct.unpack('H', ddata[0x8A:0x8A + 2])[0]  # rpm rev limiter

        self.estimated_top_speed = struct.unpack('h', ddata[0x8C:0x8C + 2])[0]  # estimated top speed

        self.in_race = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-1] == '1' # "car on track"
        self.is_paused = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-2] == '1'

        self.loading_or_processing = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-3] == '1'

        self.in_gear = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-4] == '1'
        self.has_turbo = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-5] == '1'
        self.rev_limiter_blink_alert_active = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-6] == '1'
        self.hand_brake_active = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-7] == '1'
        self.lights_active = bin(struct.unpack('B', ddata[0x8E:0x8E + 1])[0])[-8] == '1'
        self.high_beam_active = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-1] == '1'
        self.low_beam_active = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-2] == '1'
        self.asm_active = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-3] == '1'
        self.tcs_active = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-4] == '1'
        self.reserved_flag_13 = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-5] == '1'
        self.reserved_flag_14 = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-6] == '1'
        self.reserved_flag_15 = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-7] == '1'
        self.reserved_flag_16 = bin(struct.unpack('B', ddata[0x8F:0x8F + 1])[0])[-8] == '1'

        self.current_gear = struct.unpack('B', ddata[0x90:0x90 + 1])[0] & 0b00001111
        self.suggested_gear = struct.unpack('B', ddata[0x90:0x90 + 1])[0] >> 4

        self.throttle = struct.unpack('B', ddata[0x91:0x91 + 1])[0] / 2.55  # throttle

        self.brake = struct.unpack('B', ddata[0x92:0x92 + 1])[0] / 2.55  # brake

        self.unknown.append( bin(struct.unpack('B', ddata[0x93:0x93+1])[0])[2:])	# 0x93 = ???, always 0?

        self.normal_x = struct.unpack('f', ddata[0x94:0x94+4])[0]			# 0x94 = CAR NORMAL X
        self.normal_y = struct.unpack('f', ddata[0x98:0x98+4])[0]			# 0x98 = CAR NORMAL Y
        self.normal_z = struct.unpack('f', ddata[0x9C:0x9C+4])[0]			# 0x9C = CAR NORMAL Z

        self.unknown.append( struct.unpack('f', ddata[0xA0:0xA0+4])[0])			# 0xA0 = ??? (TODO RoadPlaneDistance???)

        self.tyre_speed_FL = abs(3.6 * self.tyre_diameter_FL * struct.unpack('f', ddata[0xA4:0xA4 + 4])[0])
        self.tyre_speed_FR = abs(3.6 * self.tyre_diameter_FR * struct.unpack('f', ddata[0xA8:0xA8 + 4])[0])
        self.tyre_speed_RL = abs(3.6 * self.tyre_diameter_RL * struct.unpack('f', ddata[0xAC:0xAC + 4])[0])
        self.tyre_speed_RR = abs(3.6 * self.tyre_diameter_RR * struct.unpack('f', ddata[0xB0:0xB0 + 4])[0])

        self.tyre_diameter_FL = struct.unpack('f', ddata[0xB4:0xB4 + 4])[0]
        self.tyre_diameter_FR = struct.unpack('f', ddata[0xB8:0xB8 + 4])[0]
        self.tyre_diameter_RL = struct.unpack('f', ddata[0xBC:0xBC + 4])[0]
        self.tyre_diameter_RR = struct.unpack('f', ddata[0xC0:0xC0 + 4])[0]

        self.suspension_FL = struct.unpack('f', ddata[0xC4:0xC4 + 4])[0]  # suspension FL
        self.suspension_FR = struct.unpack('f', ddata[0xC8:0xC8 + 4])[0]  # suspension FR
        self.suspension_RL = struct.unpack('f', ddata[0xCC:0xCC + 4])[0]  # suspension RL
        self.suspension_RR = struct.unpack('f', ddata[0xD0:0xD0 + 4])[0]  # suspension RR

        self.unknown.append( struct.unpack('f', ddata[0xD4:0xD4+4])[0])			# 0xD4 = ???, always 0?
        self.unknown.append( struct.unpack('f', ddata[0xD8:0xD8+4])[0])			# 0xD8 = ???, always 0?
        self.unknown.append( struct.unpack('f', ddata[0xDC:0xDC+4])[0])			# 0xDC = ???, always 0?
        self.unknown.append( struct.unpack('f', ddata[0xE0:0xE0+4])[0])			# 0xE0 = ???, always 0?

        self.unknown.append( struct.unpack('f', ddata[0xE4:0xE4+4])[0])			# 0xE4 = ???, always 0?
        self.unknown.append( struct.unpack('f', ddata[0xE8:0xE8+4])[0])			# 0xE8 = ???, always 0?
        self.unknown.append( struct.unpack('f', ddata[0xEC:0xEC+4])[0])			# 0xEC = ???, always 0?
        self.unknown.append( struct.unpack('f', ddata[0xF0:0xF0+4])[0])			# 0xF0 = ???, always 0?

        self.clutch = struct.unpack('f', ddata[0xF4:0xF4 + 4])[0]  # clutch
        self.clutch_engaged = struct.unpack('f', ddata[0xF8:0xF8 + 4])[0]  # clutch engaged
        self.rpm_after_clutch = struct.unpack('f', ddata[0xFC:0xFC + 4])[0]  # rpm after clutch

        self.unknown.append(struct.unpack('f', ddata[0x100:0x100+4])[0])		# 0x100 = ??? (TODO TransmissionTopSpeed???)

        self.gear_1 = struct.unpack('f', ddata[0x104:0x104 + 4])[0]  # 1st gear
        self.gear_2 = struct.unpack('f', ddata[0x108:0x108 + 4])[0]  # 2nd gear
        self.gear_3 = struct.unpack('f', ddata[0x10C:0x10C + 4])[0]  # 3rd gear
        self.gear_4 = struct.unpack('f', ddata[0x110:0x110 + 4])[0]  # 4th gear
        self.gear_5 = struct.unpack('f', ddata[0x114:0x114 + 4])[0]  # 5th gear
        self.gear_6 = struct.unpack('f', ddata[0x118:0x118 + 4])[0]  # 6th gear
        self.gear_7 = struct.unpack('f', ddata[0x11C:0x11C + 4])[0]  # 7th gear
        self.gear_8 = struct.unpack('f', ddata[0x120:0x120 + 4])[0]  # 8th gear

        self.car_id = struct.unpack('i', ddata[0x124:0x124 + 4])[0]  # car id

        if self.car_speed > 0:
            self.tyre_slip_ratio_FL = '{:6.2f}'.format(self.tyre_speed_FL / self.car_speed)
            self.tyre_slip_ratio_FR = '{:6.2f}'.format(self.tyre_speed_FR / self.car_speed)
            self.tyre_slip_ratio_RL = '{:6.2f}'.format(self.tyre_speed_RL / self.car_speed)
            self.tyre_slip_ratio_RR = '{:6.2f}'.format(self.tyre_speed_RR / self.car_speed)
        else:
            self.tyre_slip_ratio_FL = 1
            self.tyre_slip_ratio_FR = 1
            self.tyre_slip_ratio_RL = 1
            self.tyre_slip_ratio_RR = 1

        # end of https://github.com/snipem/gt7dashboard/blob/main/gt7dashboard/gt7communication.py

        self.message = None

    def recreatePackage(self):
# TODO Update based on __init__ updates
        newPkt = bytearray(296)

        struct.pack_into ('i', newPkt, 0x00, self.magic)
        struct.pack_into ('i', newPkt, 0x70, self.package_id)
        struct.pack_into ('i', newPkt, 0x78, self.best_lap)
        struct.pack_into ('i', newPkt, 0x7C, self.last_lap)
        struct.pack_into ('h', newPkt, 0x74, self.current_lap)
        gearfield = self.current_gear + (self.suggested_gear << 4)
        struct.pack_into ('B', newPkt, 0x90, gearfield)
        struct.pack_into ('f', newPkt, 0x48, self.fuel_capacity)
        struct.pack_into ('f', newPkt, 0x44, self.current_fuel)
        struct.pack_into ('f', newPkt, 0x50, self.boost + 1)

        struct.pack_into ('f', newPkt, 0xB4, self.tyre_diameter_FL)
        struct.pack_into ('f', newPkt, 0xB8, self.tyre_diameter_FR)
        struct.pack_into ('f', newPkt, 0xBC, self.tyre_diameter_RL)
        struct.pack_into ('f', newPkt, 0xC0, self.tyre_diameter_RR)

        struct.pack_into ('f', newPkt, 0xA4, self.tyre_speed_FL)
        struct.pack_into ('f', newPkt, 0xA8, self.tyre_speed_FR)
        struct.pack_into ('f', newPkt, 0xAC, self.tyre_speed_RL)
        struct.pack_into ('f', newPkt, 0xB0, self.tyre_speed_RR)

        struct.pack_into ('f', newPkt, 0x4C, self.car_speed / 3.6)

        struct.pack_into ('i', newPkt, 0x80, self.raw_time_on_track)

        struct.pack_into ('h', newPkt, 0x76, self.total_laps)

        struct.pack_into ('h', newPkt, 0x84, self.current_position)
        struct.pack_into ('h', newPkt, 0x86, self.total_positions)

        struct.pack_into ('i', newPkt, 0x124, self.car_id)

        struct.pack_into ('B', newPkt, 0x91, int(round(self.throttle * 2.55)))
        struct.pack_into ('f', newPkt, 0x3C, self.rpm)
        struct.pack_into ('H', newPkt, 0x88, self.rpm_rev_warning)

        struct.pack_into ('B', newPkt, 0x92, int(round(self.brake * 2.55)))

        struct.pack_into ('H', newPkt, 0x8A, self.rpm_rev_limiter)

        struct.pack_into ('h', newPkt, 0x8C, self.estimated_top_speed)

        struct.pack_into ('f', newPkt, 0xF4, self.clutch)
        struct.pack_into ('f', newPkt, 0xF8, self.clutch_engaged)
        struct.pack_into ('f', newPkt, 0xFC, self.rpm_after_clutch)

        struct.pack_into ('f', newPkt, 0x5C, self.oil_temp)
        struct.pack_into ('f', newPkt, 0x58, self.water_temp)

        struct.pack_into ('f', newPkt, 0x54, self.oil_pressure)
        struct.pack_into ('f', newPkt, 0x38, self.ride_height)

        struct.pack_into ('f', newPkt, 0x60, self.tyre_temp_FL)
        struct.pack_into ('f', newPkt, 0x64, self.tyre_temp_FR)

        struct.pack_into ('f', newPkt, 0xC4, self.suspension_FL)
        struct.pack_into ('f', newPkt, 0xC8, self.suspension_FR)

        struct.pack_into ('f', newPkt, 0x68, self.tyre_temp_RL)
        struct.pack_into ('f', newPkt, 0x6C, self.tyre_temp_RR)

        struct.pack_into ('f', newPkt, 0xCC, self.suspension_RL)
        struct.pack_into ('f', newPkt, 0xD0, self.suspension_RR)

        struct.pack_into ('f', newPkt, 0x104, self.gear_1)
        struct.pack_into ('f', newPkt, 0x108, self.gear_2)
        struct.pack_into ('f', newPkt, 0x10C, self.gear_3)
        struct.pack_into ('f', newPkt, 0x110, self.gear_4)
        struct.pack_into ('f', newPkt, 0x114, self.gear_5)
        struct.pack_into ('f', newPkt, 0x118, self.gear_6)
        struct.pack_into ('f', newPkt, 0x11C, self.gear_7)
        struct.pack_into ('f', newPkt, 0x120, self.gear_8)

        struct.pack_into ('f', newPkt, 0x04, self.position_x)
        struct.pack_into ('f', newPkt, 0x08, self.position_y)
        struct.pack_into ('f', newPkt, 0x0C, self.position_z)

        struct.pack_into ('f', newPkt, 0x10, self.velocity_x)
        struct.pack_into ('f', newPkt, 0x14, self.velocity_y)
        struct.pack_into ('f', newPkt, 0x18, self.velocity_z)

        struct.pack_into ('f', newPkt, 0x1C, self.rotation_pitch)
        struct.pack_into ('f', newPkt, 0x20, self.rotation_yaw)
        struct.pack_into ('f', newPkt, 0x24, self.rotation_roll)

        struct.pack_into ('f', newPkt, 0x2C, self.angular_velocity_x)
        struct.pack_into ('f', newPkt, 0x30, self.angular_velocity_y)
        struct.pack_into ('f', newPkt, 0x34, self.angular_velocity_z)

        struct.pack_into ('B', newPkt, 0x8E, self.is_paused)
        struct.pack_into ('B', newPkt, 0x8E, self.in_race)

        struct.pack_into('f', newPkt, 0x28, self.unknown[0])

        #struct.pack_into('I', newPkt, 0x40, int(self.unknown[1])) TODO: fix

        struct.pack_into('B', newPkt, 0x8E, int(self.unknown[2],2))
        struct.pack_into('B', newPkt, 0x8F, int(self.unknown[3],2))
        struct.pack_into('B', newPkt, 0x93, int(self.unknown[4],2))

        struct.pack_into('f', newPkt, 0x94, self.unknown[5])
        struct.pack_into('f', newPkt, 0x98, self.unknown[6])
        struct.pack_into('f', newPkt, 0x9C, self.unknown[7])
        struct.pack_into('f', newPkt, 0xA0, self.unknown[8])

        struct.pack_into('f', newPkt, 0xD4, self.unknown[9])
        struct.pack_into('f', newPkt, 0xD8, self.unknown[10])
        struct.pack_into('f', newPkt, 0xDC, self.unknown[11])
        struct.pack_into('f', newPkt, 0xE0, self.unknown[12])

        struct.pack_into('f', newPkt, 0xE4, self.unknown[13])
        struct.pack_into('f', newPkt, 0xE8, self.unknown[14])
        struct.pack_into('f', newPkt, 0xEC, self.unknown[15])
        struct.pack_into('f', newPkt, 0xF0, self.unknown[16])

        struct.pack_into('f', newPkt, 0x100, self.unknown[17])

        encr = salsa20_enc(newPkt, 296)
        self.raw = encr


    def interpolate(self, other, alpha):
# TODO Update based on __init__ updates
        newdat = bytearray(296)

        self.magic = other.magic
        self.package_id = int(alpha * other.package_id + (1-alpha) * self.package_id)
        self.best_lap = other.best_lap
        self.last_lap = other.last_lap
        self.current_lap = other.current_lap
        self.current_gear = other.current_gear
        self.suggested_gear = other.suggested_gear
        self.fuel_capacity = alpha * other.fuel_capacity + (1-alpha) * self.fuel_capacity
        self.current_fuel = alpha * other.current_fuel + (1-alpha) * self.current_fuel
        self.boost = alpha * other.boost + (1-alpha) * self.boost

        self.tyre_diameter_FL = alpha * other.tyre_diameter_FL + (1-alpha) * self.tyre_diameter_FL
        self.tyre_diameter_FR = alpha * other.tyre_diameter_FR + (1-alpha) * self.tyre_diameter_FR
        self.tyre_diameter_RL = alpha * other.tyre_diameter_RL + (1-alpha) * self.tyre_diameter_RL
        self.tyre_diameter_RR = alpha * other.tyre_diameter_RR + (1-alpha) * self.tyre_diameter_RR

        self.tyre_speed_FL = alpha * other.tyre_speed_FL + (1-alpha) * self.tyre_speed_FL
        self.tyre_speed_FR = alpha * other.tyre_speed_FR + (1-alpha) * self.tyre_speed_FR
        self.tyre_speed_RL = alpha * other.tyre_speed_RL + (1-alpha) * self.tyre_speed_RL
        self.tyre_speed_RR = alpha * other.tyre_speed_RR + (1-alpha) * self.tyre_speed_RR

        self.car_speed = alpha * other.car_speed + (1-alpha) * self.car_speed

        self.time_on_track = alpha * other.time_on_track + (1-alpha) * self.time_on_track
        self.raw_time_on_track = int(alpha * other.raw_time_on_track + (1-alpha) * self.raw_time_on_track)

        self.total_laps = other.total_laps

        self.current_position = round(alpha * other.current_position + (1-alpha) * self.current_position)
        self.total_positions = other.total_positions

        self.car_id = other.car_id

        self.throttle = int(round(alpha * other.throttle + (1-alpha) * self.throttle))
        self.rpm = alpha * other.rpm + (1-alpha) * self.rpm
        self.rpm_rev_warning = int(round(alpha * other.rpm_rev_warning + (1-alpha) * self.rpm_rev_warning))

        self.brake = int(round(alpha * other.brake + (1-alpha) * self.brake))

        self.boost = alpha * other.boost + (1-alpha) * self.boost

        self.rpm_rev_limiter = int(round(alpha * other.rpm_rev_limiter + (1-alpha) * self.rpm_rev_limiter))

        self.estimated_top_speed = int(round(alpha * other.estimated_top_speed + (1-alpha) * self.estimated_top_speed))

        self.clutch = alpha * other.clutch + (1-alpha) * self.clutch
        self.clutch_engaged = alpha * other.clutch_engaged + (1-alpha) * self.clutch_engaged
        self.rpm_after_clutch = alpha * other.rpm_after_clutch + (1-alpha) * self.rpm_after_clutch

        self.oil_temp = alpha * other.oil_temp + (1-alpha) * self.oil_temp
        self.water_temp = alpha * other.water_temp + (1-alpha) * self.water_temp

        self.oil_pressure = alpha * other.oil_pressure + (1-alpha) * self.oil_pressure
        self.ride_height = alpha * other.ride_height + (1-alpha) * self.ride_height

        self.tyre_temp_FL = alpha * other.tyre_temp_FL + (1-alpha) * self.tyre_temp_FL
        self.tyre_temp_FR = alpha * other.tyre_temp_FR + (1-alpha) * self.tyre_temp_FR

        self.suspension_FL = alpha * other.suspension_FL + (1-alpha) * self.suspension_FL
        self.suspension_FR = alpha * other.suspension_FR + (1-alpha) * self.suspension_FR

        self.tyre_temp_RL = alpha * other.tyre_temp_RL + (1-alpha) * self.tyre_temp_RL
        self.tyre_temp_RR = alpha * other.tyre_temp_RR + (1-alpha) * self.tyre_temp_RR

        self.suspension_RL = alpha * other.suspension_RL + (1-alpha) * self.suspension_RL
        self.suspension_RR = alpha * other.suspension_RR + (1-alpha) * self.suspension_RR

        self.gear_1 = other.gear_1
        self.gear_2 = other.gear_2
        self.gear_3 = other.gear_3
        self.gear_4 = other.gear_4
        self.gear_5 = other.gear_5
        self.gear_6 = other.gear_6
        self.gear_7 = other.gear_7
        self.gear_8 = other.gear_8

        self.position_x = alpha * other.position_x + (1-alpha) * self.position_x
        self.position_y = alpha * other.position_y + (1-alpha) * self.position_y
        self.position_z = alpha * other.position_z + (1-alpha) * self.position_z

        self.velocity_x = alpha * other.velocity_x + (1-alpha) * self.velocity_x
        self.velocity_y = alpha * other.velocity_y + (1-alpha) * self.velocity_y
        self.velocity_z = alpha * other.velocity_z + (1-alpha) * self.velocity_z 

        self.rotation_pitch = alpha * other.rotation_pitch + (1-alpha) * self.rotation_pitch
        self.rotation_yaw = alpha * other.rotation_yaw + (1-alpha) * self.rotation_yaw
        self.rotation_roll = alpha * other.rotation_roll + (1-alpha) * self.rotation_roll

        self.angular_velocity_x = alpha * other.angular_velocity_x + (1-alpha) * self.angular_velocity_x
        self.angular_velocity_y = alpha * other.angular_velocity_y + (1-alpha) * self.angular_velocity_y
        self.angular_velocity_z = alpha * other.angular_velocity_z + (1-alpha) * self.angular_velocity_z

        self.is_paused = other.is_paused or self.is_paused
        self.in_race = other.in_race and self.in_race

        self.unknown[0] = ( alpha * other.unknown[0] + (1-alpha) * self.unknown[0])

        self.unknown[1] = other.unknown[1]

        self.unknown[2] = other.unknown[2]
        self.unknown[3] = other.unknown[3]
        self.unknown[4] = other.unknown[4]

        self.unknown[5] = ( alpha * other.unknown[5] + (1-alpha) * self.unknown[5])
        self.unknown[6] = ( alpha * other.unknown[6] + (1-alpha) * self.unknown[6])
        self.unknown[7] = ( alpha * other.unknown[7] + (1-alpha) * self.unknown[7])
        self.unknown[8] = ( alpha * other.unknown[8] + (1-alpha) * self.unknown[8])

        self.unknown[9] = ( alpha * other.unknown[9] + (1-alpha) * self.unknown[9])
        self.unknown[10] = ( alpha * other.unknown[10] + (1-alpha) * self.unknown[10])
        self.unknown[11] = ( alpha * other.unknown[11] + (1-alpha) * self.unknown[11])
        self.unknown[12] = ( alpha * other.unknown[12] + (1-alpha) * self.unknown[12])

        self.unknown[13] = ( alpha * other.unknown[13] + (1-alpha) * self.unknown[13])
        self.unknown[14] = ( alpha * other.unknown[14] + (1-alpha) * self.unknown[14])
        self.unknown[15] = ( alpha * other.unknown[15] + (1-alpha) * self.unknown[15])
        self.unknown[16] = ( alpha * other.unknown[16] + (1-alpha) * self.unknown[16])

        self.unknown[17] = ( alpha * other.unknown[17] + (1-alpha) * self.unknown[17])

        self.recreatePackage()

    def str(self):
        return str(self.position_x) + " " + str(self.position_y) + " " + str (self.position_z) + " " + str(self.current_lap)



