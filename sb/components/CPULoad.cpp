#include "sb/components/CPULoad.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

CPULoad::CPULoad (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("?");
}

QWidget * CPULoad::getWidget() const
{
    return m_widget;
}

QString CPULoad::defaultTitle () const
{
    return "CPU load";
}

void CPULoad::newPoint(PTelemetryPoint p)
{
    DBG_MSG << state()->lastProcessingTime/1000.0;
    m_widget->setText(QString::number(round(state()->lastProcessingTime/1000.0)));// / (10000000000.0/59.94)) + " %");
}


QString CPULoad::description ()
{
    return "Show the CPU load of the telemetry stream processing";
}

QList<QString> CPULoad::actions ()
{
    return QList<QString>();
}

QString CPULoad::componentId ()
{
    return "CPULoad";
}

static ComponentFactory::RegisterComponent<CPULoad> reg;
