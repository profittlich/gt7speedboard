#include "Track.h"
#include "sb/system/Laps.h"

Track::Track(const QString & fn)
{
    m_tolerance = 30.0;
    m_pitTolerance = m_tolerance;
    m_pitExit = 0;
    m_pitEntry = 0;
    DBG_MSG << "Load track " << fn;
    auto tfn = fn.left(fn.size() - QString(".gt7track").size()).split("!");
    PLap lap = Lap::loadLap(":/assets/assets/tracks/" + fn, false);
    m_points.assign(lap->points().begin(), lap->points().end());
    if (tfn.size() == 1)
    {
        m_name = fn.left(fn.size() - QString(".gt7track").size());
    }
    else
    {
        m_name = tfn[0];
    }

    for (size_t i = 1; i < tfn.size(); ++i)
    {
        DBG_MSG << "Param:" << tfn[0] << ":" << tfn[i];
        if (tfn[i].left(6) == "WIDTH-")
        {
            m_tolerance = (tfn[i].right(tfn[i].size() - 6)).toFloat();
            DBG_MSG << "Tolerance for" << tfn[0] << ":" << m_tolerance;
        }
        else if (tfn[i].left(4) == "PIT-")
        {
            auto pitData = (tfn[i].right(tfn[i].size() - 4)).split("-");
            m_pitEntry = pitData[0].toUInt();
            m_pitExit = pitData[1].toUInt();
            m_pitTolerance = pitData[2].toFloat();
            DBG_MSG << "Pit data for" << tfn[0] << ":" << m_pitEntry << m_pitExit << m_pitTolerance;
        }
    }

    DBG_MSG << "Loaded" << m_name;
}

bool Track::isOnTrack(PPoint p, size_t & index, size_t offset, bool verbose)
{
    float minDist = 1000000000.0;
    for (size_t j = 0; j < m_points.size(); ++j)
    {
        size_t i = (j + offset) % m_points.size();
        auto dist = p->position().distanceTo(m_points[i]->position());
        minDist = std::min(minDist, dist);
        if (((m_pitEntry > m_pitExit and (i < m_pitExit or i > m_pitEntry)) or (m_pitEntry < m_pitExit and i < m_pitExit and i > m_pitEntry)))
        {
            if (dist <= m_pitTolerance)
            {
                index = i;
                return true;
            }
        }
        else
        {
            if (dist <= m_tolerance)
            {
                index = i;
                return true;
            }
        }
    }
    if (verbose)
    {
        DBG_MSG << "Not on track" << m_name << ", dist=" << minDist << "tolerance" << m_tolerance;
    }
    return false;
}