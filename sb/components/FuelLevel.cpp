#include "sb/components/FuelLevel.h"

#include "sb/components/ComponentFactory.h"



FuelLevel::FuelLevel () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("? %");
}

QWidget * FuelLevel::getWidget() const
{
    return m_widget;
}

QString FuelLevel::defaultTitle () const
{
    return "Fuel level";
}

void FuelLevel::newPoint(PTelemetryPoint p)
{
    m_widget->setText (QString::number(round(p->currentFuel() * 10)/10) + "%");
}


QString FuelLevel::description ()
{
    return "Show current fuel level";
}

QMap<QString, Action> FuelLevel::actions ()
{
    return QMap<QString, Action>();
}

QString FuelLevel::componentId ()
{
    return "FuelLevel";
}


static ComponentFactory::RegisterComponent<FuelLevel> reg(true);
