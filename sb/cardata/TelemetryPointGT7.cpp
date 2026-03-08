#include <QtCore/qdebug.h>
#include <sb/cardata/TelemetryPointGT7.h>

const size_t idxMagic = 0x00;

const size_t idxPositionX = 0x04;
const size_t idxPositionY = 0x08;
const size_t idxPositionZ = 0x0c;

const size_t idxVelocityX = 0x10;
const size_t idxVelocityY = 0x14;
const size_t idxVelocityZ = 0x18;

const size_t idxRotationPitch = 0x1c;
const size_t idxRotationYaw = 0x20;
const size_t idxRotationRoll = 0x24;

// 0x28

const size_t idxAngularVelocityX = 0x2C;
const size_t idxAngularVelocityY = 0x30;
const size_t idxAngularVelocityZ = 0x34;

const size_t idxRideHeight = 0x38;

const size_t idxRpm = 0x3c;

// 0x40

const size_t idxCurrentFuel = 0x44;
const size_t idxFuelCapacity = 0x48;
const size_t idxCarSpeed = 0x4c;
const size_t idxBoost = 0x50;
const size_t idxOilPressure = 0x54;
const size_t idxWaterTemperature = 0x58;
const size_t idxOilTemperature = 0x5c;
const size_t idxTyreTemperatureFL = 0x60;
const size_t idxTyreTemperatureFR = 0x64;
const size_t idxTyreTemperatureRL = 0x68;
const size_t idxTyreTemperatureRR = 0x6c;

const size_t idxSequenceNumber = 0x70;
const size_t idxCurrentLap = 0x74;
const size_t idxTotalLaps = 0x76;
const size_t idxBestLapTime = 0x78;
const size_t idxLastLapTime = 0x7c;

const size_t idxTimeOnTrack = 0x80;
const size_t idxCurrentPosition = 0x84;
const size_t idxTotalPositions = 0x88;
const size_t idxRPMRevWarning = 0x8a;
const size_t idxRPMRevLimit = 0x8c;

const size_t idxEstimatedTopSpeed = 0x8d;

const size_t idxFlags = 0x8e;

const size_t idxCurrentGear = 0x90;

const size_t idxThrottle = 0x91;
const size_t idxBrake = 0x92;

const size_t idxCarId = 0x124;

TelemetryPointGT7::TelemetryPointGT7(const QByteArray & data)
{
    m_data = data;

    setSequenceNumber(*reinterpret_cast<const unsigned*> (&data.data()[idxSequenceNumber]));

    setPosition(Vector3D<float> (
        *reinterpret_cast<const float*> (&data.data()[idxPositionX]),
        *reinterpret_cast<const float*> (&data.data()[idxPositionY]),
        *reinterpret_cast<const float*> (&data.data()[idxPositionZ])));

    setCarSpeed(3.6 * *reinterpret_cast<const float*> (&data.data()[idxCarSpeed]));
    setBrake(static_cast<unsigned char>(data.data()[idxBrake])/2.55);
    setThrottle(static_cast<unsigned char>(data.data()[idxThrottle])/2.55);
    setRpm(*reinterpret_cast<const float*> (&data.data()[idxRpm]));
    setCurrentGear(data.data()[idxCurrentGear] & 0x0f);
    setCurrentLap(*reinterpret_cast<const int16_t*> (&data.data()[idxCurrentLap]));
    setTotalLaps(*reinterpret_cast<const int16_t*> (&data.data()[idxTotalLaps]));
    setLastLapMs(*reinterpret_cast<const int32_t*> (&data.data()[idxLastLapTime]));
    setTyreTemperature(WheelData<float>(
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureFL]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureFR]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureRL]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureRR])));
    setCurrentFuel(*reinterpret_cast<const float*> (&data.data()[idxCurrentFuel]));

    setCarID(*reinterpret_cast<const int32_t*> (&data.data()[idxCarId]));

    uint16_t flags = *reinterpret_cast<const uint16_t*> (&data.data()[idxFlags]);

    setInRace(flags & 0x1);
    setIsPaused(flags & 0x2);
}

QByteArray TelemetryPointGT7::getData()
{
    return m_data;
}

QMap<QString, size_t> TelemetryPointGT7::getIntKeys()
{
    QMap<QString, size_t>  result = TelemetryPoint::getIntKeys();
    result.insert("carID", 1001);
    return result;
}

int TelemetryPointGT7::getInt(size_t key)
{
    if (key == 1001) return m_carID;

    return TelemetryPoint::getInt(key);
}
