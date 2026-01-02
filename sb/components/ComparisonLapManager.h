#pragma once

#include "sb/components/Component.h"

class ComparisonLapManager : public Component
{
public:
    ComparisonLapManager (const QJsonValue config);

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);
    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();

protected:
    void updateClosestPoints(PTelemetryPoint p);
    void updateNextCriticalPoints();

private:
    PComponentParameterFloat m_maxClosenessDistance;
    PTelemetryPoint m_cachedPt;
};
