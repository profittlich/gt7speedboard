import struct
from datetime import timedelta as td
from sb.crypt import salsa20_dec, salsa20_enc

import inspect
def logPrint(*args, **kwargs):
    lines = inspect.stack()[1]
    print(lines.filename[lines.filename.rfind('/')+1:] + "::" +  str(lines.lineno) + " [" + lines.function + "()]:", *args, **kwargs)

class Point:

    def __init__(self, ddata, encRaw):
        self.raw = encRaw

        self.unknown = {}

        unpackFormat = 'ifffffffffffffffIfffffffffffihhiiihhHHhBBBBBBffffffffffffffffffffffffffffffffffffi'
        unpacked = struct.unpack(unpackFormat,ddata)

        self.magic = struct.unpack('i', ddata[0x00:0x00 + 4])[0] # 0x47375330
        if self.magic != unpacked[0]:
            logPrint("Mismatch")

        # based on https://github.com/snipem/gt7dashboard/blob/main/gt7dashboard/gt7communication.py
        # additional info from https://github.com/Nenkai/PDTools/blob/8df793cd8ce46dbbcb202fde75f87b3989ca7782/PDTools.SimulatorInterface/SimulatorPacketG7S0.cs
        self.position_x = struct.unpack('f', ddata[0x04:0x04 + 4])[0]  # pos X
        if self.position_x != unpacked[1]:
            logPrint("Mismatch")
        self.position_y = struct.unpack('f', ddata[0x08:0x08 + 4])[0]  # pos Y
        if self.position_y != unpacked[2]:
            logPrint("Mismatch")
        self.position_z = struct.unpack('f', ddata[0x0C:0x0C + 4])[0]  # pos Z
        if self.position_z != unpacked[3]:
            logPrint("Mismatch")

        self.velocity_x = struct.unpack('f', ddata[0x10:0x10 + 4])[0]  # velocity X
        if self.velocity_x != unpacked[4]:
            logPrint("Mismatch")
        self.velocity_y = struct.unpack('f', ddata[0x14:0x14 + 4])[0]  # velocity Y
        if self.velocity_y != unpacked[5]:
            logPrint("Mismatch")
        self.velocity_z = struct.unpack('f', ddata[0x18:0x18 + 4])[0]  # velocity Z
        if self.velocity_z != unpacked[6]:
            logPrint("Mismatch")

        self.rotation_pitch = struct.unpack('f', ddata[0x1C:0x1C + 4])[0]  # rot Pitch
        if self.rotation_pitch != unpacked[7]:
            logPrint("Mismatch")
        self.rotation_yaw = struct.unpack('f', ddata[0x20:0x20 + 4])[0]  # rot Yaw
        if self.rotation_yaw != unpacked[8]:
            logPrint("Mismatch")
        self.rotation_roll = struct.unpack('f', ddata[0x24:0x24 + 4])[0]  # rot Roll
        if self.rotation_roll != unpacked[9]:
            logPrint("Mismatch")

        self.unknown[0x28] = struct.unpack('f', ddata[0x28:0x28+4])[0]					# rot ??? (TODO RelativeOrientationToNorth????)
        if self.unknown[0x28] != unpacked[10]:
            logPrint("Mismatch")

        self.angular_velocity_x = struct.unpack('f', ddata[0x2C:0x2C + 4])[0]  # angular velocity X
        if self.angular_velocity_x != unpacked[11]:
            logPrint("Mismatch")
        self.angular_velocity_y = struct.unpack('f', ddata[0x30:0x30 + 4])[0]  # angular velocity Y
        if self.angular_velocity_y != unpacked[12]:
            logPrint("Mismatch")
        self.angular_velocity_z = struct.unpack('f', ddata[0x34:0x34 + 4])[0]  # angular velocity Z
        if self.angular_velocity_z != unpacked[13]:
            logPrint("Mismatch")
        
        self.ride_height = 1000 * struct.unpack('f', ddata[0x38:0x38 + 4])[0]  # ride height
        if self.ride_height != 1000 * unpacked[14]:
            logPrint("Mismatch")
        self.rpm = struct.unpack('f', ddata[0x3C:0x3C + 4])[0]  # rpm
        if self.rpm != unpacked[15]:
            logPrint("Mismatch")

        self.unknown[0x40] = struct.unpack('I', ddata[0x40:0x40+4])[0]		# Unknown/empty?
        if self.unknown[0x40] != unpacked[16]:
            logPrint("Mismatch")

        self.current_fuel = struct.unpack('f', ddata[0x44:0x44 + 4])[0]  # fuel
        if self.current_fuel != unpacked[17]:
            logPrint("Mismatch")
        self.fuel_capacity = struct.unpack('f', ddata[0x48:0x48 + 4])[0]
        if self.fuel_capacity != unpacked[18]:
            logPrint("Mismatch")
        self.car_speed = 3.6 * struct.unpack('f', ddata[0x4C:0x4C + 4])[0] # m/s to km/h
        if self.car_speed != 3.6 * unpacked[19]:
            logPrint("Mismatch")
        self.boost = struct.unpack('f', ddata[0x50:0x50 + 4])[0] - 1  # boost
        if self.boost != unpacked[20]-1:
            logPrint("Mismatch")
        self.oil_pressure = struct.unpack('f', ddata[0x54:0x54 + 4])[0]  # oil pressure
        if self.oil_pressure != unpacked[21]:
            logPrint("Mismatch")
        self.water_temp = struct.unpack('f', ddata[0x58:0x58 + 4])[0]  # water temp
        if self.water_temp != unpacked[22]:
            logPrint("Mismatch")
        self.oil_temp = struct.unpack('f', ddata[0x5C:0x5C + 4])[0]  # oil temp
        if self.oil_temp != unpacked[23]:
            logPrint("Mismatch")

        self.tyre_temp_FL = struct.unpack('f', ddata[0x60:0x60 + 4])[0]  # tyre temp FL
        if self.tyre_temp_FL != unpacked[24]:
            logPrint("Mismatch")
        self.tyre_temp_FR = struct.unpack('f', ddata[0x64:0x64 + 4])[0]  # tyre temp FR
        if self.tyre_temp_FR != unpacked[25]:
            logPrint("Mismatch")
        self.tyre_temp_RL = struct.unpack('f', ddata[0x68:0x68 + 4])[0]  # tyre temp RL
        if self.tyre_temp_RL != unpacked[26]:
            logPrint("Mismatch")
        self.tyre_temp_RR = struct.unpack('f', ddata[0x6C:0x6C + 4])[0]  # tyre temp RR
        if self.tyre_temp_RR != unpacked[27]:
            logPrint("Mismatch")

        self.package_id = struct.unpack('i', ddata[0x70:0x70 + 4])[0]
        if self.package_id != unpacked[28]:
            logPrint("Mismatch")
        self.current_lap = struct.unpack('h', ddata[0x74:0x74 + 2])[0]
        if self.current_lap != unpacked[29]:
            logPrint("Mismatch")
        self.total_laps = struct.unpack('h', ddata[0x76:0x76 + 2])[0]  # total laps
        if self.total_laps != unpacked[30]:
            logPrint("Mismatch")
        self.best_lap = struct.unpack('i', ddata[0x78:0x78 + 4])[0]
        if self.best_lap != unpacked[31]:
            logPrint("Mismatch")
        self.last_lap = struct.unpack('i', ddata[0x7C:0x7C + 4])[0]
        if self.last_lap != unpacked[32]:
            logPrint("Mismatch")

        self.raw_time_on_track = struct.unpack('i', ddata[0x80:0x80 + 4])[0]
        if self.raw_time_on_track != unpacked[33]:
            logPrint("Mismatch")
        self.time_on_track = td(seconds=round(struct.unpack('i', ddata[0x80:0x80 + 4])[0] / 1000))  # time of day on track
        if self.time_on_track != td(seconds=round(unpacked[33]/1000)):
            logPrint("Mismatch")

        self.current_position = struct.unpack('h', ddata[0x84:0x84 + 2])[0]  # current position (TODO PreRaceStartPositionOrQualiPos????)
        if self.current_position != unpacked[34]:
            logPrint("Mismatch")
        self.total_positions = struct.unpack('h', ddata[0x86:0x86 + 2])[0]  # total positions
        if self.total_positions != unpacked[35]:
            logPrint("Mismatch")

        self.rpm_rev_warning = struct.unpack('H', ddata[0x88:0x88 + 2])[0]  # rpm rev warning
        if self.rpm_rev_warning != unpacked[36]:
            logPrint("Mismatch")
        self.rpm_rev_limiter = struct.unpack('H', ddata[0x8A:0x8A + 2])[0]  # rpm rev limiter
        if self.rpm_rev_limiter != unpacked[37]:
            logPrint("Mismatch")

        self.estimated_top_speed = struct.unpack('h', ddata[0x8C:0x8C + 2])[0]  # estimated top speed
        if self.estimated_top_speed != unpacked[38]:
            logPrint("Mismatch")

        self.in_race = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b1 == 0b1 # "car on track"
        if self.in_race != (unpacked[39] & 0b1 == 0b1):
            logPrint("Mismatch")
        self.is_paused = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b10 == 0b10
        if self.is_paused != (unpacked[39] & 0b10 == 0b10):
            logPrint("Mismatch")

        self.loading_or_processing = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b100 == 0b100
        if self.loading_or_processing != (unpacked[39] & 0b100 == 0b100):
            logPrint("Mismatch")

        self.in_gear = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b1000 == 0b1000
        if self.in_gear != (unpacked[39] & 0b1000 == 0b1000):
            logPrint("Mismatch")
        self.has_turbo = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b10000 == 0b10000
        if self.has_turbo != (unpacked[39] & 0b10000 == 0b10000):
            logPrint("Mismatch")
        self.rev_limiter_blink_alert_active = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b100000 == 0b100000
        if self.rev_limiter_blink_alert_active != (unpacked[39] & 0b100000 == 0b100000):
            logPrint("Mismatch")
        self.hand_brake_active = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b1000000 == 0b1000000
        if self.hand_brake_active != (unpacked[39] & 0b1000000 == 0b1000000):
            logPrint("Mismatch")
        self.lights_active = struct.unpack('B', ddata[0x8E:0x8E + 1])[0] & 0b10000000 == 0b10000000
        if self.lights_active != (unpacked[39] & 0b10000000 == 0b10000000):
            logPrint("Mismatch")
        self.high_beam_active = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b1 == 0b1
        if self.high_beam_active != (unpacked[40] & 0b1 == 0b1):
            logPrint("Mismatch")
        self.low_beam_active = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b10 == 0b10
        if self.low_beam_active != (unpacked[40] & 0b10 == 0b10):
            logPrint("Mismatch")
        self.asm_active = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b100 == 0b100
        if self.asm_active != (unpacked[40] & 0b100 == 0b100):
            logPrint("Mismatch")
        self.tcs_active = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b1000 == 0b1000
        if self.tcs_active != (unpacked[40] & 0b1000 == 0b1000):
            logPrint("Mismatch")
        self.reserved_flag_13 = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b10000 == 0b10000
        if self.reserved_flag_13 != (unpacked[40] & 0b10000 == 0b10000):
            logPrint("Mismatch")
        self.reserved_flag_14 = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b100000 == 0b100000
        if self.reserved_flag_14 != (unpacked[40] & 0b100000 == 0b100000):
            logPrint("Mismatch")
        self.reserved_flag_15 = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b1000000 == 0b1000000
        if self.reserved_flag_15 != (unpacked[40] & 0b1000000 == 0b1000000):
            logPrint("Mismatch")
        self.reserved_flag_16 = struct.unpack('B', ddata[0x8F:0x8F + 1])[0] & 0b10000000 == 0b10000000
        if self.reserved_flag_16 != (unpacked[40] & 0b10000000 == 0b10000000):
            logPrint("Mismatch")

        self.current_gear = struct.unpack('B', ddata[0x90:0x90 + 1])[0] & 0b00001111
        if self.current_gear != unpacked[41] & 0b00001111:
            logPrint("Mismatch")
        self.suggested_gear = struct.unpack('B', ddata[0x90:0x90 + 1])[0] >> 4
        if self.suggested_gear != unpacked[41] >> 4:
            logPrint("Mismatch")

        self.throttle = struct.unpack('B', ddata[0x91:0x91 + 1])[0] / 2.55  # throttle
        if self.throttle != unpacked[42] / 2.55:
            logPrint("Mismatch")

        self.brake = struct.unpack('B', ddata[0x92:0x92 + 1])[0] / 2.55  # brake
        if self.brake != unpacked[43] / 2.55:
            logPrint("Mismatch")

        self.unknown[0x93] = bin(struct.unpack('B', ddata[0x93:0x93+1])[0])[2:]	# 0x93 = ???, always 0?
        if self.unknown[0x93] != bin(unpacked[44])[2:]:
            logPrint("Mismatch")

        self.normal_x = struct.unpack('f', ddata[0x94:0x94+4])[0]			# 0x94 = CAR NORMAL X
        if self.normal_x != unpacked[45]:
            logPrint("Mismatch")
        self.normal_y = struct.unpack('f', ddata[0x98:0x98+4])[0]			# 0x98 = CAR NORMAL Y
        if self.normal_y != unpacked[46]:
            logPrint("Mismatch")
        self.normal_z = struct.unpack('f', ddata[0x9C:0x9C+4])[0]			# 0x9C = CAR NORMAL Z
        if self.normal_z != unpacked[47]:
            logPrint("Mismatch")

        self.unknown[0xA0] =  struct.unpack('f', ddata[0xA0:0xA0+4])[0]			# 0xA0 = ??? (TODO RoadPlaneDistance???)
        if self.unknown[0xA0] != unpacked[48]:
            logPrint("Mismatch")

        self.tyre_diameter_FL = struct.unpack('f', ddata[0xB4:0xB4 + 4])[0]
        if self.tyre_diameter_FL != unpacked[53]:
            logPrint("Mismatch")
        self.tyre_diameter_FR = struct.unpack('f', ddata[0xB8:0xB8 + 4])[0]
        if self.tyre_diameter_FR != unpacked[54]:
            logPrint("Mismatch")
        self.tyre_diameter_RL = struct.unpack('f', ddata[0xBC:0xBC + 4])[0]
        if self.tyre_diameter_RL != unpacked[55]:
            logPrint("Mismatch")
        self.tyre_diameter_RR = struct.unpack('f', ddata[0xC0:0xC0 + 4])[0]
        if self.tyre_diameter_RR != unpacked[56]:
            logPrint("Mismatch")

        self.tyre_speed_FL = abs(3.6 * self.tyre_diameter_FL * struct.unpack('f', ddata[0xA4:0xA4 + 4])[0])
        if self.tyre_speed_FL != abs(3.6 * self.tyre_diameter_FL * unpacked[49]):
            logPrint("Mismatch")
        self.tyre_speed_FR = abs(3.6 * self.tyre_diameter_FR * struct.unpack('f', ddata[0xA8:0xA8 + 4])[0])
        if self.tyre_speed_FR != abs(3.6 * self.tyre_diameter_FL * unpacked[50]):
            logPrint("Mismatch")
        self.tyre_speed_RL = abs(3.6 * self.tyre_diameter_RL * struct.unpack('f', ddata[0xAC:0xAC + 4])[0])
        if self.tyre_speed_RL != abs(3.6 * self.tyre_diameter_FL * unpacked[51]):
            logPrint("Mismatch")
        self.tyre_speed_RR = abs(3.6 * self.tyre_diameter_RR * struct.unpack('f', ddata[0xB0:0xB0 + 4])[0])
        if self.tyre_speed_RR != abs(3.6 * self.tyre_diameter_FL * unpacked[52]):
            logPrint("Mismatch")

        self.suspension_FL = struct.unpack('f', ddata[0xC4:0xC4 + 4])[0]  # suspension FL
        if self.suspension_FL != unpacked[57]:
            logPrint("Mismatch")
        self.suspension_FR = struct.unpack('f', ddata[0xC8:0xC8 + 4])[0]  # suspension FR
        if self.suspension_FR != unpacked[58]:
            logPrint("Mismatch")
        self.suspension_RL = struct.unpack('f', ddata[0xCC:0xCC + 4])[0]  # suspension RL
        if self.suspension_RL != unpacked[59]:
            logPrint("Mismatch")
        self.suspension_RR = struct.unpack('f', ddata[0xD0:0xD0 + 4])[0]  # suspension RR
        if self.suspension_RR != unpacked[60]:
            logPrint("Mismatch")

        self.unknown[0xD4] = struct.unpack('f', ddata[0xD4:0xD4+4])[0]			# 0xD4 = ???, always 0?
        if self.unknown[0xD4] != unpacked[61]:
            logPrint("Mismatch")
        self.unknown[0xD8] = struct.unpack('f', ddata[0xD8:0xD8+4])[0]			# 0xD8 = ???, always 0?
        if self.unknown[0xD8] != unpacked[62]:
            logPrint("Mismatch")
        self.unknown[0xDC] = struct.unpack('f', ddata[0xDC:0xDC+4])[0]			# 0xDC = ???, always 0?
        if self.unknown[0xDC] != unpacked[63]:
            logPrint("Mismatch")
        self.unknown[0xE0] = struct.unpack('f', ddata[0xE0:0xE0+4])[0]			# 0xE0 = ???, always 0?
        if self.unknown[0xE0] != unpacked[64]:
            logPrint("Mismatch")

        self.unknown[0xE4] = struct.unpack('f', ddata[0xE4:0xE4+4])[0]			# 0xE4 = ???, always 0?
        if self.unknown[0xE4] != unpacked[65]:
            logPrint("Mismatch")
        self.unknown[0xE8] = struct.unpack('f', ddata[0xE8:0xE8+4])[0]			# 0xE8 = ???, always 0?
        if self.unknown[0xE8] != unpacked[66]:
            logPrint("Mismatch")
        self.unknown[0xEC] = struct.unpack('f', ddata[0xEC:0xEC+4])[0]			# 0xEC = ???, always 0?
        if self.unknown[0xEC] != unpacked[67]:
            logPrint("Mismatch")
        self.unknown[0xF0] = struct.unpack('f', ddata[0xF0:0xF0+4])[0]			# 0xF0 = ???, always 0?
        if self.unknown[0xF0] != unpacked[68]:
            logPrint("Mismatch")

        self.clutch = struct.unpack('f', ddata[0xF4:0xF4 + 4])[0]  # clutch
        if self.clutch != unpacked[69]:
            logPrint("Mismatch")
        self.clutch_engaged = struct.unpack('f', ddata[0xF8:0xF8 + 4])[0]  # clutch engaged
        if self.clutch_engaged != unpacked[70]:
            logPrint("Mismatch")
        self.rpm_after_clutch = struct.unpack('f', ddata[0xFC:0xFC + 4])[0]  # rpm after clutch
        if self.rpm_after_clutch != unpacked[71]:
            logPrint("Mismatch")

        self.unknown[0x100] = struct.unpack('f', ddata[0x100:0x100+4])[0]		# 0x100 = ??? (TODO TransmissionTopSpeed???)
        if self.unknown[0x100] != unpacked[72]:
            logPrint("Mismatch")

        self.gear_1 = struct.unpack('f', ddata[0x104:0x104 + 4])[0]  # 1st gear
        if self.gear_1 != unpacked[73]:
            logPrint("Mismatch")
        self.gear_2 = struct.unpack('f', ddata[0x108:0x108 + 4])[0]  # 2nd gear
        if self.gear_2 != unpacked[74]:
            logPrint("Mismatch")
        self.gear_3 = struct.unpack('f', ddata[0x10C:0x10C + 4])[0]  # 3rd gear
        if self.gear_3 != unpacked[75]:
            logPrint("Mismatch")
        self.gear_4 = struct.unpack('f', ddata[0x110:0x110 + 4])[0]  # 4th gear
        if self.gear_4 != unpacked[76]:
            logPrint("Mismatch")
        self.gear_5 = struct.unpack('f', ddata[0x114:0x114 + 4])[0]  # 5th gear
        if self.gear_5 != unpacked[77]:
            logPrint("Mismatch")
        self.gear_6 = struct.unpack('f', ddata[0x118:0x118 + 4])[0]  # 6th gear
        if self.gear_6 != unpacked[78]:
            logPrint("Mismatch")
        self.gear_7 = struct.unpack('f', ddata[0x11C:0x11C + 4])[0]  # 7th gear
        if self.gear_7 != unpacked[79]:
            logPrint("Mismatch")
        self.gear_8 = struct.unpack('f', ddata[0x120:0x120 + 4])[0]  # 8th gear
        if self.gear_8 != unpacked[80]:
            logPrint("Mismatch")

        self.car_id = struct.unpack('i', ddata[0x124:0x124 + 4])[0]  # car id
        if self.car_id != unpacked[81]:#len(unpackFormat)-1]:
            logPrint("Mismatch")

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

        bits0x8E = 0
        if self.is_paused:
            bits0x8E += 1
        if self.in_race:
            bits0x8E += 2

        if self.loading_or_processing:
            bits0x8E += 4

        if self.in_gear:
            bits0x8E += 8
        if self.has_turbo:
            bits0x8E += 16
        if self.rev_limiter_blink_alert_active:
            bits0x8E += 32
        if self.hand_brake_active:
            bits0x8E += 64
        if self.lights_active:
            bits0x8E += 128

        bits0x8F = 0
        if self.high_beam_active:
            bits0x8F += 1
        if self.low_beam_active:
            bits0x8F += 2
        if self.asm_active:
            bits0x8F += 4
        if self.tcs_active:
            bits0x8F += 8
        if self.reserved_flag_13:
            bits0x8F += 16
        if self.reserved_flag_14:
            bits0x8F += 32
        if self.reserved_flag_15:
            bits0x8F += 64
        if self.reserved_flag_16:
            bits0x8F += 128

        struct.pack_into ('B', newPkt, 0x8E, bits0x8E)
        struct.pack_into ('B', newPkt, 0x8F, bits0x8F)

        struct.pack_into('f', newPkt, 0x28, self.unknown[0x28])

        struct.pack_into('I', newPkt, 0x40, self.unknown[0x40]) 

        struct.pack_into('B', newPkt, 0x93, int(self.unknown[0x93],2))

        struct.pack_into('f', newPkt, 0x94, self.normal_x)
        struct.pack_into('f', newPkt, 0x98, self.normal_y)
        struct.pack_into('f', newPkt, 0x9C, self.normal_z)
        struct.pack_into('f', newPkt, 0xA0, self.unknown[0xA0])

        struct.pack_into('f', newPkt, 0xD4, self.unknown[0xD4])
        struct.pack_into('f', newPkt, 0xD8, self.unknown[0xD8])
        struct.pack_into('f', newPkt, 0xDC, self.unknown[0xDC])
        struct.pack_into('f', newPkt, 0xE0, self.unknown[0xE0])

        struct.pack_into('f', newPkt, 0xE4, self.unknown[0xE4])
        struct.pack_into('f', newPkt, 0xE8, self.unknown[0xE8])
        struct.pack_into('f', newPkt, 0xEC, self.unknown[0xEC])
        struct.pack_into('f', newPkt, 0xF0, self.unknown[0xF0])

        struct.pack_into('f', newPkt, 0x100, self.unknown[0x100])

        encr = salsa20_enc(newPkt, 296)
        self.raw = encr


    def interpolate(self, other, alpha):

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

        self.normal_x = alpha * other.normal_x + (1-alpha) * self.normal_x
        self.normal_y = alpha * other.normal_y + (1-alpha) * self.normal_y
        self.normal_z = alpha * other.normal_z + (1-alpha) * self.normal_z

        self.is_paused = other.is_paused or self.is_paused
        self.in_race = other.in_race and self.in_race

        self.loading_or_processing = other.loading_or_processing or self.loading_or_processing

        self.in_gear = other.in_gear or self.in_gear
        self.has_turbo = other.has_turbo or self.has_turbo
        self.rev_limiter_blink_alert_active = other.rev_limiter_blink_alert_active or self.rev_limiter_blink_alert_active
        self.hand_brake_active = other.hand_brake_active or self.hand_brake_active
        self.lights_active = other.lights_active or self.lights_active
        self.high_beam_active = other.high_beam_active or self.high_beam_active
        self.low_beam_active = other.low_beam_active or self.low_beam_active
        self.asm_active = other.asm_active or self.asm_active
        self.tcs_active = other.tcs_active or self.tcs_active
        self.reserved_flag_13 = other.reserved_flag_13 or self.reserved_flag_13
        self.reserved_flag_14 = other.reserved_flag_14 or self.reserved_flag_14
        self.reserved_flag_15 = other.reserved_flag_15 or self.reserved_flag_15
        self.reserved_flag_16 = other.reserved_flag_16 or self.reserved_flag_16

        self.unknown[0x28] = ( alpha * other.unknown[0x28] + (1-alpha) * self.unknown[0x28])

        self.unknown[0x40] = other.unknown[0x40]
        self.unknown[0x93] = other.unknown[0x93]

        self.unknown[0xA0] = ( alpha * other.unknown[0xA0] + (1-alpha) * self.unknown[0xA0])

        self.unknown[0xD4] = ( alpha * other.unknown[0xD4] + (1-alpha) * self.unknown[0xD4])
        self.unknown[0xD8] = ( alpha * other.unknown[0xD8] + (1-alpha) * self.unknown[0xD8])
        self.unknown[0xDC] = ( alpha * other.unknown[0xDC] + (1-alpha) * self.unknown[0xDC])
        self.unknown[0xE0] = ( alpha * other.unknown[0xE0] + (1-alpha) * self.unknown[0xE0])

        self.unknown[0xE4] = ( alpha * other.unknown[0xE4] + (1-alpha) * self.unknown[0xE4])
        self.unknown[0xE8] = ( alpha * other.unknown[0xE8] + (1-alpha) * self.unknown[0xE8])
        self.unknown[0xEC] = ( alpha * other.unknown[0xEC] + (1-alpha) * self.unknown[0xEC])
        self.unknown[0xF0] = ( alpha * other.unknown[0xF0] + (1-alpha) * self.unknown[0xF0])

        self.unknown[0x100] = ( alpha * other.unknown[0x100] + (1-alpha) * self.unknown[0x100])


        self.recreatePackage()

    def str(self):
        return str(self.position_x) + " " + str(self.position_y) + " " + str (self.position_z) + " " + str(self.current_lap)



