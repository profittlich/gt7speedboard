#pragma once

#include "sb/components/Component.h"

class SessionChangeDetector : public Component
{
public:
    SessionChangeDetector (const QJsonValue config);

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();

private:
    int m_currentLap;

};
