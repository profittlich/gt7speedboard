#pragma once

#include "src/components/Component.h"

class ComparisonLapManager : public Component
{
public:
    ComparisonLapManager ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    virtual void newTrack(PTrack track) override;
    //virtual void maybeNewTrack(PTrack track) override;
    virtual void leftTrack() override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:
    void updateClosestPoints(PTelemetryPoint p);
    void updateNextCriticalPoints();

private:
    PComponentParameterFloat m_maxClosenessDistance;
    PTelemetryPoint m_cachedPt;
    size_t m_medianStart = 0;
};
