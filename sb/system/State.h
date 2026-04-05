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
    float fuelTime;
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
        //onNewTrack(false),
        //maybeOnNewTrack(false),
        presetChanged(false),
        frameDrops(0),
        cpuLoad(0),
        avgFrameTime(16.7)
    {
        lastProcessingTimes.push_back(16.7 * 1000000);
        lastProcessingTimes.push_back(16.7 * 1000000);
        lastProcessingTimes.push_back(16.7 * 1000000);
        lastProcessingTimes.push_back(16.7 * 1000000);
        lastProcessingTimes.push_back(16.7 * 1000000);
        lastProcessingTimes.push_back(16.7 * 1000000);

        lastFpsTimes.push_back(16.7 * 1000000);
        lastFpsTimes.push_back(16.7 * 1000000);
        lastFpsTimes.push_back(16.7 * 1000000);
        lastFpsTimes.push_back(16.7 * 1000000);
        lastFpsTimes.push_back(16.7 * 1000000);
        lastFpsTimes.push_back(16.7 * 1000000);
    }

    void addMessage(QString channel, QString message)
    {
        m_messageQueue[channel].push_back(message);
    }

    QList<QString> messages(QString channel)
    {
        if (m_messageQueue.contains(channel))
        {
            return m_messageQueue[channel];
        }
        return QList<QString> ();
    }

    void saveComparisonLap(QString key, QString fnKey, bool absolutePath = false);
    void loadComparisonLap(QString key, QString fnKey, bool absolutePath = false);

    PLap currentLap;
    float lapProgress;

    QList<PLap> previousLaps;
    QMap<QString, PComparisonLap> comparisonLaps;

    PTrack assumedTrack;
    PTrack identifiedTrack;

    FuelData fuelData;

    QList<unsigned> lastProcessingTimes;
    QList<unsigned> lastFpsTimes;
    unsigned frameDrops;

    float cpuLoad;
    float avgFrameTime;

protected:
    void clearMessages()
    {
        m_messageQueue.clear();
    }

    bool newLap;
    bool newLapIsClosedLoop; // TODO: redundant with Lap::m_valid?
    bool newSession;
    bool inPit;
    //bool onNewTrack;
    //bool maybeOnNewTrack;
    QString currentPreset;
    bool presetChanged;
    QMap<QString, QList<QString>> m_messageQueue;
};

typedef QSharedPointer<State> PState;
