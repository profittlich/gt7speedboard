#include "TrackDetector.h"

void TrackDetector::addPoint(PPoint p)
{
    QList<PTrack> toRemove;
    for (auto i : m_candidates)
    {
        size_t curIndex;
        bool verbose=false;
        if (m_candidates.size() == 1)
        {
            verbose = true;
        }
        if(!i->isOnTrack(p, curIndex, std::max(0, m_indexes[i]), verbose))
        {

            toRemove.append(i);
        }
        else
        {
            auto gap = static_cast<int>(curIndex) - m_indexes[i];
            auto gapOverflow = static_cast<int>(curIndex) - m_indexes[i] - static_cast<int>(i->numPoints());
            auto gapUnderflow = static_cast<int>(curIndex) - m_indexes[i] + static_cast<int>(i->numPoints());
            if (m_indexes[i] != -1 &&  abs(gap) > 5 && abs (gapUnderflow) > 5 && abs (gapOverflow) > 5 && !m_previousPoint.isNull() && p->position().distanceTo(m_previousPoint->position()) < 5) // Ignore jumps
            {
                DBG_MSG << "Large gap!" << gap << curIndex << m_indexes[i] << "of" << i->numPoints() << "at" << i->name() << gapOverflow << gapUnderflow;
                toRemove.append(i);
            }
            else
            {
                //DBG_MSG << gap << curIndex << m_indexes[i] << "of" << i->numPoints() << "at" << i->name();

                if (curIndex > m_indexes[i])
                {
                    m_directions[i]++;
                }
                else if (curIndex < m_indexes[i])
                {
                    m_directions[i]--;
                }
                m_directions[i] = std::min(5, std::max(-5, m_directions[i]));
                m_indexes[i] = static_cast<int>(curIndex);
            }
        }
    }

    m_previousPoint = p;

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

QString TrackDetector::location()
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
        return firstLoc + " (" + QString::number(numCandidates()) + " layouts)";
    }
    return "unknown location (" + QString::number(numCandidates()) + " tracks)";
}

void TrackDetector::reset()
{
    m_candidates = g_globalConfiguration.allTracks();
    for (auto i : m_candidates)
    {
        m_indexes[i] = -1;
        m_directions[i] = 0;
    }
}

PTrackDetector TrackDetector::copy()
{
    PTrackDetector result (new TrackDetector());
    result->m_candidates = m_candidates;
    result->m_directions = m_directions;
    return result;
}