#include "src/components/PedalGraph.h"

#include "src/components/ComponentFactory.h"

const size_t c_idxGearUp = 2;
const size_t c_idxGearDown = 3;
const size_t c_idxBrake = 0;
const size_t c_idxThrottle = 1;


PedalGraph::PedalGraph () : Component()
{
    m_widget = new Graph(nullptr);
    m_widget->setWidth(400);
    m_widget->setYRange(0, 100);

    m_widget->setColor (c_idxBrake, QColor(255, 0, 0));
    m_widget->setColor (c_idxThrottle, QColor(0, 255, 0));
    m_widget->setColor (c_idxGearDown, QColor(255, 255, 255, 127));
    m_widget->setColor (c_idxGearUp, QColor(255, 255, 255, 127));

    m_widget->setType(c_idxGearUp, Graph::MarkerUp);
    m_widget->setType(c_idxGearDown, Graph::MarkerDown);

    m_counter = 0;
}

QWidget * PedalGraph::getWidget() const
{
    return m_widget;
}

QString PedalGraph::defaultTitle () const
{
    return "Pedals";
}

void PedalGraph::newPoint(PTelemetryPoint p)
{
    m_widget->addValue(c_idxBrake, m_counter, p->brake());
    m_widget->addValue(c_idxThrottle, m_counter, p->throttle());

    if (!m_previous.isNull() && m_previous->currentGear() != p->currentGear())
    {
        if (m_previous->currentGear() > p->currentGear())
        {
            m_widget->addValue(c_idxGearDown, m_counter, 50);
        }
        else
        {
            m_widget->addValue(c_idxGearUp, m_counter, 50);
        }
    }

    m_counter++;
    m_previous = p;
}



QString PedalGraph::description ()
{
    return "Show the current pedal levels in a graph";
}

QMap<QString, Action> PedalGraph::actions ()
{
    return QMap<QString, Action>();
}

QString PedalGraph::componentId ()
{
    return "PedalGraph";
}

static ComponentFactory::RegisterComponent<PedalGraph> reg(true);
