#include "src/components/PedalGraph.h"

#include "src/components/ComponentFactory.h"
#include "src/system/Configuration.h"

PedalGraph::PedalGraph () : Component()
{
    m_widget = new Graph(nullptr);
    m_widget->setWidth(400);
    m_widget->setYRange(0, 100);

    m_widget->setColor (2, QColor(255, 0, 0));
    m_widget->setColor (3, QColor(0, 255, 0));
    m_widget->setColor (1, QColor(127, 127, 127));
    m_widget->setColor (0, QColor(127, 127, 127));

    m_widget->setType(0, Graph::MarkerUp);
    m_widget->setType(1, Graph::MarkerDown);

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
    m_widget->addValue(2, m_counter, p->brake());
    m_widget->addValue(3, m_counter, p->throttle());

    if (!m_previous.isNull() && m_previous->currentGear() != p->currentGear())
    {
        if (m_previous->currentGear() > p->currentGear())
        {
            m_widget->addValue(0, m_counter, 50);
        }
        else
        {
            m_widget->addValue(1, m_counter, 50);
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
