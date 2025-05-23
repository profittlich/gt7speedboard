from openpyxl import Workbook
import sys
from sb.gt7telepoint import Point
from sb.laps import loadLaps
from sb.laps import Lap


def convertGT7toXL (fni, fno):
    sep = ";"
    laps = loadLaps(fni)

    wb = Workbook()
    ws = wb.active

    header = [
                "index",
                "car_speed", 
                "best_lap", 
                "last_lap", 
                "current_lap", 
                "current_gear", 
                "suggested_gear", 
                "fuel_capacity", 
                "current_fuel", 
                "tyre_diameter_FL", 
                "tyre_diameter_FR", 
                "tyre_diameter_RL", 
                "tyre_diameter_RR", 
                "tyre_speed_FL", 
                "tyre_speed_FR", 
                "tyre_speed_RL", 
                "tyre_speed_RR", 
                "tyre_slip_ratio_FL", 
                "tyre_slip_ratio_FR", 
                "tyre_slip_ratio_RL", 
                "tyre_slip_ratio_RR", 
                "time_on_track", 
                "total_laps", 
                "current_position", 
                "total_positions", 
                "car_id", 
                "throttle", 
                "rpm", 
                "rpm_rev_warning", 
                "brake", 
                "boost", 
                "rpm_rev_limiter", 
                "estimated_top_speed", 
                "clutch", 
                "clutch_engaged", 
                "rpm_after_clutch", 
                "oil_temp", 
                "water_temp", 
                "oil_pressure", 
                "ride_height", 
                "tyre_temp_FL", 
                "tyre_temp_FR", 
                "tyre_temp_RL", 
                "tyre_temp_RR", 
                "suspension_FL", 
                "suspension_FR", 
                "suspension_RL", 
                "suspension_RR", 
                "gear_1", 
                "gear_2", 
                "gear_3", 
                "gear_4", 
                "gear_5", 
                "gear_6", 
                "gear_7", 
                "gear_8", 
                "position_x", 
                "position_y", 
                "position_z", 
                "velocity_x", 
                "velocity_y", 
                "velocity_z", 
                "rotation_pitch", 
                "rotation_yaw", 
                "rotation_roll", 
                "angular_velocity_x", 
                "angular_velocity_y", 
                "angular_velocity_z", 
                "is_paused", 
                "in_race", 
                "Unknowns..."
                ]
    ws.append(header)
    for lap in laps:
        if not lap.preceeding is None:
            lap.points.insert(0, lap.preceeding)
        if not lap.following is None:
            lap.points.append(lap.following)
        i = 0
        for p in lap.points:
            row = [
                        i, 
                        p.car_speed, 
                        p.best_lap, 
                        p.last_lap, 
                        p.current_lap, 
                        p.current_gear, 
                        p.suggested_gear, 
                        p.fuel_capacity, 
                        p.current_fuel, 
                        p.tyre_diameter_FL, 
                        p.tyre_diameter_FR, 
                        p.tyre_diameter_RL, 
                        p.tyre_diameter_RR, 
                        p.tyre_speed_FL, 
                        p.tyre_speed_FR, 
                        p.tyre_speed_RL, 
                        p.tyre_speed_RR, 
                        p.tyre_slip_ratio_FL, 
                        p.tyre_slip_ratio_FR, 
                        p.tyre_slip_ratio_RL, 
                        p.tyre_slip_ratio_RR, 
                        p.time_on_track, 
                        p.total_laps, 
                        p.current_position, 
                        p.total_positions, 
                        p.car_id, 
                        p.throttle, 
                        p.rpm, 
                        p.rpm_rev_warning, 
                        p.brake, 
                        p.boost, 
                        p.rpm_rev_limiter, 
                        p.estimated_top_speed, 
                        p.clutch, 
                        p.clutch_engaged, 
                        p.rpm_after_clutch, 
                        p.oil_temp, 
                        p.water_temp, 
                        p.oil_pressure, 
                        p.ride_height, 
                        p.tyre_temp_FL, 
                        p.tyre_temp_FR, 
                        p.tyre_temp_RL, 
                        p.tyre_temp_RR, 
                        p.suspension_FL, 
                        p.suspension_FR, 
                        p.suspension_RL, 
                        p.suspension_RR, 
                        p.gear_1, 
                        p.gear_2, 
                        p.gear_3, 
                        p.gear_4, 
                        p.gear_5, 
                        p.gear_6, 
                        p.gear_7, 
                        p.gear_8, 
                        p.position_x, 
                        p.position_y, 
                        p.position_z, 
                        p.velocity_x, 
                        p.velocity_y, 
                        p.velocity_z, 
                        p.rotation_pitch, 
                        p.rotation_yaw, 
                        p.rotation_roll, 
                        p.angular_velocity_x, 
                        p.angular_velocity_y, 
                        p.angular_velocity_z, 
                        p.is_paused, 
                        p.in_race, 
                        ]
            for u in p.unknown:
               row.append(u)
            ws.append(row)
            i+=1
    

    wb.save(fno)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        convertGT7toXL(sys.argv[1], sys.argv[2])
    else:
        print("usage: " + sys.argv[0] + " <infile> <outfile>")
