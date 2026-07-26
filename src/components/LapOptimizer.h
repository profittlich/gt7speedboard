#pragma once

#include "src/components/Component.h"

class LapOptimizer : public Component
{
public:
    LapOptimizer ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:
    void publishOptimizingLap();

private:
    PComparisonLap m_preparingOptimized;
    PLap m_optimizingLap;
    size_t m_curIndex = 0;
    size_t m_curLiveIndex = 0;
    bool m_curBrake = false;
};
