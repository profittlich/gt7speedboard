#include "sb/components/CarName.h"

#include "sb/cardata/TelemetryPointGT7.h"
#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"



CarName::CarName () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("?");
}

QWidget * CarName::getWidget() const
{
    return m_widget;
}

QString CarName::defaultTitle () const
{
    return "Car name";
}

void CarName::newPoint(PTelemetryPoint p)
{
    PTelemetryPointGT7 pgt7 = p.dynamicCast<TelemetryPointGT7>();
    m_widget->setText (g_globalConfiguration.carName(pgt7->carID()));
}


QString CarName::description ()
{
    return "Show the model of the current car";
}

QMap<QString, Action> CarName::actions ()
{
    return QMap<QString, Action>();
}

QString CarName::componentId ()
{
    return "CarName";
}


static ComponentFactory::RegisterComponent<CarName> reg(true);
