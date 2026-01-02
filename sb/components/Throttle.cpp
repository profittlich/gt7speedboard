#include "sb/components/Throttle.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

Throttle::Throttle (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 10);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");
    m_widget->setText("0 %");
}

QWidget * Throttle::getWidget() const
{
    return m_widget;
}

QString Throttle::defaultTitle () const
{
    return "Throttle";
}

void Throttle::newPoint(PTelemetryPoint p)
{
    m_curThrottle = p->throttle();
    if (p->sequenceNumber() % 10 == 0)
    {
        m_widget->setText (QString::number(round(p->throttle())) + " %");
    }
}

QColor Throttle::signalColor()
{
    if (m_curThrottle >= 99)
    {
        return QColor (0xff0000);
    }
    return QColor();
}

QString Throttle::description ()
{
    return "Show the current throttle level";
}

QList<QString> Throttle::actions ()
{
    return QList<QString>();
}

QString Throttle::componentId ()
{
    return "Throttle";
}

static ComponentFactory::RegisterComponent<Throttle> reg;
