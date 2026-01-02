#include "sb/components/FuelRange.h"

#include "sb/components/ComponentFactory.h"



FuelRange::FuelRange (const QJsonValue config) : Component(config)
{
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
    if (state()->fuelData.fuelPerLap == -1)
    {
        m_widget->setText ("MEASURING");
    }
    else
    {
        float range = p->currentFuel() / state()->fuelData.fuelPerLap;
        m_widget->setText (QString::number(round(range)/100.) + " of " + QString::number(round(1.0/state()->fuelData.fuelPerLap * 100.)/100.) + " LAPS"); // full range
    }

}


QString FuelRange::description ()
{
    return "Show range in laps with current fuel";
}

QList<QString> FuelRange::actions ()
{
    return QList<QString>();
}

QString FuelRange::componentId ()
{
    return "FuelRange";
}


static ComponentFactory::RegisterComponent<FuelRange> reg;
