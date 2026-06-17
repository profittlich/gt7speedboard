#include "TelemetryPoint.h"

QMap<QString, size_t> TelemetryPoint::getIntKeys()
{
    QMap<QString, size_t> result;

    result.insert("sequenceNumber", 1);
    result.insert("currentGear", 2);
    result.insert("suggestedGear", 3);
    result.insert("rpmRevWarning", 4);
    result.insert("rpmRevLimiter", 5);
    result.insert("currentLap", 6);
    result.insert("totalLaps", 7);
    result.insert("bestLapMs", 8);
    result.insert("lastLapMs", 9);
    result.insert("timeOnTrack", 10);

    result.insert("currentPosition", 11);
    result.insert("totalPositions", 12);

    return result;
}

QMap<QString, size_t> TelemetryPoint::getFloatKeys()
{
    QMap<QString, size_t> result;

    result.insert("rpm", 1);
    result.insert("carSpeed", 2);
    result.insert("currentFuel", 3);
    result.insert("boost", 4);
    result.insert("oilPressure", 5);
    result.insert("waterTemperature", 6);
    result.insert("oilTemperature", 7);

    result.insert("throttle", 8);
    result.insert("brake", 9);

    result.insert("clutch", 10);
    result.insert("clutchEngaged", 11);
    result.insert("rpmAfterClutch", 12);

    result.insert("rideHeight", 13);
    result.insert("fuelCapacity", 14);
    result.insert("estimatedTopSpeed", 15);

    result.insert("gear1", 16);
    result.insert("gear2", 17);
    result.insert("gear3", 18);
    result.insert("gear4", 19);
    result.insert("gear5", 20);
    result.insert("gear6", 21);
    result.insert("gear7", 22);
    result.insert("gear8", 23);

    return result;
}

QMap<QString, size_t> TelemetryPoint::getBoolKeys()
{
    QMap<QString, size_t> result;

    result.insert("inRace", 1);
    result.insert("isPaused", 2);
    result.insert("loadingOrProcessing", 3);
    result.insert("inGear", 4);
    result.insert("hasTurbo",5);
    result.insert("revLimiterBlinkAlertActive", 6);
    result.insert("lightsActive", 7);
    result.insert("highBeamActive", 8);
    result.insert("lowBeamActive", 9);
    result.insert("asmActive", 10);
    result.insert("tcsActive", 11);

    return result;
}

QMap<QString, size_t> TelemetryPoint::getVector3DKeys()
{
    QMap<QString, size_t> result;

    result.insert("velocity", 1);
    result.insert("position", 2);
    result.insert("normal", 3);
    result.insert("rotation", 4);
    result.insert("angularVelocity", 5);

    return result;
}

QMap<QString, size_t> TelemetryPoint::getWheelDataKeys()
{
    QMap<QString, size_t> result;

    result.insert("tyreTemperature", 1);
    result.insert("tyreSpeed", 2);
    result.insert("suspension", 3);
    result.insert("tyreDiameter", 4);

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

    else if (key == 2) return m_tyreSpeed;

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
