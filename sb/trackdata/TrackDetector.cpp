#include "TrackDetector.h"

void TrackDetector::addPoint(PPoint p)
{
    QList<PTrack> toRemove;
    for (auto i : m_candidates)
    {
        if(!i->isOnTrack(p))
        {
            toRemove.append(i);
        }
    }

    for (auto i : toRemove)
    {
        m_candidates.removeAll(i);
    }

    if (m_candidates.size() == 0)
    {
        DBG_MSG << "reset track check";
        reset();
    }
}
