#include "sb/components/FuelPerLap.h"

#include "sb/components/ComponentFactory.h"



FuelPerLap::FuelPerLap (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("MEASURING");
}

QWidget * FuelPerLap::getWidget() const
{
    return m_widget;
}

QString FuelPerLap::defaultTitle () const
{
    return "Fuel per lap";
}

void FuelPerLap::newPoint(PTelemetryPoint p)
{
    if (state()->fuelData.infiniteFuel)
    {
        m_widget->setText ("0% PER LAP");
    }
    else if (state()->fuelData.fuelPerLap == -1)
    {
        m_widget->setText ("MEASURING");
    }
    else
    {
        m_widget->setText (QString::number(round(state()->fuelData.fuelPerLap * 1000)/10) + "% PER LAP");
    }

}


QString FuelPerLap::description ()
{
    return "Show fuel consumption per lap";
}

QList<QString> FuelPerLap::actions ()
{
    return QList<QString>();
}

QString FuelPerLap::componentId ()
{
    return "FuelPerLap";
}


static ComponentFactory::RegisterComponent<FuelPerLap> reg;
