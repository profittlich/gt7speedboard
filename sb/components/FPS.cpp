#include "sb/components/FPS.h"

#include "sb/components/ComponentFactory.h"

FPS::FPS () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("? FPS");
    m_timer.start();
    m_counter = 0;
}

QWidget * FPS::getWidget() const
{
    return m_widget;
}

QString FPS::defaultTitle () const
{
    return "FPS";
}

void FPS::newPoint(PTelemetryPoint p)
{
    m_counter++;
    if (m_counter == 60)
    {
        float fps = round(60 * 10000000000.0/m_timer.nsecsElapsed())/10.0;
        m_widget->setText(QString::number(fps) + " FPS");
        m_counter = 0;
        m_timer.restart();
    }
}


QString FPS::description ()
{
    return "Show the FPS of the incoming telemetry stream";
}

QMap<QString, Action> FPS::actions ()
{
    return QMap<QString, Action>();
}

QString FPS::componentId ()
{
    return "FPS";
}

static ComponentFactory::RegisterComponent<FPS> reg(true);
