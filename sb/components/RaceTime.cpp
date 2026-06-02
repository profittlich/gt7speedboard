#include "sb/components/RaceTime.h"

#include "sb/components/ComponentFactory.h"



RaceTime::RaceTime () : Component(), m_raceLength(new ComponentParameter<float>("Race length", 40, true)), m_showLaps(new ComponentParameter<bool>("Laps left", false, true))
{
    m_started = false;
    m_readyToStart = false;
    addComponentParameter(m_raceLength);
    addComponentParameter(m_showLaps);
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("");
    connect(m_widget, &ColorLabel::clicked, this, &RaceTime::touched);
    m_timer.restart();
}

QWidget * RaceTime::getWidget() const
{
    return m_widget;
}

QString RaceTime::defaultTitle () const
{
    return "Race Time";
}

void RaceTime::newPoint(PTelemetryPoint p)
{
    auto ms = m_timer.elapsed();
    auto elapsed = msToTime(ms);
    elapsed = elapsed.left(elapsed.length()-4);
    float laps = p->currentLap()-1;

    //DBG_MSG << "Race estimation available:" << m_started;
    if (m_started && (*m_showLaps)() && laps > 0)
    {
        float lapsLeft = (laps / m_elapsed) * (1000 * 60 * (*m_raceLength)()) - laps;
        //DBG_MSG << "rounded laps left:" << lapsLeft;
        lapsLeft = ceil(lapsLeft);
        QString risk = "";
        if (state()->lapProgress > -0.5)
        {
            lapsLeft = (laps + state()->lapProgress) / ms * (1000 * 60 * (*m_raceLength)()) - laps;
            //DBG_MSG << "exact laps left:" << lapsLeft;
            if (lapsLeft - int(lapsLeft) > 0.9)
            {
                risk = " (+1?)";
            }
            else if (lapsLeft - int(lapsLeft) < 0.1)
            {
                risk = " (-1?)";
            }

            lapsLeft = ceil(lapsLeft);
            lapsLeft -= state()->lapProgress;
            //DBG_MSG << "with final lap:" << lapsLeft;
            lapsLeft = round(100*lapsLeft) / 100;
        }
        m_widget->setText (elapsed + " (" + QString::number((*m_raceLength)()) + " min. race)\n" + QString::number(lapsLeft) + risk + " laps to go");

    }
    else if ((*m_showLaps)())
    {
        m_widget->setText (elapsed + " (" + QString::number((*m_raceLength)()) + " min. race)");
    }
    else
    {
        m_widget->setText (elapsed);
    }
    m_curPoint = p;
}

void RaceTime::completedLap(PLap lastLap, bool isFullLap)
{
    if (m_curPoint->currentLap() == 0)
    {
        m_readyToStart = true;
    }
    else if (m_curPoint->currentLap() == 1 && m_readyToStart)
    {
        m_timer.restart();
        m_started = true;
        m_elapsed = 0;
        m_readyToStart = false;
    }
    else
    {
        m_elapsed = m_timer.elapsed();
    }
}

void RaceTime::callAction(QString a)
{
    if (a == "timeUp")
    {
        if ((*m_raceLength)() < 1440)
        {
            (*m_raceLength)()++;
        }
    }
    else if (a == "timeDown")
    {
        if ((*m_raceLength)() > 1)
        {
            (*m_raceLength)()--;
        }
    }
    else if (a == "toggleLapsLeft")
    {
        (*m_showLaps)() = !(*m_showLaps)();
    }
}

void RaceTime::touched()
{
    callAction("toggleLapsLeft");
}


QString RaceTime::description ()
{
    return "Time in the race and laps left";
}

QMap<QString, Action> RaceTime::actions ()
{
    QMap<QString, Action> result;

    result["timeUp"] = { 1, "time +", "increase the race length by 1 minute"};
    result["timeDown"] = { 2, "time -", "decrease the race length by 1 minute"};
    result["toggleLapsLeft"] = { 2, "toggle laps left", "show laps left in timed race or only time"};

    return result;
}

QString RaceTime::componentId ()
{
    return "RaceTime";
}


static ComponentFactory::RegisterComponent<RaceTime> reg(true);
