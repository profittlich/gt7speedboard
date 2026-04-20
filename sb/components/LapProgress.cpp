#include "sb/components/LapProgress.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

LapProgress::LapProgress () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 10);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");
    m_widget->setText("-");
}

QWidget * LapProgress::getWidget() const
{
    return m_widget;
}

QString LapProgress::defaultTitle () const
{
    return "Progress";
}

void LapProgress::newPoint(PTelemetryPoint p)
{
    m_curProgress = state()->lapProgress;
    if (p->sequenceNumber() % 10 == 0)
    {
        if (m_curProgress < -0.5)
        {
            m_widget->setText ("-");
        }
        else
        {
            m_widget->setText (QString::number(round(100.0 * m_curProgress)) + "%");
        }
    }
}

QString LapProgress::description ()
{
    return "Show the time-based progress in a lap";
}

QMap<QString, Action> LapProgress::actions ()
{
    return QMap<QString, Action>();
}

QString LapProgress::componentId ()
{
    return "LapProgress";
}

static ComponentFactory::RegisterComponent<LapProgress> reg(true);
