#pragma once

#include <QList>

#include "sb/cardata/Point.h"
#include "sb/cardata/TelemetryPoint.h"
#include "sb/system/Helpers.h"

class Lap
{
public:
    Lap () : m_valid(true) {}

    QPair<size_t, float> findClosestPoint(PPoint p, size_t start = 0) const
    {
        size_t result = 0;
        float resultDist = 1000000;
        for (size_t i = 0; i <  m_points.size(); ++i)
        {
            float newDist = p->position().distanceTo(m_points[i]->position());
            if (newDist < resultDist)
            {
                resultDist = newDist;
                result = i;
            }

        }
        return QPair<size_t, float> (result, resultDist);
    }

    float topSpeed() const
    {
        float result = 0;
        for (auto it : m_points)
        {
            if (it->carSpeed() > result)
            {
                result = it->carSpeed();
            }
        }
        return result;
    }

    size_t findNextBrake () const { return 0; }
    size_t findNextThrottle () const { return 0; }
    size_t findNextBrakeLift () const { return 0; }
    size_t findNextThrottleLift () const { return 0; }
    size_t findNextShift () const { return 0; }

    void appendTelemetryPoint(PTelemetryPoint p) { m_points.append(p); }
    const QList<PTelemetryPoint> & points() const { return m_points; }
    void setSucceedingPoint (PTelemetryPoint p) { m_succeedingPoint = p; }
    void setPreceedingPoint (PTelemetryPoint p) { m_preceedingPoint = p; }
    const PTelemetryPoint & succeedingPoint() const { return m_succeedingPoint; }
    const PTelemetryPoint & preceedingPoint() const { return m_preceedingPoint; }

    int lapTime() const
    {
        if (m_succeedingPoint.isNull())
        {
            return -1;
        }
        return m_succeedingPoint->lastLapMs();
    }

    int estimateLapTime() const
    {
        return (m_points.size()+1) * 1000.0 / c_FPS;
    }

    bool valid () const
    {
        return m_valid;
    }

    void invalidate ()
    {
        DBG_MSG << "Invalidate lap";
        m_valid = false;
    }

    static Lap loadLap(QString filename, size_t index = 0) {};
    static QList<Lap> loadLaps(QString filename) {};

private:
    PTelemetryPoint m_preceedingPoint;
    QList<PTelemetryPoint> m_points;
    PTelemetryPoint m_succeedingPoint;
    bool m_valid;

};

typedef QSharedPointer<Lap> PLap;

class ComparisonLap
{
public:
    ComparisonLap () : lapTime(UINT_MAX), hasClosestPoint(false) {}
    PLap lap;
    unsigned lapTime;
    size_t closestPoint;
    bool hasClosestPoint;
    size_t nextBrake;
    size_t nextThrottle;
};

typedef QSharedPointer<ComparisonLap> PComparisonLap;
