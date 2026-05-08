#include "sb/components/LapDisplay.h"

#include "sb/components/ComponentFactory.h"



LapDisplay::LapDisplay () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
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
    if (p->totalLaps() == 0)
    {
        if (state()->lapProgress > -0.5)
        {
            m_widget->setText (QString::number(round(100 * (p->currentLap() + state()->lapProgress))/100.0));
        }
        else
        {
            m_widget->setText (QString::number(p->currentLap()));
        }
    }
    else
    {
        if (state()->lapProgress > -0.5)
        {
            m_widget->setText (QString::number(round(100 * (p->currentLap() + state()->lapProgress))/100.0) + " of " + QString::number(p->totalLaps()) + "\n(" + QString::number(p->totalLaps() - round(100 * (p->currentLap() + state()->lapProgress))/100.0) + " left)");
        }
        else
        {
            m_widget->setText (QString::number(p->currentLap()) + " of " + QString::number(p->totalLaps()) + "\n(" + QString::number(p->totalLaps() - p->currentLap()) + " left)");
        }
    }
}


QString LapDisplay::description ()
{
    return "Show the current lap";
}

QMap<QString, Action> LapDisplay::actions ()
{
    return QMap<QString, Action>();
}

QString LapDisplay::componentId ()
{
    return "LapDisplay";
}


static ComponentFactory::RegisterComponent<LapDisplay> reg(true);
