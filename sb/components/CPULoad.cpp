#include "sb/components/CPULoad.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"
#include <QtWidgets/qboxlayout.h>

CPULoad::CPULoad () : Component()
{
    m_widget = new QWidget();
    QVBoxLayout * layout = new QVBoxLayout(m_widget);

    m_widgetFps = new GaugeLabel(m_widget, 0.0, 16.7, true, false);

    m_widgetFps->setValue(0);

    m_widgetFps->setAlignment(Qt::AlignCenter);
    QFont font = m_widgetFps->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widgetFps->setFont(font);
    m_widgetFps->setStyleSheet("color : #fff;");

    m_widgetFps->setText("?");

    m_widgetCpu = new GaugeLabel(m_widget, 0.0, 100.0, false, false);

    m_widgetCpu->setValue(0);

    m_widgetCpu->setAlignment(Qt::AlignCenter);
    font = m_widgetCpu->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widgetCpu->setFont(font);
    m_widgetCpu->setStyleSheet("color : #fff;");

    m_widgetCpu->setText("?");

    m_widgetDrops = new ColorLabel(m_widget);

    m_widgetDrops->setAlignment(Qt::AlignCenter);
    font = m_widgetDrops->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widgetDrops->setFont(font);
    m_widgetDrops->setStyleSheet("color : #fff;");

    layout->addWidget (m_widgetCpu);
    layout->addWidget (m_widgetFps);
    layout->addWidget (m_widgetDrops);
    layout->setContentsMargins(0,0,0,0);
}

QWidget * CPULoad::getWidget() const
{
    return m_widget;
}

QString CPULoad::defaultTitle () const
{
    return "System stress";
}

void CPULoad::newPoint(PTelemetryPoint p)
{
    if (p->sequenceNumber() % 6 > 0)
        return;
    unsigned summed = 0;
    for (auto i : state()->lastProcessingTimes)
    {
        summed += i;
    }
    unsigned avgTime = summed / state()->lastProcessingTimes.size();

    m_widgetCpu->setValue(100.0 * state()->cpuLoad);
    m_widgetCpu->setText(QString::number(round (1000.0 * state()->cpuLoad)/10.0) + " % proc thread");

    m_widgetFps->setValue(state()->avgFrameTime - 16.7);
    m_widgetFps->setText(QString::number(round(10.0 * (state()->avgFrameTime - 16.7))/10.0) + " ms jitter");

    m_widgetDrops->setText("Package loss: " + QString::number(state()->frameDrops-1));
}


QString CPULoad::description ()
{
    return "Show the CPU load of the telemetry stream processing";
}

QMap<QString, Action> CPULoad::actions ()
{
    return QMap<QString, Action>();
}

QString CPULoad::componentId ()
{
    return "CPULoad";
}

static ComponentFactory::RegisterComponent<CPULoad> reg(true);
