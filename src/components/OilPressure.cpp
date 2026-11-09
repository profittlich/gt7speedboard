#include "src/components/OilPressure.h"

#include "src/components/ComponentFactory.h"

OilPressure::OilPressure() : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("0 PSI");
}

QWidget * OilPressure::getWidget() const
{
    return m_widget;
}

QString OilPressure::defaultTitle() const
{
    return "Oil pressure";
}

void OilPressure::newPoint(PTelemetryPoint p)
{
    const float psi = p->oilPressure();
    m_widget->setText(QString::number(round(psi)) + " PSI");
}

QString OilPressure::description()
{
    return "Show current oil pressure";
}

QMap<QString, Action> OilPressure::actions()
{
    return QMap<QString, Action>();
}

QString OilPressure::componentId()
{
    return "OilPressure";
}

static ComponentFactory::RegisterComponent<OilPressure> reg(true);
