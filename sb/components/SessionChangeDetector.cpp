#include "sb/components/SessionChangeDetector.h"

#include "sb/components/ComponentFactory.h"



SessionChangeDetector::SessionChangeDetector (const QJsonValue config) : Component(config), m_currentLap(-1)
{
}

QWidget * SessionChangeDetector::getWidget() const
{
    return nullptr;
}

QString SessionChangeDetector::defaultTitle () const
{
    return "Session Change Detector";
}

void SessionChangeDetector::newPoint(PTelemetryPoint p)
{
    if (m_currentLap != p->currentLap() && p->currentLap() == 1)
    {
        DBG_MSG << ("Session change detected");
        state()->newSession = true;
    }
    m_currentLap = p->currentLap();
}


QString SessionChangeDetector::description ()
{
    return "Detects session changes for other components";
}

QList<QString> SessionChangeDetector::actions ()
{
    return QList<QString>();
}

QString SessionChangeDetector::componentId ()
{
    return "SessionChangeDetector";
}


static ComponentFactory::RegisterComponent<SessionChangeDetector> reg;
