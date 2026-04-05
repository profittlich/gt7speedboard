#include "sb/components/FuelRange.h"

#include "sb/components/ComponentFactory.h"



FuelRange::FuelRange (const QJsonValue config) : Component(config), m_showTime(new ComponentParameter<bool>("Show remaining time", false, true))
{
    addComponentParameter(m_showTime);
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("MEASURING");
}

QWidget * FuelRange::getWidget() const
{
    return m_widget;
}

QString FuelRange::defaultTitle () const
{
    return "Fuel range";
}

void FuelRange::newPoint(PTelemetryPoint p)
{
    if (state()->fuelData.infiniteFuel)
    {
        m_widget->setText (QString("INFINITE"));
    }
    else if (state()->fuelData.fuelPerLap == -1)
    {
        m_widget->setText (QString("MEASURING"));
    }
    else
    {
        float range = p->currentFuel() / state()->fuelData.fuelPerLap;
        m_widget->setText (QString::number(round(range)/100.) + " of " + QString::number(round(1.0/state()->fuelData.fuelPerLap * 100.)/100.) + " LAPS" + ((*m_showTime)() ? "\n" + sToTime(p->currentFuel() * state()->fuelData.fuelTime / 100000) + " of " + sToTime(state()->fuelData.fuelTime / 1000): "")); // full range
    }

}


QString FuelRange::description ()
{
    return "Show range in laps with current fuel";
}

QList<QString> FuelRange::actions ()
{
    QList<QString> result;

    result.append("toggle time left");

    return result;
}

QString FuelRange::componentId ()
{
    return "FuelRange";
}

void FuelRange::callAction(QString a)
{
    if (a == "toggle time left")
    {
        (*m_showTime)() = !(*m_showTime)();
    }
}

static ComponentFactory::RegisterComponent<FuelRange> reg;
