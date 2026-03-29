#include "sb/components/FuelAnalyzer.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"



FuelAnalyzer::FuelAnalyzer (const QJsonValue config) : Component(config), m_wasInPit(false)
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
    if (!m_curPoint.isNull() && p->currentFuel() > m_curPoint->currentFuel())
    {
        DBG_MSG << "refuel detected";
        m_wasInPit = true;
    }
    m_curPoint = p;
}

void FuelAnalyzer::completedLap(PLap lastLap, bool isFullLap)
{
    if (m_wasInPit)
    {
        DBG_MSG << "Ignoring lap due to refueal";
        m_wasInPit = false;
        return;
    }

    DBG_MSG << isFullLap << state()->previousLaps.back()->points().empty();
    if (!state()->previousLaps.back()->points().empty())
    {
        auto lastConsumption = fabs(state()->previousLaps.back()->points()[0]->currentFuel() - m_curPoint->currentFuel());
        state()->fuelData.infiniteFuel = lastConsumption < std::numeric_limits<float>::epsilon();
    }

    if (isFullLap && !state()->previousLaps.back()->points().empty())
    {
        m_previousLapFuel.append(state()->previousLaps.back()->points()[0]->currentFuel() - m_curPoint->currentFuel());
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
        if (m_curPoint->fuelCapacity() <= std::numeric_limits<float>::epsilon())
        {
            DBG_MSG << "No fuel capacity available, set to 100";
            fuelCapacity = 100;
        }
        state()->fuelData.fuelPerLap = avgConsumption / fuelCapacity;
        DBG_MSG << "Fuel per lap:" << state()->fuelData.fuelPerLap;
    }
    else
    {
        state()->fuelData.fuelPerLap = -1;
        DBG_MSG << "Fuel per lap:" << state()->fuelData.fuelPerLap;
    }
}

void FuelAnalyzer::pitStop()
{
    //m_wasInPit = true;
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

