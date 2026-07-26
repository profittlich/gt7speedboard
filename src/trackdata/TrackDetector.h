#pragma once

#include <QSharedPointer>
#include <QMap>
#include <src/cardata/Point.h>
#include <src/trackdata/Track.h>

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
    bool isAmongCandidates(PTrack trk);
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


