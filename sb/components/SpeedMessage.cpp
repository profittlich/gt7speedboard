#include "sb/components/SpeedMessage.h"

#include "sb/components/ComponentFactory.h"

SpeedMessage::SpeedMessage (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 15);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("0\nkm/h");
}

QWidget * SpeedMessage::getWidget() const
{
    return m_widget;
}

QString SpeedMessage::defaultTitle () const
{
    return "Speed Message";
}

void SpeedMessage::newPoint(PTelemetryPoint p)
{
    if (m_countdown > 0)
    {
        m_countdown--;
    }
    else
    {
        m_widget->setText("");
    }
}

void SpeedMessage::completedLap(PLap lastLap, bool isFullLap)
{
    DBG_MSG << ("New lap message on");
    m_widget->setText("NEW LAP");
    m_countdown = 180;
}

void SpeedMessage::newSession()
{
    DBG_MSG << ("New session message on");
    m_widget->setText("NEW SESSION");
    m_countdown = 180;
}

bool SpeedMessage::raise()
{
    return m_countdown > 0;
}

QString SpeedMessage::description ()
{
    return "Simple speedometer message for testing";
}

QList<QString> SpeedMessage::actions ()
{
    return QList<QString>();
}

QString SpeedMessage::componentId ()
{
    return "SpeedMessage";
}

static ComponentFactory::RegisterComponent<SpeedMessage> reg;
