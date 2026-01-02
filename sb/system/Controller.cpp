#include "sb/system/Controller.h"
#include "sb/system/Configuration.h"

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
    m_timer.start();
    if (p->sequenceNumber() != m_previousSequenceNumber + 1)
    {
        DBG_MSG << ("Controller: Start of new telemetry sequence, d=" + QString::number (p->sequenceNumber() - m_previousSequenceNumber).toLatin1());
    }
    m_previousSequenceNumber = p->sequenceNumber();

    if (p->isPaused() || !p->inRace())
    {
        return;
    }

    //qInfo("Point");
    // Reset TODO: optimize
    QString newStyle = "background-color: " + g_globalConfiguration.dimColor().name() + ";";

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
                previousLap->setSucceedingPoint(p);

                m_state->currentLap = PLap(new Lap());
                if (previousLap->points().size() > 0)
                {
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
        else if (m_state->newLap)
        {
            m_state->newLap = false;
        }

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

    for (auto it : std::as_const(m_dash->components))
    {
        if (it->canFullScreenSignal())
        {
            QColor col = it->signalColor();
            if (col.isValid())
            {
                newStyle = "background-color: " + col.name() + ";";
            }
        }

        if (it->canRaise() && it->raise() && it->stacker() != nullptr)
        {
            it->stacker()->setCurrentIndex(it->stackIndex());
        }
    }

    if (newStyle != m_currentStyle)
    {
        m_dash->widget->setStyleSheet(newStyle);
        m_dash->widget->parentWidget()->setStyleSheet(newStyle);
        m_currentStyle = newStyle;
    }

    m_state->lastProcessingTime = m_timer.nsecsElapsed();
}


