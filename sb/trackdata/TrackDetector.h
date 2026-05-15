#pragma once

#include "sb/cardata/TelemetryPoint.h"
#include "sb/system/Configuration.h"
#include <QSharedPointer>

class TrackDetector;
typedef QSharedPointer<TrackDetector> PTrackDetector;

class TrackDetector
{
public:
    TrackDetector()
    {
        reset();
    }

    void reset();

    PTrackDetector copy();

    void addPoint(PPoint p);

    bool trackFound() { return m_candidates.size () == 1 && abs(m_directions[m_candidates[0]]) >= 3; }
    size_t numCandidates() { return m_candidates.size(); }
    QString location();
    bool isReversed()
    {
        return m_directions[m_candidates[0]] <= -3;
    }

    PTrack detectedTrack ()
    {
        if (!trackFound())
        {
            return PTrack();
        }

        return m_candidates[0];
    }

private:
    QList<PTrack> m_candidates;
    QMap<PTrack, int> m_indexes;
    QMap<PTrack, int> m_directions;
    QList<bool> m_possible;
    PPoint m_previousPoint;
};


