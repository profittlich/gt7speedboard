#include "src/components/Map.h"

#include "src/components/ComponentFactory.h"
#include "src/components/MapRenderers/SBGLMapWidgetLines.h"
#include "src/components/MapRenderers/SBGLMapWidgetZoomedLines.h"

Map::Map () : Component(), m_target (new ComponentParameter<QString>("target","last", true)), m_target2 (new ComponentParameter<QString>("target2","", true)), m_target3 (new ComponentParameter<QString>("target3","", true)), m_renderer (new ComponentParameter<QString>("renderer","lines", true)), m_showCurrent(new ComponentParameter<bool>("show current lap", true, true)), m_showCurrentDot(new ComponentParameter<bool>("show current position", true, true)), m_showPrev(new ComponentParameter<bool>("show previous lap", true, true)), m_firstPointReceived(false)
{
    addComponentParameter(m_target);
    addComponentParameter(m_target2);
    addComponentParameter(m_target3);
    addComponentParameter(m_renderer);
    addComponentParameter(m_showCurrent);
    addComponentParameter(m_showCurrentDot);
    addComponentParameter(m_showPrev);
    m_widget = nullptr;
}

QWidget * Map::getWidget() const
{
    if (m_widget == nullptr)
    {
        if (m_renderer() == "lines")
        {
            m_widget = new SBGLMapWidgetLines(this);
        }
        else if (m_renderer() == "zoomedlines")
        {
            m_widget = new SBGLMapWidgetZoomedLines(this);
        }
        else
        {
            m_widget = new SBGLMapWidgetLines(this);
        }
    }
    return m_widget;
}

QString Map::defaultTitle () const
{
    return "Map";
}


QString Map::componentId ()
{
    return "Map";
}

QString Map::target() const
{
    return m_target();
}

QString Map::target2() const
{
    return m_target2();
}

QString Map::target3() const
{
    return m_target3();
}

void Map::loaded()
{
    if (state()->comparisonLaps.contains(m_target()) && (m_refLap.isNull() || state()->comparisonLaps[m_target()]->lap != m_refLap))
    {
        DBG_MSG << "loaded";
        m_refLap = state()->comparisonLaps[m_target()]->lap;
        m_widget->updateRefLap(m_refLap);
        m_widget->update();
    }

    if (state()->comparisonLaps.contains(m_target2()) && (m_refLap2.isNull() || state()->comparisonLaps[m_target2()]->lap != m_refLap2))
    {
        DBG_MSG << "loaded";
        m_refLap2 = state()->comparisonLaps[m_target2()]->lap;
        m_widget->updateRefLap2(m_refLap2);
        m_widget->update();
    }

    if (state()->comparisonLaps.contains(m_target3()) && (m_refLap3.isNull() || state()->comparisonLaps[m_target3()]->lap != m_refLap3))
    {
        DBG_MSG << "loaded";
        m_refLap3 = state()->comparisonLaps[m_target3()]->lap;
        m_widget->updateRefLap3(m_refLap3);
        m_widget->update();
    }

    parameterChanged(m_showCurrent);
    parameterChanged(m_showCurrentDot);
    parameterChanged(m_showPrev);
}

void Map::parameterChanged(const PComponentParameterBoolean & p)
{
    if (m_widget != nullptr)
    {
        if (p == m_showCurrent)
        {
            m_widget->setShowCurrent(p());
        }
        else if (p == m_showCurrentDot)
        {
            m_widget->setShowCurrentDot(p());
        }
        else if (p == m_showPrev)
        {
            m_widget->setShowPrevious(p());
        }
    }

}

bool Map::targetLapUsable(QString key) const
{
    return state()->comparisonLaps.contains(key) &&
           state()->comparisonLaps[key]->lap->maybeOnSameTrack(state()->currentLap);
}

void Map::newPoint(PTelemetryPoint p)
{
    m_widget->addPoint(p);
    if (!m_firstPointReceived)
    {
        m_firstPointReceived = true;

        if (state()->comparisonLaps.contains(m_target()) && (m_refLap.isNull() || state()->comparisonLaps[m_target()]->lap != m_refLap))
        {
            DBG_MSG << "Set up ref lap" << m_refLap.isNull();
            m_refLap = state()->comparisonLaps[m_target()]->lap;
            m_widget->updateRefLap(m_refLap);
        }
        if (state()->comparisonLaps.contains(m_target2()) && (m_refLap2.isNull() || state()->comparisonLaps[m_target2()]->lap != m_refLap2))
        {
            DBG_MSG << "Set up ref lap 2" << m_refLap2.isNull();
            m_refLap2 = state()->comparisonLaps[m_target2()]->lap;
            m_widget->updateRefLap2(m_refLap2);
        }
        if (state()->comparisonLaps.contains(m_target3()) && (m_refLap3.isNull() || state()->comparisonLaps[m_target3()]->lap != m_refLap3))
        {
            DBG_MSG << "Set up ref lap" << m_refLap.isNull();
            m_refLap3 = state()->comparisonLaps[m_target3()]->lap;
            m_widget->updateRefLap3(m_refLap3);
        }
    }
    if (!targetLapUsable(m_target()) && m_widget->hasRefLap())
    {
        m_refLap.clear();
        m_widget->clearRefLap();
    }
    if (!targetLapUsable(m_target2()) && m_widget->hasRefLap2())
    {
        m_refLap2.clear();
        m_widget->clearRefLap2();
    }
    if (!targetLapUsable(m_target3()) && m_widget->hasRefLap3())
    {
        m_refLap3.clear();
        m_widget->clearRefLap3();
    }

    if (targetLapUsable(m_target()) && (m_refLap.isNull() || state()->comparisonLaps[m_target()]->lap != m_refLap || m_refLap->points().size() != qsizetype(m_prevSize)))
    {
        m_refLap = state()->comparisonLaps[m_target()]->lap;
        m_prevSize = m_refLap->points().size();
        //DBG_MSG << "New ref lap:" << m_refLap->points().size();
        m_widget->updateRefLap(m_refLap);
    }
    if (targetLapUsable(m_target2()) && (m_refLap2.isNull() || state()->comparisonLaps[m_target2()]->lap != m_refLap2 || m_refLap2->points().size() != qsizetype(m_prevSize2)))
    {
        m_refLap2 = state()->comparisonLaps[m_target2()]->lap;
        m_prevSize2 = m_refLap2->points().size();
        //DBG_MSG << "New ref lap2:" << m_refLap2->points().size();
        m_widget->updateRefLap2(m_refLap2);
    }
    if (targetLapUsable(m_target3()) && (m_refLap3.isNull() || state()->comparisonLaps[m_target3()]->lap != m_refLap3 || m_refLap3->points().size() != qsizetype(m_prevSize3)))
    {
        m_refLap3 = state()->comparisonLaps[m_target3()]->lap;
        m_prevSize3 = m_refLap3->points().size();
        //DBG_MSG << "New ref lap3:" << m_refLap3->points().size();
        m_widget->updateRefLap3(m_refLap3);
    }

    m_widget->update();
}

void Map::completedLap(PLap, bool)
{
    if (state()->comparisonLaps.contains(m_target()) && (m_refLap.isNull() || state()->comparisonLaps[m_target()]->lap != m_refLap))
    {
        m_refLap = state()->comparisonLaps[m_target()]->lap;
        DBG_MSG << "New ref lap:" << m_refLap->points().size();
        m_widget->updateRefLap(m_refLap);
    }
    if (state()->comparisonLaps.contains(m_target2()) && (m_refLap2.isNull() || state()->comparisonLaps[m_target2()]->lap != m_refLap2))
    {
        m_refLap2 = state()->comparisonLaps[m_target2()]->lap;
        DBG_MSG << "New ref lap:2" << m_refLap2->points().size();
        m_widget->updateRefLap2(m_refLap2);
    }
    if (state()->comparisonLaps.contains(m_target3()) && (m_refLap3.isNull() || state()->comparisonLaps[m_target3()]->lap != m_refLap3))
    {
        m_refLap3 = state()->comparisonLaps[m_target3()]->lap;
        DBG_MSG << "New ref lap3:" << m_refLap3->points().size();
        m_widget->updateRefLap3(m_refLap3);
    }
    m_widget->nextLap();
}


QString Map::description ()
{
    return "Show a map of the track and the current location";
}

QMap<QString, Action> Map::actions ()
{
    return QMap<QString, Action>();
}

static ComponentFactory::RegisterComponent<Map> reg(true);
