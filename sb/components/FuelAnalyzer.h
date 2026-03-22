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
    static QList<QString> actions ();
    static QString componentId ();

private:
    QList<float> m_previousLapFuel;
    PTelemetryPoint m_curPoint;
    bool m_wasInPit;

};
