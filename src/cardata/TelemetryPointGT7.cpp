#include <QtCore/qdebug.h>
#include <src/cardata/TelemetryPointGT7.h>

#include "src/system/Helpers.h"

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
const size_t idxUnknown28 = 0x28;

const size_t idxAngularVelocityX = 0x2C;
const size_t idxAngularVelocityY = 0x30;
const size_t idxAngularVelocityZ = 0x34;

const size_t idxRideHeight = 0x38;

const size_t idxRpm = 0x3c;

// 0x40
const size_t idxUnknown40 = 0x40;

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
const size_t idxTotalPositions = 0x86;
const size_t idxRPMRevWarning = 0x88;
const size_t idxRPMRevLimit = 0x8a;

const size_t idxEstimatedTopSpeed = 0x8c;

const size_t idxFlags = 0x8e;

const size_t idxCurrentGear = 0x90;

const size_t idxThrottle = 0x91;
const size_t idxBrake = 0x92;

const size_t idxUnknown93 = 0x93;

const size_t idxNormalX = 0x94;
const size_t idxNormalY = 0x98;
const size_t idxNormalZ = 0x9c;

const size_t idxUnknownA0 = 0xa0;

const size_t idxWheelRPSFL = 0xa4;
const size_t idxWheelRPSFR = 0xa8;
const size_t idxWheelRPSRL = 0xac;
const size_t idxWheelRPSRR = 0xb0;

const size_t idxTyreDiameterFL = 0xb4;
const size_t idxTyreDiameterFR = 0xb8;
const size_t idxTyreDiameterRL = 0xbc;
const size_t idxTyreDiameterRR = 0xc0;

const size_t idxSuspensionFL = 0xc4;
const size_t idxSuspensionFR = 0xc8;
const size_t idxSuspensionRL = 0xcc;
const size_t idxSuspensionRR = 0xd0;

const size_t idxUnknownD4 = 0xd4;
const size_t idxUnknownD8 = 0xd8;
const size_t idxUnknownDC = 0xdc;
const size_t idxUnknownE0 = 0xe0;
const size_t idxUnknownE4 = 0xe4;
const size_t idxUnknownE8 = 0xe8;
const size_t idxUnknownEC = 0xec;
const size_t idxUnknownF0 = 0xf0;

const size_t idxClutch = 0xf4;
const size_t idxClutchEngaged = 0xf8;
const size_t idxRpmAfterClutch = 0xfc;

const size_t idxUnknown100 = 0x100;

const size_t idxGear1 = 0x104;
const size_t idxGear2 = 0x108;
const size_t idxGear3 = 0x10c;
const size_t idxGear4 = 0x110;
const size_t idxGear5 = 0x114;
const size_t idxGear6 = 0x118;
const size_t idxGear7 = 0x11c;
const size_t idxGear8 = 0x120;

const size_t idxCarId = 0x124;

// B

const size_t idxSteeringWheelRotation = 0x128;
const size_t idxSteeringWheelVelocity = 0x12c;
const size_t idxShs = 0x130; // sway, heave, surge

// ~
const size_t idxFilteredThrottle = 0x13c;
const size_t idxFilteredBrake = 0x13d;

const size_t idxUnknown144 = 0x13e;
const size_t idxUnknown148 = 0x13f;

const size_t idxTorque = 0x140;

const size_t idxEnergyRecovery = 0x150;

const size_t idxUnknown160 = 0x154;

// C
const size_t idxSurface = 0x164;
const size_t idxCurrentLapMs = 0x168;
const size_t idxSteeringAngleL = 0x16c;
const size_t idxSteeringAngleR = 0x170;
const size_t idxWheelBase = 0x174;
const size_t idxCarCategory = 0x178;



TelemetryPointGT7::TelemetryPointGT7(const QByteArray & data)
{
    const size_t datagramSize = data.size();
    switch(datagramSize)
    {
    case 296:
        break;
    default:
        DBG_MSG << "Unknown datagram size: " << datagramSize;
    }

    m_data = data;

    setPosition(Vector3D<float> (
        *reinterpret_cast<const float*> (&data.data()[idxPositionX]),
        *reinterpret_cast<const float*> (&data.data()[idxPositionY]),
        *reinterpret_cast<const float*> (&data.data()[idxPositionZ])));

    setVelocity(Vector3D<float> (
        *reinterpret_cast<const float*> (&data.data()[idxVelocityX]),
        *reinterpret_cast<const float*> (&data.data()[idxVelocityY]),
        *reinterpret_cast<const float*> (&data.data()[idxVelocityZ])));

    setRotation(Vector3D<float> (
        *reinterpret_cast<const float*> (&data.data()[idxRotationPitch]),
        *reinterpret_cast<const float*> (&data.data()[idxRotationYaw]),
        *reinterpret_cast<const float*> (&data.data()[idxRotationRoll])));

    setUnknown28(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknown28]));

    setAngularVelocity(Vector3D<float> (
        *reinterpret_cast<const float*> (&data.data()[idxAngularVelocityX]),
        *reinterpret_cast<const float*> (&data.data()[idxAngularVelocityY]),
        *reinterpret_cast<const float*> (&data.data()[idxAngularVelocityZ])));

    //DBG_MSG << "AV-Z:" << (*reinterpret_cast<const float*> (&data.data()[idxAngularVelocityZ])) << angularVelocity().z();

    setRideHeight(1000.0 * *reinterpret_cast<const float*> (&data.data()[idxRideHeight]));
    setRpm(*reinterpret_cast<const float*> (&data.data()[idxRpm]));

    setUnknown40(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknown40]));

    setCurrentFuel(*reinterpret_cast<const float*> (&data.data()[idxCurrentFuel]));
    setFuelCapacity(*reinterpret_cast<const float*> (&data.data()[idxFuelCapacity]));

    setCarSpeed(3.6 * *reinterpret_cast<const float*> (&data.data()[idxCarSpeed]));

    setBoost(*reinterpret_cast<const float*> (&data.data()[idxBoost]) - 1); // TODO: really -1?
    setOilPressure(*reinterpret_cast<const float*> (&data.data()[idxOilPressure]));
    setWaterTemperature(*reinterpret_cast<const float*> (&data.data()[idxWaterTemperature]));
    setOilTemperature(*reinterpret_cast<const float*> (&data.data()[idxOilTemperature]));

    setTyreTemperature(WheelData<float>(
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureFL]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureFR]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureRL]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreTemperatureRR])));

    setSequenceNumber(*reinterpret_cast<const unsigned*> (&data.data()[idxSequenceNumber]));

    setCurrentLap(*reinterpret_cast<const int16_t*> (&data.data()[idxCurrentLap]));
    setTotalLaps(*reinterpret_cast<const int16_t*> (&data.data()[idxTotalLaps]));
    setBestLapMs(*reinterpret_cast<const int32_t*> (&data.data()[idxBestLapTime]));
    setLastLapMs(*reinterpret_cast<const int32_t*> (&data.data()[idxLastLapTime]));

    setTimeOnTrack(*reinterpret_cast<const int32_t*> (&data.data()[idxTimeOnTrack]));

    setCurrentPosition(*reinterpret_cast<const int16_t*> (&data.data()[idxCurrentPosition]));
    setTotalPositions(*reinterpret_cast<const int16_t*> (&data.data()[idxTotalPositions]));

    setRpmRevWarning(*reinterpret_cast<const uint16_t*> (&data.data()[idxRPMRevWarning]));
    setRpmRevLimiter(*reinterpret_cast<const uint16_t*> (&data.data()[idxRPMRevLimit]));

    setEstimatedTopSpeed(*reinterpret_cast<const uint16_t*> (&data.data()[idxEstimatedTopSpeed]));

    uint16_t flags = *reinterpret_cast<const uint16_t*> (&data.data()[idxFlags]);

    setInRace(flags & 0x1);
    setIsPaused(flags & 0x2);
    setLoadingOrProcessing(flags & 0x4);
    setInGear(flags & 0x8);
    setHasTurbo(flags & 0x10);
    setRevLimiterBlinkAlertActive(flags & 0x20);
    setHandBrakeActive(flags & 0x40);
    setLightsActive(flags & 0x80);
    setHighBeamActive(flags & 0x100);
    setLowBeamActive(flags & 0x200);
    setAsmActive(flags & 0x400);
    setTcsActive(flags & 0x800);

    setCurrentGear(data.data()[idxCurrentGear] & 0x0f);
    setSuggestedGear(unsigned(data.data()[idxCurrentGear]) >> 4);
    setThrottle(static_cast<unsigned char>(data.data()[idxThrottle])/2.55);
    setBrake(static_cast<unsigned char>(data.data()[idxBrake])/2.55);

    setUnknown93(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknown93]));

    setNormal(Vector3D<float> (
        *reinterpret_cast<const float*> (&data.data()[idxNormalX]),
        *reinterpret_cast<const float*> (&data.data()[idxNormalY]),
        *reinterpret_cast<const float*> (&data.data()[idxNormalZ])));

    setWheelRps(WheelData<float>(
        *reinterpret_cast<const float*> (&data.data()[idxWheelRPSFL]),
        *reinterpret_cast<const float*> (&data.data()[idxWheelRPSFR]),
        *reinterpret_cast<const float*> (&data.data()[idxWheelRPSRL]),
        *reinterpret_cast<const float*> (&data.data()[idxWheelRPSRR])));

    setTyreDiameter(WheelData<float>(
        *reinterpret_cast<const float*> (&data.data()[idxTyreDiameterFL]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreDiameterFR]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreDiameterRL]),
        *reinterpret_cast<const float*> (&data.data()[idxTyreDiameterRR])));

    setSuspension(WheelData<float>(
        *reinterpret_cast<const float*> (&data.data()[idxSuspensionFL]),
        *reinterpret_cast<const float*> (&data.data()[idxSuspensionFR]),
        *reinterpret_cast<const float*> (&data.data()[idxSuspensionRL]),
        *reinterpret_cast<const float*> (&data.data()[idxSuspensionRR])));

    setUnknownA0(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownA0]));
    setUnknownD4(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownD4]));
    setUnknownD8(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownD8]));
    setUnknownDC(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownDC]));
    setUnknownE0(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownE0]));
    setUnknownE4(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownE4]));
    setUnknownE8(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownE8]));
    setUnknownEC(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownEC]));
    setUnknownF0(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknownF0]));

    setClutch(*reinterpret_cast<const float*> (&data.data()[idxClutch]));
    setClutchEngaged(*reinterpret_cast<const float*> (&data.data()[idxClutchEngaged]));
    setRpmAfterClutch(*reinterpret_cast<const float*> (&data.data()[idxRpmAfterClutch]));

    setUnknown100(*reinterpret_cast<const uint32_t*> (&data.data()[idxUnknown100]));

    setGear(1, *reinterpret_cast<const float*> (&data.data()[idxGear1]));
    setGear(2, *reinterpret_cast<const float*> (&data.data()[idxGear2]));
    setGear(3, *reinterpret_cast<const float*> (&data.data()[idxGear3]));
    setGear(4, *reinterpret_cast<const float*> (&data.data()[idxGear4]));
    setGear(5, *reinterpret_cast<const float*> (&data.data()[idxGear5]));
    setGear(6, *reinterpret_cast<const float*> (&data.data()[idxGear6]));
    setGear(7, *reinterpret_cast<const float*> (&data.data()[idxGear7]));
    setGear(8, *reinterpret_cast<const float*> (&data.data()[idxGear8]));

    setCarID(*reinterpret_cast<const int32_t*> (&data.data()[idxCarId]));

    if (datagramSize >= 296 + 20)
    {
        // B
        setSteeringWheelRotation(*reinterpret_cast<const float*> (&data.data()[idxSteeringWheelRotation]));
        setSteeringWheelVelocity(*reinterpret_cast<const float*> (&data.data()[idxSteeringWheelVelocity]));
        //setShs();
    }
    if (datagramSize >= 296 + 20 + 28)
    {
        // ~
        //setFilteredThrottle();
        //setFilteredBrake();
        //setUnknown144();
        //setUnknown148();
        //setTorque();
        //setEnergyRecovery();
        //setUnknown154();
    }
    if (datagramSize >= 296 + 20 + 28 + 20)
    {
        // C
        //setSurface();
        //setCurrentLapMs();
        //setSteeringAngleL();
        //setSteeringAngleR();
        //setWheelBase();
        //setCarCategory();
    }

}

PTelemetryPoint TelemetryPointGT7::copy()
{
    return PTelemetryPointGT7(new TelemetryPointGT7(*this));
}

QByteArray TelemetryPointGT7::getData()
{
    return m_data;
}

QByteArray TelemetryPointGT7::makeGT7Package(size_t targetSize)
{
    QByteArray result;
    result.append(reinterpret_cast<const char*>(m_data.data() + idxMagic), 4);
    assert(result.size () == idxMagic + 4);

    result.append(reinterpret_cast<const char*>(&position().x()), 4);
    assert(result.size() ==  idxPositionX + 4);
    result.append(reinterpret_cast<const char*>(&position().y()), 4);
    assert(result.size() ==  idxPositionY + 4);
    result.append(reinterpret_cast<const char*>(&position().z()), 4);
    assert(result.size() ==  idxPositionZ + 4);

    result.append(reinterpret_cast<const char*>(&velocity().x()), 4);
    assert(result.size() ==  idxVelocityX + 4);
    result.append(reinterpret_cast<const char*>(&velocity().y()), 4);
    assert(result.size() ==  idxVelocityY + 4);
    result.append(reinterpret_cast<const char*>(&velocity().z()), 4);
    assert(result.size() ==  idxVelocityZ + 4);

    result.append(reinterpret_cast<const char*>(&rotation().x()), 4);
    assert(result.size() ==  idxRotationPitch + 4);
    result.append(reinterpret_cast<const char*>(&rotation().y()), 4);
    assert(result.size() ==  idxRotationYaw + 4);
    result.append(reinterpret_cast<const char*>(&rotation().z()), 4);
    assert(result.size() ==  idxRotationRoll + 4);

    // 0x28
    result.append(reinterpret_cast<const char*>(&m_unknown28), 4);
    assert(result.size() ==  idxUnknown28 + 4);

    result.append(reinterpret_cast<const char*>(&angularVelocity().x()), 4);
    assert(result.size() ==  idxAngularVelocityX + 4);
    result.append(reinterpret_cast<const char*>(&angularVelocity().y()), 4);
    assert(result.size() ==  idxAngularVelocityY + 4);
    result.append(reinterpret_cast<const char*>(&angularVelocity().z()), 4);
    assert(result.size() ==  idxAngularVelocityZ + 4);

    float rideHeightVal = rideHeight() / 1000.0;
    result.append(reinterpret_cast<const char*>(&rideHeightVal), 4);
    assert(result.size() ==  idxRideHeight + 4);

    result.append(reinterpret_cast<const char*>(&rpm()), 4);
    assert(result.size() ==  idxRpm + 4);

    // 0x40
    result.append(reinterpret_cast<const char*>(&m_unknown40), 4);
    assert(result.size() ==  idxUnknown40 + 4);

    result.append(reinterpret_cast<const char*>(&currentFuel()), 4);
    assert(result.size() ==  idxCurrentFuel + 4);
    result.append(reinterpret_cast<const char*>(&fuelCapacity()), 4);
    assert(result.size() ==  idxFuelCapacity + 4);

    float carSpeedVal = carSpeed() / 3.6;
    result.append(reinterpret_cast<const char*>(&carSpeedVal), 4);
    assert(result.size() ==  idxCarSpeed + 4);
    float boostVal = boost() + 1;
    result.append(reinterpret_cast<const char*>(&boostVal), 4);
    assert(result.size() ==  idxBoost + 4);
    result.append(reinterpret_cast<const char*>(&oilPressure()), 4);
    assert(result.size() ==  idxOilPressure + 4);
    result.append(reinterpret_cast<const char*>(&waterTemperature()), 4);
    assert(result.size() ==  idxWaterTemperature + 4);
    result.append(reinterpret_cast<const char*>(&oilTemperature()), 4);
    assert(result.size() ==  idxOilTemperature + 4);
    result.append(reinterpret_cast<const char*>(&tyreTemperature().fl()), 4);
    assert(result.size() ==  idxTyreTemperatureFL + 4);
    result.append(reinterpret_cast<const char*>(&tyreTemperature().fr()), 4);
    assert(result.size() ==  idxTyreTemperatureFR + 4);
    result.append(reinterpret_cast<const char*>(&tyreTemperature().rl()), 4);
    assert(result.size() ==  idxTyreTemperatureRL + 4);
    result.append(reinterpret_cast<const char*>(&tyreTemperature().rr()), 4);
    assert(result.size() ==  idxTyreTemperatureRR + 4);

    result.append(reinterpret_cast<const char*>(&sequenceNumber()), 4);
    assert(result.size() ==  idxSequenceNumber + 4);
    result.append(reinterpret_cast<const char*>(&currentLap()), 2);
    assert(result.size() ==  idxCurrentLap + 2);
    result.append(reinterpret_cast<const char*>(&totalLaps()), 2);
    assert(result.size() ==  idxTotalLaps + 2);
    result.append(reinterpret_cast<const char*>(&bestLapMs()), 4);
    assert(result.size() ==  idxBestLapTime + 4);
    result.append(reinterpret_cast<const char*>(&lastLapMs()), 4);
    assert(result.size() ==  idxLastLapTime + 4);

    result.append(reinterpret_cast<const char*>(&timeOnTrack()), 4);
    assert(result.size() ==  idxTimeOnTrack + 4);
    result.append(reinterpret_cast<const char*>(&currentPosition()), 2);
    assert(result.size() ==  idxCurrentPosition + 2);
    result.append(reinterpret_cast<const char*>(&totalPositions()), 2);
    assert(result.size() ==  idxTotalPositions + 2);
    result.append(reinterpret_cast<const char*>(&rpmRevWarning()), 2);
    assert(result.size() ==  idxRPMRevWarning + 2);
    result.append(reinterpret_cast<const char*>(&rpmRevLimiter()), 2);
    assert(result.size() ==  idxRPMRevLimit + 2);

    uint16_t estTopVal = estimatedTopSpeed();
    result.append(reinterpret_cast<const char*>(&estTopVal), 2);
    assert(result.size() ==  idxEstimatedTopSpeed + 2);

    //DBG_MSG << estimatedTopSpeed();
    //DBG_MSG << *reinterpret_cast<const uint16_t*> (&result.data()[idxEstimatedTopSpeed]);


    unsigned short flags = 0;

    flags |= inRace() ? 0x1 : 0;
    flags |= isPaused() ? 0x2 : 0;
    flags |= loadingOrProcessing() ? 0x4 : 0;
    flags |= inGear() ? 0x8 : 0;
    flags |= hasTurbo() ? 0x10 : 0;
    flags |= revLimiterBlinkAlertActive() ? 0x20 : 0;
    flags |= handBrakeActive() ? 0x40 : 0;
    flags |= lightsActive() ? 0x80 : 0;
    flags |= highBeamActive() ? 0x100 : 0;
    flags |= lowBeamActive() ? 0x200 : 0;
    flags |= asmActive() ? 0x400 : 0;
    flags |= tcsActive() ? 0x800 : 0;

    result.append(reinterpret_cast<const char*>(&flags), 2);
    assert(result.size() ==  idxFlags + 2);

    uint16_t gearval = currentGear() + (suggestedGear() << 4);
    result.append(reinterpret_cast<const char*>(&gearval), 1);
    assert(result.size() ==  idxCurrentGear + 1);

    unsigned char throttleval = round(throttle() * 255.0 / 100.0);
    result.append(reinterpret_cast<const char*>(&throttleval), 1);
    assert(result.size() ==  idxThrottle + 1);
    unsigned char brakeval = round(brake() * 255.0 / 100.0);
    result.append(reinterpret_cast<const char*>(&brakeval), 1);
    assert(result.size() ==  idxBrake + 1);

    result.append(reinterpret_cast<const char*>(&m_unknown93), 1);
    assert(result.size() ==  idxUnknown93 + 1);

    result.append(reinterpret_cast<const char*>(&normal().x()), 4);
    assert(result.size() ==  idxNormalX + 4);
    result.append(reinterpret_cast<const char*>(&normal().y()), 4);
    assert(result.size() ==  idxNormalY + 4);
    result.append(reinterpret_cast<const char*>(&normal().z()), 4);
    assert(result.size() ==  idxNormalZ + 4);

    result.append(reinterpret_cast<const char*>(&m_unknownA0), 4);
    assert(result.size() ==  idxUnknownA0 + 4);

    result.append(reinterpret_cast<const char*>(&wheelRps().fl()), 4);
    assert(result.size() ==  idxWheelRPSFL + 4);
    result.append(reinterpret_cast<const char*>(&wheelRps().fr()), 4);
    assert(result.size() ==  idxWheelRPSFR + 4);
    result.append(reinterpret_cast<const char*>(&wheelRps().rl()), 4);
    assert(result.size() ==  idxWheelRPSRL + 4);
    result.append(reinterpret_cast<const char*>(&wheelRps().rr()), 4);
    assert(result.size() ==  idxWheelRPSRR + 4);

    result.append(reinterpret_cast<const char*>(&tyreDiameter().fl()), 4);
    assert(result.size() ==  idxTyreDiameterFL + 4);
    result.append(reinterpret_cast<const char*>(&tyreDiameter().fr()), 4);
    assert(result.size() ==  idxTyreDiameterFR + 4);
    result.append(reinterpret_cast<const char*>(&tyreDiameter().rl()), 4);
    assert(result.size() ==  idxTyreDiameterRL + 4);
    result.append(reinterpret_cast<const char*>(&tyreDiameter().rr()), 4);
    assert(result.size() ==  idxTyreDiameterRR + 4);

    result.append(reinterpret_cast<const char*>(&suspension().fl()), 4);
    assert(result.size() ==  idxSuspensionFL + 4);
    result.append(reinterpret_cast<const char*>(&suspension().fr()), 4);
    assert(result.size() ==  idxSuspensionFR + 4);
    result.append(reinterpret_cast<const char*>(&suspension().rl()), 4);
    assert(result.size() ==  idxSuspensionRL + 4);
    result.append(reinterpret_cast<const char*>(&suspension().rr()), 4);
    assert(result.size() ==  idxSuspensionRR + 4);

    result.append(reinterpret_cast<const char*>(&m_unknownD4), 4);
    assert(result.size() ==  idxUnknownD4 + 4);
    result.append(reinterpret_cast<const char*>(&m_unknownD8), 4);
    assert(result.size() ==  idxUnknownD8 + 4);
    result.append(reinterpret_cast<const char*>(&m_unknownDC), 4);
    assert(result.size() ==  idxUnknownDC + 4);
    result.append(reinterpret_cast<const char*>(&m_unknownE0), 4);
    assert(result.size() ==  idxUnknownE0 + 4);
    result.append(reinterpret_cast<const char*>(&m_unknownE4), 4);
    assert(result.size() ==  idxUnknownE4 + 4);
    result.append(reinterpret_cast<const char*>(&m_unknownE8), 4);
    assert(result.size() ==  idxUnknownE8 + 4);
    result.append(reinterpret_cast<const char*>(&m_unknownEC), 4);
    assert(result.size() ==  idxUnknownEC + 4);
    result.append(reinterpret_cast<const char*>(&m_unknownF0), 4);
    assert(result.size() ==  idxUnknownF0 + 4);

    result.append(reinterpret_cast<const char*>(&clutch()), 4);
    assert(result.size() ==  idxClutch + 4);
    result.append(reinterpret_cast<const char*>(&clutchEngaged()), 4);
    assert(result.size() ==  idxClutchEngaged + 4);
    result.append(reinterpret_cast<const char*>(&rpmAfterClutch()), 4);
    assert(result.size() ==  idxRpmAfterClutch + 4);

    result.append(reinterpret_cast<const char*>(&m_unknown100), 4);
    assert(result.size() ==  idxUnknown100 + 4);

    result.append(reinterpret_cast<const char*>(&gear(1)), 4);
    assert(result.size() ==  idxGear1 + 4);
    result.append(reinterpret_cast<const char*>(&gear(2)), 4);
    assert(result.size() ==  idxGear2 + 4);
    result.append(reinterpret_cast<const char*>(&gear(3)), 4);
    assert(result.size() ==  idxGear3 + 4);
    result.append(reinterpret_cast<const char*>(&gear(4)), 4);
    assert(result.size() ==  idxGear4 + 4);
    result.append(reinterpret_cast<const char*>(&gear(5)), 4);
    assert(result.size() ==  idxGear5 + 4);
    result.append(reinterpret_cast<const char*>(&gear(6)), 4);
    assert(result.size() ==  idxGear6 + 4);
    result.append(reinterpret_cast<const char*>(&gear(7)), 4);
    assert(result.size() ==  idxGear7 + 4);
    result.append(reinterpret_cast<const char*>(&gear(8)), 4);
    assert(result.size() ==  idxGear8 + 4);

    result.append(reinterpret_cast<const char*>(&carID()), 4);
    assert(result.size() ==  idxCarId + 4);

    // B
    if (targetSize >= 296 + 20)
    {
        assert(result.size() ==  idxSteeringWheelRotation + 4);
        assert(result.size() ==  idxSteeringWheelVelocity + 4);
        assert(result.size() ==  idxShs + 4);
    }

    // ~
    if (targetSize >= 296 + 20 + 28)
    {
        assert(result.size() ==  idxFilteredThrottle + 4);
        assert(result.size() ==  idxFilteredBrake + 4);

        assert(result.size() ==  idxUnknown144 + 4);
        assert(result.size() ==  idxUnknown148 + 4);

        assert(result.size() ==  idxTorque + 4);

        assert(result.size() ==  idxEnergyRecovery + 4);

        assert(result.size() ==  idxUnknown160 + 4);
    }

    // C
    if (targetSize >= 296 + 20 + 28 + 20)
    {
        assert(result.size() ==  idxSurface + 4);
        assert(result.size() ==  idxCurrentLapMs + 4);
        assert(result.size() ==  idxSteeringAngleL + 4);
        assert(result.size() ==  idxSteeringAngleR + 4);
        assert(result.size() ==  idxWheelBase + 4);
        assert(result.size() ==  idxCarCategory + 4);
    }

    /*
    bool checkOK = true;
    for (qsizetype i = 0; i < m_data.size() && i < result.size(); ++i)
    {
        if (unsigned(m_data[i]) != unsigned(result[i]))
        {
            if (i >= idxCarSpeed && i < idxCarSpeed+4)
            {

            }
            else
            {
                checkOK = false;
                DBG_MSG << i << " -> " <<  uint8_t(m_data[i]) <<  uint8_t (result[i]);
                DBG_MSG << tcsActive();
                //DBG_MSG << (carSpeed()/3.6) << (*reinterpret_cast<const float*> (&m_data.data()[idxCarSpeed])) << (*reinterpret_cast<const float*> (&result.data()[idxCarSpeed]));
                //DBG_MSG << idxFlags << " -> " <<  uint8_t(m_data[idxFlags]) <<  uint8_t (result[idxFlags]);
                //DBG_MSG << idxFlags+1 << " -> " <<  uint8_t(m_data[idxFlags+1]) <<  uint8_t (result[idxFlags+1]);
                //DBG_MSG << idxCarSpeed+2 << " -> " <<  uint8_t(m_data[idxCarSpeed+2]) <<  uint8_t (result[idxCarSpeed+2]);
                //DBG_MSG << idxCarSpeed+3 << " -> " <<  uint8_t(m_data[idxCarSpeed+3]) <<  uint8_t (result[idxCarSpeed+3]);
            }
        }


        //assert(m_data[i] == result[i]);
    }

    assert(checkOK);
    */

    return result;
}

void TelemetryPointGT7::reconstructData()
{
    m_data = makeGT7Package((m_data.size()));
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
