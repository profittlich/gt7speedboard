#pragma once

#include "sb/cardata/Point.h"

#include <QList>

class Track
{
    QString name;
    QList<Point> points;
};

typedef QSharedPointer<Track> PTrack;
