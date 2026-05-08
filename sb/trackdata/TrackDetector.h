#pragma once

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

    void reset()
    {
        m_candidates = g_globalConfiguration.allTracks();
    }

    PTrackDetector copy()
    {
        PTrackDetector result (new TrackDetector());
        result->m_candidates = m_candidates;
        return result;
    }

    void addPoint(PPoint p);

    bool trackFound() { return m_candidates.size () == 1; }
    size_t numCandidates() { return m_candidates.size(); }
    QString location()
    {
        QString firstLoc = m_candidates[0]->name().left (m_candidates[0]->name().indexOf('-')-1);
        if (numCandidates() == 1)
        {
            return firstLoc;
        }
        else if (numCandidates() <= 12) // Lago Maggiore has 12 layouts
        {
            for (size_t i = 1; i < numCandidates(); ++i)
            {
                QString curLoc = m_candidates[i]->name().left (m_candidates[i]->name().indexOf('-')-1);
                if (curLoc != firstLoc)
                {
                    return "unknown location (" + QString::number(numCandidates()) + " tracks)";
                }
            }
            return firstLoc;
        }
        return "unknown location (" + QString::number(numCandidates()) + " tracks)";
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
    QList<bool> m_possible;
};


