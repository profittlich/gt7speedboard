#pragma once

#include "src/cardata/Point.h"

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

    bool isOnTrack(PPoint p, size_t & index, size_t offset = 0, bool verbose=false, float *dist = nullptr);
    const QString name () const { return m_name; }
    size_t numPoints() { return m_points.size(); }

private:
    QString m_name;
    QList<PPoint> m_points;
    float m_tolerance = 0;
    size_t m_pitEntry = 0;
    size_t m_pitExit = 0;
    float m_pitTolerance = 0;
};

typedef QSharedPointer<Track> PTrack;
