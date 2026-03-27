#include "sb/system/Controller.h"
#include "sb/cardata/TelemetryPointGT7.h"
#include "sb/system/Configuration.h"
#include "sb/widgets/DashWidget.h"

void Controller::setDash(PDash d)
{
    m_dash = d;
}

PDash Controller::dash()
{
    return m_dash;
}

PState Controller::state()
{
    return m_state;
}

void Controller::newTelemetryPoint(PTelemetryPoint p)
{
    static unsigned sCarId=0;
    auto fpsTime = m_fpsTimer.nsecsElapsed();
    m_fpsTimer.start();

    m_timer.start();
    if (p->sequenceNumber() != m_previousSequenceNumber + 1)
    {
        DBG_MSG << ("Controller: Start of new telemetry sequence, d=" + QString::number (p->sequenceNumber() - m_previousSequenceNumber).toLatin1());
        m_state->currentLap->invalidate();
        m_state->frameDrops++;
    }
    m_previousSequenceNumber = p->sequenceNumber();

    PTelemetryPointGT7 gt7 = qSharedPointerCast<TelemetryPointGT7>(p);

    if (!gt7.isNull() && gt7->carID() != sCarId)
    {
        sCarId = gt7->carID();
        DBG_MSG << "New car ID: " << sCarId;

    }

    if (p->isPaused() || !p->inRace())
    {
        return;
    }

    if (m_state->presetChanged)
    {
        m_state->presetChanged = false;
        for (auto it : std::as_const(m_dash->components))
        {
            it->switchToPreset(m_state->currentPreset);
        }
    }

    // Update components, first those without widget, then with widget
    PLap previousLap;
    bool withoutWidget = true;
    for (size_t o = 0; o < 2; ++o)
    {
        for (auto it : std::as_const(m_dash->components))
        {
            if ((it->getWidget() == nullptr) == withoutWidget)
            {
                it->newPoint(p);
            }
        }

        // New lap
        if (m_state->newLap && !m_state->currentLap->points().empty())
        {
            DBG_MSG << ("new Lap, closed loop: " + QString::number(m_state->newLapIsClosedLoop).toLatin1());

            m_state->newLap = false || withoutWidget;

            if (withoutWidget)
            {
                previousLap = m_state->currentLap;
                DBG_MSG << "Old lap length = " << previousLap->points().size();
                m_state->previousLaps.append(previousLap);
                if (p->currentLap() == previousLap->points()[0]->currentLap() + 1)
                {
                    DBG_MSG << "set succeeding point" << previousLap->points()[0]->currentLap() << "->" << p->currentLap() << p->lastLapMs();
                    previousLap->setSucceedingPoint(p);
                }

                m_state->currentLap = PLap(new Lap());

                if (p->currentLap() == previousLap->points()[0]->currentLap() + 1 && previousLap->points().size() > 0)
                {
                    DBG_MSG << "set preceeding point" << previousLap->points()[previousLap->points().size()-1]->currentLap() << "->" << p->currentLap() << previousLap->points()[previousLap->points().size()-1]->lastLapMs();

                    m_state->currentLap->setPreceedingPoint(previousLap->points()[previousLap->points().size()-1]);
                }
            }

            for (auto it : std::as_const(m_dash->components))
            {
                if ((it->getWidget() == nullptr) == withoutWidget)
                {
                    it->completedLap(previousLap, m_state->newLapIsClosedLoop);
                }
            }
        }

        if (!withoutWidget)
        {
            m_state->newLap = false;
        }

        // pit stop
        if (m_state->inPit)
        {
            DBG_MSG << ("in pit");
            for (auto it : std::as_const(m_dash->components))
            {
                if ((it->getWidget() == nullptr) == withoutWidget)
                {
                    it->pitStop();
                }
            }
        }

        if (!withoutWidget)
        {
            m_state->inPit = false;
        }

        // current lap
        if (withoutWidget)
        {
            m_state->currentLap->appendTelemetryPoint(p);
        }

        // New session
        if (m_state->newSession)
        {
            DBG_MSG << ("new session");
            for (auto it : std::as_const(m_dash->components))
            {
                if ((it->getWidget() == nullptr) == withoutWidget)
                {
                    it->newSession();
                }
            }
        }

        if (!withoutWidget)
        {
            m_state->newSession = false;
        }

        // Update components with complete data
        for (auto it : std::as_const(m_dash->components))
        {
            if ((it->getWidget() == nullptr) == withoutWidget)
            {
                it->pointFinished(p);
            }
        }

        withoutWidget = !withoutWidget;
    }

    // Update UI
    for (auto it : std::as_const(m_dash->components))
    {
        if (it->stacker() != nullptr)
        {
            it->stacker()->setCurrentIndex(0);
        }
    }

    QColor newColor;
    m_dash->widget->setColor(g_globalConfiguration.dimColor());
    for (auto it : std::as_const(m_dash->components))
    {
        if (it->canFullScreenSignal())
        {
            QColor col = it->signalColor();
            if (col.isValid() && col != m_currentColor)
            {
                m_dash->widget->setColor(col);
                newColor = col;
            }
        }

        if (newColor != m_currentColor)
        {
            m_dash->widget->update();
            m_currentColor = newColor;
        }

        if (it->canRaise() && it->raise() && it->stacker() != nullptr)
        {
            it->stacker()->setCurrentIndex(it->stackIndex());
        }
    }

    m_state->clearMessages();

    m_state->lastProcessingTimes.push_back (m_timer.nsecsElapsed());
    m_state->lastProcessingTimes.pop_front();

    unsigned summed = 0;
    for (auto i : m_state->lastProcessingTimes)
    {
        summed += i;
    }
    unsigned avgTime = summed / state()->lastProcessingTimes.size();

    m_state->lastFpsTimes.push_back (fpsTime);
    m_state->lastFpsTimes.pop_front();

    summed = 0;
    for (auto i : m_state->lastFpsTimes)
    {
        summed += i;
    }
    unsigned avgFpsTime = float(summed) / state()->lastFpsTimes.size();


    m_state->cpuLoad = (m_timer.nsecsElapsed()/1000)/1000.0/16.7;
    m_state->avgFrameTime = (fpsTime/100000)/10.0;
}


