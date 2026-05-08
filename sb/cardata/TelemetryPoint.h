#pragma once

#include <cfloat>
#include <cstdint>
#include <sb/cardata/Point.h>
#include <sb/cardata/WheelData.h>
#include <QMap>

class TelemetryPoint : public Point
{
public:
    float angle(const TelemetryPoint & p2) const
    {
        return velocity().angle(p2.velocity());
    }

    virtual QByteArray getData() = 0;

    virtual int getInt(size_t key);
    virtual float getFloat(size_t key);
    virtual bool getBool(size_t key);
    virtual Vector3D<float> getVector3D(size_t key);
    virtual WheelData<float> getWheelData(size_t key);

    virtual QMap<QString, size_t> getIntKeys();
    virtual QMap<QString, size_t> getFloatKeys();
    virtual QMap<QString, size_t> getBoolKeys();
    virtual QMap<QString, size_t> getVector3DKeys();
    virtual QMap<QString, size_t> getWheelDataKeys();

    /* SETTERS */
    void setSequenceNumber(const unsigned & n) { m_sequenceNumber = n; }

    void setVelocity(const Vector3D<float> & v) { m_velocity = v; }
    void setRotation(const Vector3D<float> & v) { m_rotation = v; }
    void setAngularVelocity(const Vector3D<float> & v) { m_angularVelocity = v; }

    void setRpm(const float & v) { m_rpm = v; }
    void setCarSpeed(const float & v) { m_carSpeed = v; }
    void setCurrentFuel(const float & v) { m_currentFuel = v; }
    void setBoost(const float & v) { m_boost = v; }
    void setOilPressure(const float & v) { m_oilPressure = v; }
    void setWaterTemperature(const float & v) { m_waterTemperature = v; }
    void setOilTemperature(const float & v) { m_oilTemperature = v; }

    void setCurrentGear(const int32_t & v) { m_currentGear = v; }
    void setSuggestedGear(const int32_t & v) { m_suggestedGear = v; }
    void setThrottle(const float & v) { m_throttle = v; }
    void setBrake(const float & v) { m_brake = v; }

    void setClutch(const float & v) { m_clutch = v; }
    void setClutchEngaged(const float & v) { m_clutchEngaged = v; }
    void setRpmAfterClutch(const float & v) { m_rpmAfterClutch = v; }

    void setTyreTemperature(const WheelData<float> & v) { m_tyreTemperature = v; }

    void setTyreSpeed(const WheelData<float> & v) { m_tyreSpeed = v; }

    void setSuspension(const WheelData<float> & v) { m_suspension = v; }

    void setTyreDiameter(const WheelData<float> & v) { m_tyreDiameter = v; }
    void setRideHeight(const float & v) { m_rideHeight = v; }
    void setFuelCapacity(const float & v) { m_fuelCapacity = v; }
    void setRpmRevWarning(const int32_t & v) { m_rpmRevWarning = v; }
    void setRpmRevLimiter(const int32_t & v) { m_rpmRevLimiter = v; }
    void setEstimatedTopSpeed(const float & v) { m_estimatedTopSpeed = v; }

    void setGear(const unsigned index, const float & v) { m_gear[index] = v; }

    void setCurrentLap(const int32_t & v) { m_currentLap = v; }
    void setTotalLaps(const int32_t & v) { m_totalLaps = v; }
    void setBestLapMs(const int32_t & v) { m_bestLapMs = v; }
    void setLastLapMs(const int32_t & v) { m_lastLapMs = v; }

    void setTimeOnTrack(const uint32_t & v) { m_timeOnTrack = v; }

    void setCurrentPosition(const int32_t & v) { m_currentPosition = v; }
    void setTotalPositions(const int32_t & v) { m_totalPositions = v; }

    void setInRace(const bool & v) { m_inRace = v; }
    void setIsPaused(const bool & v) { m_isPaused = v; }
    void setLoadingOrProcessing(const bool & v) { m_loadingOrProcessing = v; }
    void setInGear(const bool & v) { m_inGear = v; }
    void setHasTurbo(const bool & v) { m_hasTurbo = v; }
    void setRevLimiterBlinkAlertActive(const bool & v) { m_revLimiterBlinkAlertActive = v; }
    void setLightsActive(const bool & v) { m_lightsActive = v; }
    void setHighBeamActive(const bool & v) { m_highBeamActive = v; }
    void setLowBeamActive(const bool & v) { m_lowBeamActive = v; }
    void setAsmActive(const bool & v) { m_asmActive = v; }
    void setTcsActive(const bool & v) { m_tcsActive = v; }

    /* GETTERS */
    const unsigned & sequenceNumber() const { return m_sequenceNumber; }

    const Vector3D<float> & velocity() const { return m_velocity; }
    const Vector3D<float> & rotation() const { return m_rotation; }
    const Vector3D<float> & angularVelocity() const { return m_angularVelocity; }

    const float & rpm() const { return m_rpm; }
    const float & carSpeed() const { return m_carSpeed; }
    const float & currentFuel() const { return m_currentFuel; }
    const float & boost() const { return m_boost; }
    const float & oilPressure() const { return m_oilPressure; }
    const float & waterTemperature() const { return m_waterTemperature; }
    const float & oilTemperature() const { return m_oilTemperature; }

    const int32_t & currentGear() const { return m_currentGear; }
    const int32_t & suggestedGear() const { return m_suggestedGear; }
    const float & throttle() const { return m_throttle; }
    const float & brake() const { return m_brake; }

    const float & clutch() const { return m_clutch; }
    const float & clutchEngaged() const { return m_clutchEngaged; }
    const float & rpmAfterClutch() const { return m_rpmAfterClutch; }

    const WheelData<float> & tyreTemperature() const { return m_tyreTemperature; }

    const WheelData<float> & tyreSpeed() const { return m_tyreSpeed; }

    const WheelData<float> & suspension() const { return m_suspension; }

    const WheelData<float> & tyreDiameter() const { return m_tyreDiameter; }
    const float & rideHeight() const { return m_rideHeight; }
    const float & fuelCapacity() const { return m_fuelCapacity; }
    const int32_t & rpmRevWarning() const { return m_rpmRevWarning; }
    const int32_t & rpmRevLimiter() const { return m_rpmRevLimiter; }
    const float & estimatedTopSpeed() const { return m_estimatedTopSpeed; }

    const float & gear(unsigned index) const { return m_gear[index]; }

    const int32_t & currentLap() const { return m_currentLap; }
    const int32_t & totalLaps() const { return m_totalLaps; }
    const int32_t & bestLapMs() const { return m_bestLapMs; }
    const int32_t & lastLapMs() const { return m_lastLapMs; }

    const uint32_t & timeOnTrack() const { return m_timeOnTrack; }

    const int32_t & currentPosition() const { return m_currentPosition; }
    const int32_t & totalPositions() const { return m_totalPositions; }

    const bool & inRace() const { return m_inRace; }
    const bool & isPaused() const { return m_isPaused; }
    const bool & loadingOrProcessing() const { return m_loadingOrProcessing; }
    const bool & inGear() const { return m_inGear; }
    const bool & hasTurbo() const { return m_hasTurbo; }
    const bool & revLimiterBlinkAlertActive() const { return m_revLimiterBlinkAlertActive; }
    const bool & lightsActive() const { return m_lightsActive; }
    const bool & highBeamActive() const { return m_highBeamActive; }
    const bool & lowBeamActive() const { return m_lowBeamActive; }
    const bool & asmActive() const { return m_asmActive; }
    const bool & tcsActive() const { return m_tcsActive; }

private:
    /* PROPERTIES */
    unsigned m_sequenceNumber;

    Vector3D<float> m_velocity;
    Vector3D<float> m_rotation;
    Vector3D<float> m_angularVelocity;

    float m_rpm;
    float m_carSpeed;
    float m_currentFuel;
    float m_boost;
    float m_oilPressure;
    float m_waterTemperature;
    float m_oilTemperature;

    int32_t m_currentGear;
    int32_t m_suggestedGear;
    float m_throttle;
    float m_brake;

    float m_clutch;
    float m_clutchEngaged;
    float m_rpmAfterClutch;

    WheelData<float> m_tyreTemperature;

    WheelData<float> m_tyreSpeed;

    WheelData<float> m_suspension;

    WheelData<float> m_tyreDiameter;
    float m_rideHeight;
    float m_fuelCapacity;
    int32_t m_rpmRevWarning;
    int32_t m_rpmRevLimiter;
    float m_estimatedTopSpeed;

    float m_gear[8];

    int32_t m_currentLap;
    int32_t m_totalLaps;
    int32_t m_bestLapMs;
    int32_t m_lastLapMs;

    uint32_t m_timeOnTrack;

    int32_t m_currentPosition;
    int32_t m_totalPositions;

    bool m_inRace;
    bool m_isPaused;
    bool m_loadingOrProcessing;
    bool m_inGear;
    bool m_hasTurbo;
    bool m_revLimiterBlinkAlertActive;
    bool m_lightsActive;
    bool m_highBeamActive;
    bool m_lowBeamActive;
    bool m_asmActive;
    bool m_tcsActive;

};


typedef QSharedPointer<TelemetryPoint> PTelemetryPoint;
