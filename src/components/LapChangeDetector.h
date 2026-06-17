#pragma once

#include "src/components/Component.h"

class LapChangeDetector : public Component
{
public:
    LapChangeDetector ();

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    int m_currentLap = -1;
    float m_validLapEndpointDistance = 20;

};
