#pragma once

#include "sb/components/Component.h"

class SessionChangeDetector : public Component
{
public:
    SessionChangeDetector ();

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    int m_currentLap;

};
