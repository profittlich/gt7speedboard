#pragma once

#include "sb/cardata/TelemetryPoint.h"
#include "sb/trackdata/Track.h"
#include "sb/system/Laps.h"
#include <QSharedPointer>
#include <QList>
#include <QMap>


class FuelData
{
public:
    FuelData() : fuelPerLap(-1), infiniteFuel(false) {}

    float fuelPerLap;
    bool infiniteFuel;

};

typedef QSharedPointer<FuelData> PFuelData;

class State
{
    friend class Controller;
    friend class LapChangeDetector;
    friend class SessionChangeDetector;
    friend class PresetSelector;

public:
    State () :
        currentLap(new Lap()),
        lapProgress(0),
        //currentLapValid(true),
        newLap(false),
        newLapIsClosedLoop(false),
        newSession(false),
        inPit(false),
        onNewTrack(false),
        maybeOnNewTrack(false),
        presetChanged(false)
    {}

    PLap currentLap;
    float lapProgress;
    //bool currentLapValid;

    QList<PLap> previousLaps;
    QMap<QString, PComparisonLap> comparisonLaps;

    PTrack assumedTrack;
    PTrack identifiedTrack;

    FuelData fuelData;

    unsigned lastProcessingTime;

protected:
    bool newLap;
    bool newLapIsClosedLoop; // TODO: redundant with Lap::m_valid?
    bool newSession;
    bool inPit;
    bool onNewTrack;
    bool maybeOnNewTrack;
    QString currentPreset;
    bool presetChanged;
};

typedef QSharedPointer<State> PState;
