#include "TelemetryPoint.h"

QMap<QString, TelemetryPoint::ValueDescriptor> TelemetryPoint::getIntKeys()
{
    QMap<QString, ValueDescriptor> result;

    result.insert("sequenceNumber", {1, "", "Sequence Number"});
    result.insert("currentGear", {2, "", "Current Gear"});
    result.insert("suggestedGear", {3, "", "Suggested Gear"});
    result.insert("rpmRevWarning", {4, "rpm", "RPM Rev Warning"});
    result.insert("rpmRevLimiter", {5, "rpm", "RPM Rev Limiter"});
    result.insert("currentLap", {6, "", "Current Lap"});
    result.insert("totalLaps", {7, "", "Total Laps"});
    result.insert("bestLapMs", {8, "ms", "Best Lap"});
    result.insert("lastLapMs", {9, "ms", "Last Lap"});
    result.insert("timeOnTrack", {10, "", "Time on Track"});

    result.insert("currentPosition", {11, "", "Current Position"});
    result.insert("totalPositions", {12, "", "Total Positions"});

    return result;
}

QMap<QString, TelemetryPoint::ValueDescriptor> TelemetryPoint::getFloatKeys()
{
    QMap<QString, ValueDescriptor> result;

    result.insert("rpm", {1, "rpm", "RPM"});
    result.insert("carSpeed", {2, "km/h", "Car Speed"});
    result.insert("currentFuel", {3, "L", "Current Fuel"});
    result.insert("boost", {4, "", "Boost"});
    result.insert("oilPressure", {5, "bar", "Oil Pressure"});
    result.insert("waterTemperature", {6, "°C", "Water Temperature"});
    result.insert("oilTemperature", {7, "°C", "Oil Temperature"});

    result.insert("throttle", {8, "", "Throttle"});
    result.insert("brake", {9, "", "Brake"});

    result.insert("clutch", {10, "", "Clutch"});
    result.insert("clutchEngaged", {11, "", "Clutch Engaged"});
    result.insert("rpmAfterClutch", {12, "rpm", "RPM After Clutch"});

    result.insert("rideHeight", {13, "m", "Ride Height"}); //TODO: m corrent?
    result.insert("fuelCapacity", {14, "L", "Fuel Capacity"});
    result.insert("estimatedTopSpeed", {15, "km/h", "Estimated Top Speed"});

    result.insert("gear1", {16, "", "Gear 1"});
    result.insert("gear2", {17, "", "Gear 2"});
    result.insert("gear3", {18, "", "Gear 3"});
    result.insert("gear4", {19, "", "Gear 4"});
    result.insert("gear5", {20, "", "Gear 5"});
    result.insert("gear6", {21, "", "Gear 6"});
    result.insert("gear7", {22, "", "Gear 7"});
    result.insert("gear8", {23, "", "Gear 8"});

    return result;
}

QMap<QString, TelemetryPoint::ValueDescriptor> TelemetryPoint::getBoolKeys()
{
    QMap<QString, ValueDescriptor> result;

    result.insert("inRace", {1, "", "In Race"});
    result.insert("isPaused", {2, "", "Is Paused"});
    result.insert("loadingOrProcessing", {3, "", "Loading or Processing"});
    result.insert("inGear", {4, "", "In Gear"});
    result.insert("hasTurbo", {5, "", "Has Turbo"});
    result.insert("revLimiterBlinkAlertActive", {6, "", "Rev Limiter Blink Alert Active"});
    result.insert("lightsActive", {7, "", "Lights Active"});
    result.insert("highBeamActive", {8, "", "High Beam Active"});
    result.insert("lowBeamActive", {9, "", "Low Beam Active"});
    result.insert("asmActive", {10, "", "ASM Active"});
    result.insert("tcsActive", {11, "", "TCS Active"});

    return result;
}

QMap<QString, TelemetryPoint::ValueDescriptor> TelemetryPoint::getVector3DKeys()
{
    QMap<QString, TelemetryPoint::ValueDescriptor> result;

    result.insert("velocity", {1, "", "Velocity"}); // TODO units
    result.insert("position", {2, "", "Position"});
    result.insert("normal", {3, "", "Normal"});
    result.insert("rotation", {4, "", "Rotation"});
    result.insert("angularVelocity", {5, "", "Angular Velocity"});

    return result;
}

QMap<QString, TelemetryPoint::ValueDescriptor> TelemetryPoint::getWheelDataKeys()
{
    QMap<QString, TelemetryPoint::ValueDescriptor> result;

    result.insert("tyreTemperature", {1, "°C", "Tyre Temperature"});
    result.insert("wheelRps", {2, "rps", "Wheel RPS"});
    result.insert("suspension", {3, "", "Suspension"}); // TODO units
    result.insert("tyreDiameter", {4, "", "Tyre Diameter"});

    return result;
}

int TelemetryPoint::getInt(size_t key)
{
    if (key == 1) return m_sequenceNumber;
    else if (key == 2) return m_currentGear;
    else if (key == 3) return m_suggestedGear;
    else if (key == 4) return m_rpmRevWarning;
    else if (key == 5) return m_rpmRevLimiter;
    else if (key == 6) return m_currentLap;
    else if (key == 7) return m_totalLaps;
    else if (key == 8) return m_bestLapMs;
    else if (key == 9) return m_lastLapMs;
    else if (key == 10) return m_timeOnTrack;

    else if (key == 11) return m_currentPosition;
    else if (key == 12) return m_totalPositions;

    return 0;
}


bool TelemetryPoint::getBool(size_t key)
{
    if (key == 1) return m_inRace;
    else if (key == 2) return m_isPaused;
    else if (key == 3) return m_loadingOrProcessing;
    else if (key == 4) return m_inGear;
    else if (key == 5) return m_hasTurbo;
    else if (key == 6) return m_revLimiterBlinkAlertActive;
    else if (key == 7) return m_lightsActive;
    else if (key == 8) return m_highBeamActive;
    else if (key == 9) return m_lowBeamActive;
    else if (key == 10) return m_asmActive;
    else if (key == 11) return m_tcsActive;
    return false;
}

Vector3D<float> TelemetryPoint::getVector3D(size_t key)
{
    if (key == 1) return m_velocity;
    else if (key == 2) return position();
    else if (key == 3) return normal();
    else if (key == 4) return m_rotation;
    else if (key == 5) return m_angularVelocity;

    return Vector3D<float>(0,0,0);
}

WheelData<float> TelemetryPoint::getWheelData(size_t key)
{
    if (key == 1) return m_tyreTemperature;

    else if (key == 2) return m_wheelRps;

    else if (key == 3) return m_suspension;

    else if (key == 4) return m_tyreDiameter;

    return WheelData<float>();
}

float TelemetryPoint::getFloat(size_t key)
{
    if (key == 1) return m_rpm;
    else if (key == 2) return m_carSpeed;
    else if (key == 3) return m_currentFuel;
    else if (key == 4) return m_boost;
    else if (key == 5) return m_oilPressure;
    else if (key == 6) return m_waterTemperature;
    else if (key == 7) return m_oilTemperature;

    else if (key == 8) return m_throttle;
    else if (key == 9) return m_brake;

    else if (key == 10) return m_clutch;
    else if (key == 11) return m_clutchEngaged;
    else if (key == 12) return m_rpmAfterClutch;

    else if (key == 13) return m_rideHeight;
    else if (key == 14) return m_fuelCapacity;
    else if (key == 15) return m_estimatedTopSpeed;

    else if (key == 16) return m_gear[0];
    else if (key == 17) return m_gear[1];
    else if (key == 18) return m_gear[2];
    else if (key == 19) return m_gear[3];
    else if (key == 20) return m_gear[4];
    else if (key == 21) return m_gear[5];
    else if (key == 22) return m_gear[6];
    else if (key == 23) return m_gear[7];

    return 0;
}
