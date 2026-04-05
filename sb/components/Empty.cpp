#include "sb/components/Empty.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

Empty::Empty (const QJsonValue json) : Component(json), m_text(new ComponentParameter<QString> ("text", "Empty", false)), m_color(new ComponentParameter<QString> ("color", "#fff", false)), m_hideWidget (new ComponentParameter<float> ("hideWidget", 0, false))
{
    addComponentParameter(m_text);
    addComponentParameter(m_color);
    addComponentParameter(m_hideWidget);
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setText("EMPTY");
    m_widget->setStyleSheet("color : " + g_globalConfiguration.dimColor().name() + ";");
    m_widget->setColor(QColor("red"));
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

void Empty::parameterChanged(const PComponentParameterFloat & p)
{
    DBG_MSG << "float parameterChanged";
    if (p == m_hideWidget)
    {
        DBG_MSG << "hideWidget" << (*m_hideWidget)();
        //m_widget->setHidden((*m_hideWidget)() > 0.5);
        if ((*m_hideWidget)() > 0.5)
        {
            m_widget->setDisabled(true);
        }
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

QList<QString> Empty::actions ()
{
    return QList<QString>();
}

static ComponentFactory::RegisterComponent<Empty> reg;
