#pragma once

#include "sb/cardata/Point.h"

#include <QList>

class Track
{
public:
    Track(const QString & fn);

    bool isOnTrack(PPoint p)
    {
        size_t temp;
        return isOnTrack (p, temp);
    }

    bool isOnTrack(PPoint p, size_t & index, size_t offset = 0, bool verbose=false);
    QString name () { return m_name; }
    size_t numPoints() { return m_points.size(); }

private:
    QString m_name;
    QList<PPoint> m_points;
    float m_tolerance;
    size_t m_pitEntry;
    size_t m_pitExit;
    float m_pitTolerance;
};

typedef QSharedPointer<Track> PTrack;
