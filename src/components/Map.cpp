#include "src/components/Map.h"

#include "src/components/ComponentFactory.h"
#include "src/system/Configuration.h"
#include "src/components/MapRenderers/SBGLMapWidgetLines.h"
#include "src/components/MapRenderers/SBGLMapWidgetZoomedLines.h"

Map::Map () : Component(), m_target (new ComponentParameter<QString>("target","last", true)), m_renderer (new ComponentParameter<QString>("renderer","lines", true)), m_firstPointReceived(false)
{
    addComponentParameter(m_target);
    addComponentParameter(m_renderer);
    m_widget = nullptr;
}

QWidget * Map::getWidget() const
{
    if (m_widget == nullptr)
    {
        if ((*m_renderer)() == "lines")
        {
            m_widget = new SBGLMapWidgetLines(this);
        }
        else if ((*m_renderer)() == "zoomedlines")
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
    return (*m_target)();
}

void Map::loaded()
{
    if (state()->comparisonLaps.contains((*m_target)()) && (m_refLap.isNull() || state()->comparisonLaps[(*m_target)()]->lap != m_refLap))
    {
        DBG_MSG << "loaded";
        m_refLap = state()->comparisonLaps[(*m_target)()]->lap;
        m_widget->updateRefLap(m_refLap);
        m_widget->update();
    }
    else
    {
        DBG_MSG << "loaded failed";
    }
}

bool Map::targetLapUsable() const
{
    return state()->comparisonLaps.contains((*m_target)()) &&
           state()->comparisonLaps[(*m_target)()]->lap->maybeOnSameTrack(state()->currentLap);
           /*(!state()->comparisonLaps[(*m_target)()]->lap->trackDetector()->trackFound() ||
            !state()->currentLap->trackDetector()->trackFound() ||
            state()->comparisonLaps[(*m_target)()]->lap->trackDetector()->detectedTrack().get() == state()->currentLap->trackDetector()->detectedTrack().get());*/
}

void Map::newPoint(PTelemetryPoint p)
{
    m_widget->addPoint(p);
    if (!m_firstPointReceived)
    {
        m_firstPointReceived = true;

        if (state()->comparisonLaps.contains((*m_target)()) && (m_refLap.isNull() || state()->comparisonLaps[(*m_target)()]->lap != m_refLap))
        {
            DBG_MSG << "Set up ref lap" << m_refLap.isNull();
            m_refLap = state()->comparisonLaps[(*m_target)()]->lap;
            m_widget->updateRefLap(m_refLap);
        }
    }
    if (!targetLapUsable())
    {
        m_refLap.clear();
        m_widget->clearRefLap();
    }

    if (targetLapUsable() && (m_refLap.isNull() || state()->comparisonLaps[(*m_target)()]->lap != m_refLap))
    {
        m_refLap = state()->comparisonLaps[(*m_target)()]->lap;
        m_widget->updateRefLap(m_refLap);
    }

    m_widget->update();
}

void Map::completedLap(PLap lastLap, bool isFullLap)
{
    if (state()->comparisonLaps.contains((*m_target)()) && (m_refLap.isNull() || state()->comparisonLaps[(*m_target)()]->lap != m_refLap))
    {
        m_refLap = state()->comparisonLaps[(*m_target)()]->lap;
        m_widget->updateRefLap(m_refLap);
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
