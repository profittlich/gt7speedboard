#include "sb/components/LapDisplay.h"

#include "sb/components/ComponentFactory.h"



LapDisplay::LapDisplay (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 15);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("0");
}

QWidget * LapDisplay::getWidget() const
{
    return m_widget;
}

QString LapDisplay::defaultTitle () const
{
    return "Lap";
}

void LapDisplay::newPoint(PTelemetryPoint p)
{
    m_widget->setText (QString::number(p->currentLap()));
}


QString LapDisplay::description ()
{
    return "Show the current lap";
}

QList<QString> LapDisplay::actions ()
{
    return QList<QString>();
}

QString LapDisplay::componentId ()
{
    return "LapDisplay";
}


static ComponentFactory::RegisterComponent<LapDisplay> reg;
