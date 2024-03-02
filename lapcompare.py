
from openpyxl import Workbook
import sys
from gt7telepoint import Point
from helpers import loadLap
from helpers import Lap


def compareLaps (fni1, fni2, fno):
    sep = ";"
    lap1 = loadLap(fni1)
    lap2 = loadLap(fni2)

    wb = Workbook()
    ws = wb.active

    header = [
                "index1",
                "index2",
                "delta",
                "deltadelta",
                "break count 1",
                "break count 2",
                "car_speed1", 
                "car_speed2", 
                "throttle1", 
                "throttle2", 
                "brake1", 
                "brake2", 
                "position_x1", 
                "position_x2", 
                "position_y1", 
                "position_y2", 
                "position_z1", 
                "position_z2", 
                "velocity_x1", 
                "velocity_x2", 
                "velocity_y1", 
                "velocity_y2", 
                "velocity_z1", 
                "velocity_z2", 
                "rotation_pitch1", 
                "rotation_pitch2", 
                "rotation_yaw1", 
                "rotation_yaw2", 
                "rotation_roll1", 
                "rotation_roll2", 
                "angular_velocity_x1", 
                "angular_velocity_x2", 
                "angular_velocity_y1", 
                "angular_velocity_y2", 
                "angular_velocity_z1", 
                "angular_velocity_z2", 
                "distance", 
                ]
    ws.append(header)
    i1 = 0
    i2 = 0
    p1 = lap1.points[i1]
    p2 = lap2.points[i2]
    
    p1brake = False
    p1brakeCount = 0
    p2brake = False
    p2brakeCount = 0

    dold = 0

    while i1 < len(lap1.points)-1 and i2 < len(lap2.points)-1:
        if p1.brake > 0.5 and not p1brake:
            p1brakeCount += 1
            p1brake = True
        elif p1.brake <= 0.5 and p1brake:
            p1brake = False
        if p2.brake > 0.5 and not p2brake:
            p2brakeCount += 1
            p2brake = True
        elif p2.brake <= 0.5 and p2brake:
            p2brake = False
        row = [ i1, i2, i2-i1, (i2-i1)-dold, p1brakeCount, p2brakeCount, p1.car_speed, p2.car_speed, p1.throttle, p2.throttle, p1.brake, p2.brake, p1.position_x, p2.position_x, p1.position_y, p2.position_y, p1.position_z, p2.position_z, p1.velocity_x, p2.velocity_x, p1.velocity_y, p2.velocity_y, p1.velocity_z, p2.velocity_z, p1.rotation_pitch, p2.rotation_pitch, p1.rotation_yaw, p2.rotation_yaw, p1.rotation_roll, p2.rotation_roll, p1.angular_velocity_x, p2.angular_velocity_x, p1.angular_velocity_y, p2.angular_velocity_y, p1.angular_velocity_z, p2.angular_velocity_z, lap1.distance(p1, p2)]
        ws.append(row)
        
        dold = i2-i1

        p1next = lap1.points[i1+1]
        p2next = lap2.points[i2+1]
        d1 = lap1.distance(p1next, p2)
        d2 = lap1.distance(p2next, p1)
        db = lap1.distance(p1next, p2next)
        if d1 < d2 and d1 < db:
            i1+=1
        elif d2 < d1 and d2 < db:
            i2+=1
        else:
            i1+=1
            i2+=1
        p1 = lap1.points[i1]
        p2 = lap2.points[i2]


    wb.save(fno)

if __name__ == '__main__':
    compareLaps(sys.argv[1], sys.argv[2], sys.argv[3])
