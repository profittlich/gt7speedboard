#include "sb/components/Message.h"

#include "sb/components/ComponentFactory.h"

Message::Message (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("-");
}

QWidget * Message::getWidget() const
{
    return m_widget;
}

QString Message::defaultTitle () const
{
    return "Message";
}

void Message::newPoint(PTelemetryPoint p)
{
    auto newMessages = state()->messages("main");
    m_messageQueue.append(newMessages);

    if (m_countdown > 0)
    {
        m_countdown--;
    }
    else
    {
        if (m_messageQueue.size() > 0)
        {
            m_widget->setText(m_messageQueue.front());
            m_messageQueue.pop_front();
            m_countdown = 100;
        }
        else
        {
            m_widget->setText("");
        }
    }
}

void Message::completedLap(PLap lastLap, bool isFullLap)
{
    DBG_MSG << ("New lap message on");
    //m_widget->setText("NEW LAP");
    //m_countdown = 180;
    m_messageQueue.append("NEW LAP");
}

void Message::newSession()
{
    DBG_MSG << ("New session message on");
    //m_widget->setText("NEW SESSION");
    //m_countdown = 180;
    m_messageQueue.append("NEW SESSION");
}

bool Message::raise()
{
    return m_countdown > 0;
}

QString Message::description ()
{
    return "Simple speedometer message for testing";
}

QMap<QString, Action> Message::actions ()
{
    return QMap<QString, Action>();
}

QString Message::componentId ()
{
    return "Message";
}

static ComponentFactory::RegisterComponent<Message> reg;
