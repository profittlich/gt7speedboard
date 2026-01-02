#include "sb/components/Empty.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

Empty::Empty (const QJsonValue json) : Component(json), m_text(new ComponentParameter<QString> ("text", "Empty", false)), m_color(new ComponentParameter<QString> ("color", "#fff", false))
{
    addComponentParameter(m_text);
    addComponentParameter(m_color);
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setText("EMPTY");
    m_widget->setStyleSheet("color : " + g_globalConfiguration.dimColor().name() + ";");
}


void Empty::parameterChanged(const PComponentParameterString & p)
{
    if (p == m_text)
    {
        m_widget->setText((*m_text)());
    }
    else if (p == m_color)
    {
        m_widget->setStyleSheet("color : " + (*m_color)() + ";");
    }
}

QWidget * Empty::getWidget() const
{
    return m_widget;
}

QString Empty::defaultTitle () const
{
    return "Empty";
}

QString Empty::description ()
{
    return "Empty widget with customizable text";
}

QString Empty::componentId ()
{
    return "Empty";
}

static ComponentFactory::RegisterComponent<Empty> reg;
