#include "sb/components/FuelAnalyzer.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"



FuelAnalyzer::FuelAnalyzer (const QJsonValue config) : Component(config)
{
}

QWidget * FuelAnalyzer::getWidget() const
{
    return nullptr;
}

QString FuelAnalyzer::defaultTitle () const
{
    return "Fuel Analyzer";
}

void FuelAnalyzer::newPoint(PTelemetryPoint p)
{
    m_curPoint = p;
}

void FuelAnalyzer::completedLap(PLap lastLap, bool isFullLap)
{
    if (isFullLap && !state()->currentLap->points().empty())
    {
        m_previousLapFuel.append(state()->currentLap->points()[0]->currentFuel() - m_curPoint->currentFuel());
    }
    while (m_previousLapFuel.size() > g_globalConfiguration.fuelStatisticsLaps())
    {
        m_previousLapFuel.pop_front();
    }
    DBG_MSG << ("check fuel " + QString::number(m_previousLapFuel.size()).toLatin1() + " laps");
    if (!m_previousLapFuel.empty())
    {
        float avgConsumption = 0;
        for (size_t i = 0; i < m_previousLapFuel.size(); ++i)
        {
            avgConsumption += m_previousLapFuel[i] * 1.0/(m_previousLapFuel.size());
            DBG_MSG << ("Used fuel: " + QString::number(m_previousLapFuel[i]).toLatin1() + " " + QString::number(avgConsumption).toLatin1());
        }
        float fuelCapacity = m_curPoint->fuelCapacity();
        if (m_curPoint->fuelCapacity() == 0)
        {
            fuelCapacity = 100;
        }
        state()->fuelData.fuelPerLap = avgConsumption / fuelCapacity;
    }
    else
    {
        state()->fuelData.fuelPerLap = -1;
    }
}

QString FuelAnalyzer::description ()
{
    return "Analyze fuel consumption for other components";
}

QList<QString> FuelAnalyzer::actions ()
{
    return QList<QString>();
}

QString FuelAnalyzer::componentId ()
{
    return "FuelAnalyzer";
}


static ComponentFactory::RegisterComponent<FuelAnalyzer> reg;
