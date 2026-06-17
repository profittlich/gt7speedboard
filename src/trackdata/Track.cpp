#include "Track.h"
#include "src/system/Laps.h"

Track::Track(const QString & fn)
{
    m_tolerance = 35.0;
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

    m_name = m_name.replace("_auml_", "ä");
    m_name = m_name.replace("_ouml_", "ö");
    m_name = m_name.replace("_uuml_", "ü");
    m_name = m_name.replace("_Auml_", "Ä");
    m_name = m_name.replace("_Ouml_", "Ö");
    m_name = m_name.replace("_Uuml_", "Ü");
    m_name = m_name.replace("_szlig_", "ß");

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

bool Track::isOnTrack(PPoint p, size_t & index, size_t offset, bool verbose, float *dist)
{
    float curDist=1000000000000.0;
    float tempDist;
    if (dist == nullptr)
    {
        dist = &tempDist;
    }
    *dist = 100000000000.0;
    bool enteredTrack = false;
    for (size_t j = 0; j < m_points.size(); ++j)
    {
        size_t i = (j + offset) % m_points.size();
        curDist = p->position().distanceTo(m_points[i]->position());
        if (((m_pitEntry > m_pitExit and (i < m_pitExit or i > m_pitEntry)) or (m_pitEntry < m_pitExit and i < m_pitExit and i > m_pitEntry)))
        {
            if (curDist <= m_pitTolerance)
            {
                enteredTrack = true;
                *dist = std::min(*dist, curDist);
                index = i;
                if (i == 0) // Check for lap change, maybe still at end of lap
                {
                    auto altCurDist = p->position().distanceTo(m_points.last()->position());
                    if (altCurDist < *dist)
                    {
                        index = m_points.size() - 1;
                        *dist = altCurDist;
                    }
                }
            }
            else if (enteredTrack)
            {
                break;
            }
        }
        else
        {
            if (curDist <= m_tolerance)
            {
                enteredTrack = true;
                *dist = std::min(*dist, curDist);
                index = i;
                if (i == 0)
                {
                    auto altCurDist = p->position().distanceTo(m_points.last()->position());
                    if (altCurDist < *dist)
                    {
                        index = m_points.size() - 1;
                        *dist = altCurDist;
                    }
                }
            }
            else if (enteredTrack)
            {
                break;
            }
        }
    }
    if (verbose && !enteredTrack && m_name.contains("Monza"))
    {
        DBG_MSG << "Not on track" << m_name << ", dist=" << *dist << "tolerance" << m_tolerance << "#:" << m_points.size() << "cur" << curDist;
    }
    return enteredTrack;
}