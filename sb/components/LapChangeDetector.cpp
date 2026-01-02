#include "sb/components/LapChangeDetector.h"

#include "sb/components/ComponentFactory.h"



LapChangeDetector::LapChangeDetector (const QJsonValue config) : Component(config), m_currentLap(-1)
{
    m_validLapEndpointDistance = 20;
}

QWidget * LapChangeDetector::getWidget() const
{
    return nullptr;
}

QString LapChangeDetector::defaultTitle () const
{
    return "Lap Change Detector";
}

void LapChangeDetector::newPoint(PTelemetryPoint p)
{
    if (m_currentLap != p->currentLap())
    {
        DBG_MSG << "=============";
        DBG_MSG << ("Lap change detected");
        m_currentLap = p->currentLap();
        state()->newLap = true;
        if (state()->currentLap->points().empty())
        {
            state()->newLapIsClosedLoop = false;
            DBG_MSG << ("New lap: Current lap empty");
        }
        else
        {
            const float endpointDistance = p->position().distanceTo(state()->currentLap->points()[0]->position());
            state()->newLapIsClosedLoop =  endpointDistance < m_validLapEndpointDistance;
            DBG_MSG << ("New lap " + QString::number(p->currentLap()).toLatin1() + ": " + QString::number(endpointDistance).toLatin1() + " m endpoint distane, " + QString::number(state()->currentLap->points().size()).toLatin1() + " points");
        }
    }
}


QString LapChangeDetector::description ()
{
    return "Detects lap changes for other components";
}

QList<QString> LapChangeDetector::actions ()
{
    return QList<QString>();
}

QString LapChangeDetector::componentId ()
{
    return "LapChangeDetector";
}


static ComponentFactory::RegisterComponent<LapChangeDetector> reg;
