#pragma once

#include "sb/cardata/Point.h"

#include <QList>

class Track
{
public:
    Track(const QString & fn);

    bool isOnTrack(PPoint p);
    QString name () { return m_name; }

private:
    QString m_name;
    QList<PPoint> m_points;
    float m_tolerance;
    size_t m_pitEntry;
    size_t m_pitExit;
    float m_pitTolerance;
};

typedef QSharedPointer<Track> PTrack;
