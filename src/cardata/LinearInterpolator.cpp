#include "LinearInterpolator.h"
#include "src/cardata/TelemetryPointGT7.h"

QList<PTelemetryPoint> LinearInterpolator::interpolate (PTelemetryPoint p1, PTelemetryPoint p2)
{
    QList<PTelemetryPoint> result;

    if (p1->sequenceNumber() > p2->sequenceNumber())
    {
        assert(0);
        p1.swap(p2);
    }

    int n = abs(int(p2->sequenceNumber()) - int(p1->sequenceNumber()));

    for (int i = 1; i < n; ++i)
    {
        PTelemetryPoint newPoint = p1->copy();

        float alpha = 1.0 - float (i) / float (n);
        newPoint->setSequenceNumber(p1->sequenceNumber() + i);

        newPoint->setPosition(alpha * p1->position() + (1.0f - alpha) * p2->position());
        newPoint->setVelocity(alpha * p1->velocity() + (1.0f - alpha) * p2->velocity());

        newPoint->setRotation(alpha * p1->rotation() + (1.0-alpha) * p2->rotation());
        newPoint->setAngularVelocity(alpha * p1->angularVelocity() + (1.0-alpha) * p2->angularVelocity());

        newPoint->setRpm(alpha * p1->rpm() + (1.0-alpha) * p2->rpm());
        newPoint->setCarSpeed(alpha * p1->carSpeed() + (1.0-alpha) * p2->carSpeed());
        newPoint->setCurrentFuel(alpha * p1->currentFuel() + (1.0-alpha) * p2->currentFuel());
        newPoint->setBoost(alpha * p1->boost() + (1.0-alpha) * p2->boost());
        newPoint->setOilPressure(alpha * p1->oilPressure() + (1.0-alpha) * p2->oilPressure());
        newPoint->setWaterTemperature(alpha * p1->waterTemperature() + (1.0-alpha) * p2->waterTemperature());
        newPoint->setOilTemperature(alpha * p1->oilTemperature() + (1.0-alpha) * p2->oilTemperature());

        newPoint->setCurrentGear(p1->currentGear());
        newPoint->setSuggestedGear(p1->suggestedGear());
        newPoint->setThrottle(alpha * p1->throttle() + (1.0-alpha) * p2->throttle());
        newPoint->setBrake(alpha * p1->brake() + (1.0-alpha) * p2->brake());

        newPoint->setClutch(alpha * p1->clutch() + (1.0-alpha) * p2->clutch());
        newPoint->setClutchEngaged(alpha * p1->clutchEngaged() + (1.0-alpha) * p2->clutchEngaged());
        newPoint->setRpmAfterClutch(alpha * p1->rpmAfterClutch() + (1.0-alpha) * p2->rpmAfterClutch());

        newPoint->setTyreTemperature(alpha * p1->tyreTemperature() + (1.0-alpha) * p2->tyreTemperature());

        newPoint->setWheelRps(alpha * p1->wheelRps() + (1.0-alpha) * p2->wheelRps());

        newPoint->setSuspension(alpha * p1->suspension() + (1.0-alpha) * p2->suspension());

        newPoint->setTyreDiameter(alpha * p1->tyreDiameter() + (1.0-alpha) * p2->tyreDiameter());
        newPoint->setRideHeight(alpha * p1->rideHeight() + (1.0-alpha) * p2->rideHeight());
        newPoint->setFuelCapacity(alpha * p1->fuelCapacity() + (1.0-alpha) * p2->fuelCapacity());
        newPoint->setRpmRevWarning(alpha * p1->rpmRevWarning() + (1.0-alpha) * p2->rpmRevWarning());
        newPoint->setRpmRevLimiter(alpha * p1->rpmRevLimiter() + (1.0-alpha) * p2->rpmRevLimiter());
        newPoint->setEstimatedTopSpeed(alpha * p1->estimatedTopSpeed() + (1.0-alpha) * p2->estimatedTopSpeed());

        newPoint->setGear(1, alpha * p1->gear(1) + (1.0-alpha) * p2->gear(1));
        newPoint->setGear(1, alpha * p1->gear(2) + (1.0-alpha) * p2->gear(2));
        newPoint->setGear(1, alpha * p1->gear(3) + (1.0-alpha) * p2->gear(3));
        newPoint->setGear(1, alpha * p1->gear(4) + (1.0-alpha) * p2->gear(4));
        newPoint->setGear(1, alpha * p1->gear(5) + (1.0-alpha) * p2->gear(5));
        newPoint->setGear(1, alpha * p1->gear(6) + (1.0-alpha) * p2->gear(6));
        newPoint->setGear(1, alpha * p1->gear(7) + (1.0-alpha) * p2->gear(7));
        newPoint->setGear(1, alpha * p1->gear(8) + (1.0-alpha) * p2->gear(8));

        newPoint->setCurrentLap(p1->currentLap());
        newPoint->setTotalLaps(p1->totalLaps());
        newPoint->setBestLapMs(p1->bestLapMs());
        newPoint->setLastLapMs(p1->lastLapMs());

        newPoint->setTimeOnTrack(alpha * p1->timeOnTrack() + (1.0-alpha) * p2->timeOnTrack());

        newPoint->setCurrentPosition(p1->currentPosition());
        newPoint->setTotalPositions(p1->totalPositions());

        newPoint->setInRace(p1->inRace());
        newPoint->setIsPaused(p1->isPaused());
        newPoint->setLoadingOrProcessing(p1->loadingOrProcessing());
        newPoint->setInGear(p1->inGear());
        newPoint->setHasTurbo(p1->hasTurbo());
        newPoint->setRevLimiterBlinkAlertActive(p1->revLimiterBlinkAlertActive());
        newPoint->setHandBrakeActive(p1->handBrakeActive());
        newPoint->setLightsActive(p1->lightsActive());
        newPoint->setHighBeamActive(p1->highBeamActive());
        newPoint->setLowBeamActive(p1->lowBeamActive());
        newPoint->setAsmActive(p1->asmActive());
        newPoint->setTcsActive(p1->tcsActive());

        // B

        newPoint->setSteeringWheelRotation (alpha * p1->steeringWheelRotation() + (1.0-alpha) * p2->steeringWheelRotation());
        newPoint->setSteeringWheelVelocity (alpha * p1->steeringWheelVelocity() + (1.0-alpha) * p2->steeringWheelVelocity());
        newPoint->setShs(alpha * p1->shs() + (1.0-alpha) * p2->shs());

        // ~
        newPoint->setFilteredThrottle (alpha * p1->filteredThrottle() + (1.0-alpha) * p2->filteredThrottle());
        newPoint->setFilteredBrake (alpha * p1->filteredBrake() + (1.0-alpha) * p2->filteredBrake());

        newPoint->setTorque (alpha * p1->torque() + (1.0-alpha) * p2->torque());

        newPoint->setEnergyRecovery (alpha * p1->energyRecovery() + (1.0-alpha) * p2->energyRecovery());

        // C
        newPoint->setSurface (alpha * p1->surface() + (1.0-alpha) * p2->surface());
        newPoint->setCurrentLapMs (alpha * p1->currentLapMs() + (1.0-alpha) * p2->currentLapMs());
        newPoint->setSteeringAngleL (alpha * p1->steeringAngleL() + (1.0-alpha) * p2->steeringAngleL());
        newPoint->setSteeringAngleR (alpha * p1->steeringAngleR() + (1.0-alpha) * p2->steeringAngleR());
        newPoint->setWheelBase (alpha * p1->wheelBase() + (1.0-alpha) * p2->wheelBase());


        PTelemetryPointGT7 newgt7 = qSharedPointerCast<TelemetryPointGT7>(newPoint);
        PTelemetryPointGT7 gt7p1 = qSharedPointerCast<TelemetryPointGT7>(p1);
        if(!newgt7.isNull() && !gt7p1.isNull())
        {
            newgt7->setCarID(gt7p1->carID());
            newgt7->setCarCategory (gt7p1->carCategory());

            newgt7->setUnknown28(gt7p1->unknown28());
            newgt7->setUnknown40(gt7p1->unknown40());
            newgt7->setUnknown93(gt7p1->unknown93());
            newgt7->setUnknownA0(gt7p1->unknownA0());
            newgt7->setUnknownD4(gt7p1->unknownD4());
            newgt7->setUnknownD8(gt7p1->unknownD8());
            newgt7->setUnknownDC(gt7p1->unknownDC());
            newgt7->setUnknownE0(gt7p1->unknownE0());
            newgt7->setUnknownE4(gt7p1->unknownE4());
            newgt7->setUnknownE8(gt7p1->unknownE8());
            newgt7->setUnknownEC(gt7p1->unknownEC());
            newgt7->setUnknownF0(gt7p1->unknownF0());
            newgt7->setUnknown100(gt7p1->unknown100());
            newgt7->setUnknown144(gt7p1->unknown144());
            newgt7->setUnknown148(gt7p1->unknown148());
            newgt7->setUnknown154(gt7p1->unknown154());

            newgt7->reconstructData();
        }

        result.append(newPoint);
    }

    return result;
}