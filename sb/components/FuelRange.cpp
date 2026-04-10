#include "sb/components/FuelRange.h"

#include "sb/components/ComponentFactory.h"



FuelRange::FuelRange () : Component(), m_showTime(new ComponentParameter<bool>("Show remaining time", false, true))
{
    addComponentParameter(m_showTime);
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("MEASURING");

    connect(m_widget, &ColorLabel::clicked, this, [this]() { this->callAction("toggle time left");});
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
        m_widget->setText (QString::number(round(range)/100.) + " of " + QString::number(round(1.0/state()->fuelData.fuelPerLap * 100.)/100.) + " LAPS"
                          + ((*m_showTime)() ? "\n" + sToTime(p->currentFuel() * state()->fuelData.fuelTime / 100000) + " of " + sToTime(state()->fuelData.fuelTime / 1000): ""));
    }

}


QString FuelRange::description ()
{
    return "Show range in laps with current fuel";
}

QMap<QString, Action> FuelRange::actions ()
{
    QMap<QString, Action> result;

    result["toggle time left"] = { 1, "toggle time left", "toggle wether the remaining time with fuel should be displayed" };

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

static ComponentFactory::RegisterComponent<FuelRange> reg(true);
