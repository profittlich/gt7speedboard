#include "sb/components/Speed.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

Speed::Speed (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 10);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");
    m_widget->setText("0\nKM/H");
}

QWidget * Speed::getWidget() const
{
    return m_widget;
}

QString Speed::defaultTitle () const
{
    return "Speed";
}

void Speed::newPoint(PTelemetryPoint p)
{
    m_curSpeed = p->carSpeed();
    if (p->sequenceNumber() % 10 == 0)
    {
        m_widget->setText (QString::number(round(p->carSpeed())) + "\nKM/H");
    }
}

QColor Speed::signalColor() const
{
    if (m_curSpeed >= 200)
    {
        return QColor (0xff0000);
    }
    return QColor();
}

QString Speed::description ()
{
    return "Simple speedometer";
}

QMap<QString, Action> Speed::actions ()
{
    return QMap<QString, Action>();
}

QString Speed::componentId ()
{
    return "Speed";
}

static ComponentFactory::RegisterComponent<Speed> reg;
