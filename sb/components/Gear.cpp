#include "sb/components/Gear.h"

#include "sb/components/ComponentFactory.h"



Gear::Gear (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 15);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("0");
}

QWidget * Gear::getWidget() const
{
    return m_widget;
}

QString Gear::defaultTitle () const
{
    return "Gear";
}

void Gear::newPoint(PTelemetryPoint p)
{
    m_widget->setText (QString::number(p->currentGear()));
}


QString Gear::description ()
{
    return "Simple Gear meter";
}

QList<QString> Gear::actions ()
{
    return QList<QString>();
}

QString Gear::componentId ()
{
    return "Gear";
}


static ComponentFactory::RegisterComponent<Gear> reg;
