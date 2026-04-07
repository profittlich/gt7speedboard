#include "sb/components/Brake.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

Brake::Brake () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 10);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");
    m_widget->setText("0 %");
}

QWidget * Brake::getWidget() const
{
    return m_widget;
}

QString Brake::defaultTitle () const
{
    return "Brake";
}

void Brake::newPoint(PTelemetryPoint p)
{
    m_curBrake = p->brake();
    if (p->sequenceNumber() % 10 == 0)
    {
        m_widget->setText (QString::number(round(p->brake())) + " %");
    }
}

QColor Brake::signalColor() const
{
    if (m_curBrake >= 99)
    {
        return QColor (0xff0000);
    }
    return QColor();
}

QString Brake::description ()
{
    return "Show the current braking level";
}

QMap<QString, Action> Brake::actions ()
{
    return QMap<QString, Action>();
}

QString Brake::componentId ()
{
    return "Brake";
}

static ComponentFactory::RegisterComponent<Brake> reg;
