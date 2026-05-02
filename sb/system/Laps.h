#pragma once

#include <QList>

#include "sb/cardata/Point.h"
#include "sb/cardata/TelemetryPoint.h"
#include "sb/system/Helpers.h"
#include "sb/trackdata/TrackDetector.h"


class Lap;
typedef QSharedPointer<Lap> PLap;

class Lap
{
public:
    Lap () : m_valid(true) {}

    QPair<size_t, float> findClosestPoint(PPoint p, size_t start = 0, float cancelRange=100.0) const;

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

    //size_t findNextBrake () const { return 0; }
    //size_t findNextThrottle () const { return 0; }
    //size_t findNextBrakeLift () const { return 0; }
    //size_t findNextThrottleLift () const { return 0; }
    //size_t findNextShift () const { return 0; }

    void appendTelemetryPoint(PTelemetryPoint p);
    const QList<PTelemetryPoint> & points() const { return m_points; }
    void setSucceedingPoint (PTelemetryPoint p)
    {
        DBG_MSG << "Set succeeding point" << p->lastLapMs();
        m_succeedingPoint = p;
    }
    void setPreceedingPoint (PTelemetryPoint p) { m_preceedingPoint = p; }
    const PTelemetryPoint & succeedingPoint() const { return m_succeedingPoint; }
    const PTelemetryPoint & preceedingPoint() const { return m_preceedingPoint; }

    void setTrackDetector(PTrackDetector td) { m_trackDetector = td; }
    PTrackDetector trackDetector() { return m_trackDetector; }
    QString trackName(bool withLocation = false)
    {
        if (m_trackDetector.isNull() || !m_trackDetector->trackFound())
        {
            if (withLocation)
            {
                return m_trackDetector->location();
            }
            return QString();
        }
        return m_trackDetector->detectedTrack()->name();
    }

    int lapTime() const
    {
        if (m_succeedingPoint.isNull())
        {
            DBG_MSG << "return NULL for" << points()[0]->currentLap();
            return -1;
        }
        DBG_MSG << "Return " << m_succeedingPoint->lastLapMs() << "for" << points()[0]->currentLap();
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

    PTelemetryPoint loopedPoint(int index) const
    {
        while (index < 0)
        {
            index += m_points.size();
        }
        const size_t actualIndex = index % m_points.size();
        return m_points[actualIndex];
    }

    bool saveLap(QString filename);

    static PLap loadLap(QString filename, bool detectTrack = true, size_t index = 0);
    static QList<PLap> loadLaps(QString filename, bool detectTrack = true);

private:
    PTelemetryPoint m_preceedingPoint;
    QList<PTelemetryPoint> m_points;
    PTelemetryPoint m_succeedingPoint;
    bool m_valid;
    PTrackDetector m_trackDetector;
    //QMap<int, QSet<size_t>> m_quadPoints;

};


class ComparisonLap
{
public:
    ComparisonLap () : /*lapTime(UINT_MAX),*/ hasClosestPoint(false) {}
    PLap lap;
    //unsigned lapTime;
    size_t closestPoint;
    bool hasClosestPoint;
    size_t nextBrake;
    size_t nextThrottle;
};

typedef QSharedPointer<ComparisonLap> PComparisonLap;
