import sys
from sb.gt7telepoint import Point
from sb.laps import loadLaps
from sb.laps import Lap


def convertGT7toCSV (fni, fno):
    sep = ";"
    laps = loadLaps(fni)
    with open (fno, "wb") as f:
        for lap in laps:
            f.write((
                    "index" + sep +
                    "car_speed" + sep + 
                    "best_lap" + sep + 
                    "last_lap" + sep + 
                    "current_lap" + sep + 
                    "current_gear" + sep + 
                    "suggested_gear" + sep + 
                    "fuel_capacity" + sep + 
                    "current_fuel" + sep + 
                    "tyre_diameter_FL" + sep + 
                    "tyre_diameter_FR" + sep + 
                    "tyre_diameter_RL" + sep + 
                    "tyre_diameter_RR" + sep + 
                    "tyre_speed_FL" + sep + 
                    "tyre_speed_FR" + sep + 
                    "tyre_speed_RL" + sep + 
                    "tyre_speed_RR" + sep + 
                    "tyre_slip_ratio_FL" + sep + 
                    "tyre_slip_ratio_FR" + sep + 
                    "tyre_slip_ratio_RL" + sep + 
                    "tyre_slip_ratio_RR" + sep + 
                    "time_on_track" + sep + 
                    "total_laps" + sep + 
                    "current_position" + sep + 
                    "total_positions" + sep + 
                    "car_id" + sep + 
                    "throttle" + sep + 
                    "rpm" + sep + 
                    "rpm_rev_warning" + sep + 
                    "brake" + sep + 
                    "boost" + sep + 
                    "rpm_rev_limiter" + sep + 
                    "estimated_top_speed" + sep + 
                    "clutch" + sep + 
                    "clutch_engaged" + sep + 
                    "rpm_after_clutch" + sep + 
                    "oil_temp" + sep + 
                    "water_temp" + sep + 
                    "oil_pressure" + sep + 
                    "ride_height" + sep + 
                    "tyre_temp_FL" + sep + 
                    "tyre_temp_FR" + sep + 
                    "tyre_temp_RL" + sep + 
                    "tyre_temp_RR" + sep + 
                    "suspension_FL" + sep + 
                    "suspension_FR" + sep + 
                    "suspension_RL" + sep + 
                    "suspension_RR" + sep + 
                    "gear_1" + sep + 
                    "gear_2" + sep + 
                    "gear_3" + sep + 
                    "gear_4" + sep + 
                    "gear_5" + sep + 
                    "gear_6" + sep + 
                    "gear_7" + sep + 
                    "gear_8" + sep + 
                    "position_x" + sep + 
                    "position_y" + sep + 
                    "position_z" + sep + 
                    "velocity_x" + sep + 
                    "velocity_y" + sep + 
                    "velocity_z" + sep + 
                    "rotation_pitch" + sep + 
                    "rotation_yaw" + sep + 
                    "rotation_roll" + sep + 
                    "angular_velocity_x" + sep + 
                    "angular_velocity_y" + sep + 
                    "angular_velocity_z" + sep + 
                    "is_paused" + sep + 
                    "in_race" + sep + 
                    "\n").encode("utf-8"))
    
            if not lap.preceeding is None:
                lap.points.insert(0, lap.preceeding)
            if not lap.following is None:
                lap.points.append(lap.following)
            i = 0
            for p in lap.points:
                f.write((
                        str(i) + sep + 
                        str(p.car_speed) + sep + 
                        str(p.best_lap) + sep + 
                        str(p.last_lap) + sep + 
                        str(p.current_lap) + sep + 
                        str(p.current_gear) + sep + 
                        str(p.suggested_gear) + sep + 
                        str(p.fuel_capacity) + sep + 
                        str(p.current_fuel) + sep + 
                        str(p.tyre_diameter_FL) + sep + 
                        str(p.tyre_diameter_FR) + sep + 
                        str(p.tyre_diameter_RL) + sep + 
                        str(p.tyre_diameter_RR) + sep + 
                        str(p.tyre_speed_FL) + sep + 
                        str(p.tyre_speed_FR) + sep + 
                        str(p.tyre_speed_RL) + sep + 
                        str(p.tyre_speed_RR) + sep + 
                        str(p.tyre_slip_ratio_FL) + sep + 
                        str(p.tyre_slip_ratio_FR) + sep + 
                        str(p.tyre_slip_ratio_RL) + sep + 
                        str(p.tyre_slip_ratio_RR) + sep + 
                        str(p.time_on_track) + sep + 
                        str(p.total_laps) + sep + 
                        str(p.current_position) + sep + 
                        str(p.total_positions) + sep + 
                        str(p.car_id) + sep + 
                        str(p.throttle) + sep + 
                        str(p.rpm) + sep + 
                        str(p.rpm_rev_warning) + sep + 
                        str(p.brake) + sep + 
                        str(p.boost) + sep + 
                        str(p.rpm_rev_limiter) + sep + 
                        str(p.estimated_top_speed) + sep + 
                        str(p.clutch) + sep + 
                        str(p.clutch_engaged) + sep + 
                        str(p.rpm_after_clutch) + sep + 
                        str(p.oil_temp) + sep + 
                        str(p.water_temp) + sep + 
                        str(p.oil_pressure) + sep + 
                        str(p.ride_height) + sep + 
                        str(p.tyre_temp_FL) + sep + 
                        str(p.tyre_temp_FR) + sep + 
                        str(p.tyre_temp_RL) + sep + 
                        str(p.tyre_temp_RR) + sep + 
                        str(p.suspension_FL) + sep + 
                        str(p.suspension_FR) + sep + 
                        str(p.suspension_RL) + sep + 
                        str(p.suspension_RR) + sep + 
                        str(p.gear_1) + sep + 
                        str(p.gear_2) + sep + 
                        str(p.gear_3) + sep + 
                        str(p.gear_4) + sep + 
                        str(p.gear_5) + sep + 
                        str(p.gear_6) + sep + 
                        str(p.gear_7) + sep + 
                        str(p.gear_8) + sep + 
                        str(p.position_x) + sep + 
                        str(p.position_y) + sep + 
                        str(p.position_z) + sep + 
                        str(p.velocity_x) + sep + 
                        str(p.velocity_y) + sep + 
                        str(p.velocity_z) + sep + 
                        str(p.rotation_pitch) + sep + 
                        str(p.rotation_yaw) + sep + 
                        str(p.rotation_roll) + sep + 
                        str(p.angular_velocity_x) + sep + 
                        str(p.angular_velocity_y) + sep + 
                        str(p.angular_velocity_z) + sep + 
                        str(p.is_paused) + sep + 
                        str(p.in_race) + sep + 
                        "\n").encode("utf-8"))
                i+=1
    
#    with open (fno, "rb") as fo:




if __name__ == '__main__':
    if len(sys.argv) == 3:
        convertGT7toCSV(sys.argv[1], sys.argv[2])
    else:
        print("usage: " + sys.argv[0] + " <infile> <outfile>")

