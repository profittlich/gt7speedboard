#pragma once

#include "sb/components/Component.h"

class FuelAnalyzer : public Component
{
public:
    FuelAnalyzer (const QJsonValue config);

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);
    virtual void completedLap(PLap lastLap, bool isFullLap) override;
    virtual void pitStop() override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    QList<float> m_previousLapFuel;
    QList<unsigned> m_previousLapTimes;
    PTelemetryPoint m_curPoint;
    bool m_wasInPit;

};
