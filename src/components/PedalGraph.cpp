#include "src/components/PedalGraph.h"

#include "src/components/ComponentFactory.h"

#include <QMouseEvent>
#include <QPainter>
#include <QTouchEvent>

class PedalGraphWidget final : public Graph
{
public:
    using Graph::Graph;

    void setPedalLevels(float brake, float throttle)
    {
        m_brake = brake;
        m_throttle = throttle;
        update();
    }

    void setIndicatorsVisible(bool visible)
    {
        m_indicatorsVisible = visible;
        update();
    }

protected:
    void paintGL() override
    {
        Graph::paintGL();

        if (!m_indicatorsVisible)
        {
            return;
        }

        const qreal margin = qMin<qreal>(8.0, qMin(width(), height()) / 20.0);
        const qreal squareSize = qMin(qMin(width(), height()) / 5.0,
                          qMin((width() - 3.0 * margin) / 2.0,
                           height() - 2.0 * margin));
        QPainter painter(this);
        painter.setPen(Qt::NoPen);
        painter.fillRect(QRectF(margin, margin, squareSize, squareSize), brakeColor());
        painter.fillRect(QRectF(2.0 * margin + squareSize, margin, squareSize, squareSize), throttleColor());
    }

private:
    QColor brakeColor() const
    {
        if (m_brake >= 100.0f)
        {
            return QColor(0xFF, 0x00, 0x00, 0x7F);
        }
        return m_brake > 0.0f ? QColor(0xFF, 0xFF, 0x00, 0x7F) : QColor(0,0,0,0x7F);
    }

    QColor throttleColor() const
    {
        if (m_throttle >= 100.0f)
        {
            return QColor(0x00, 0xFF, 0x00, 0x7F);
        }
        return m_throttle > 0.0f ? QColor(0x00, 0x7F, 0xFF, 0x7F) : QColor(0,0,0,0x7F);
    }

    float m_brake = 0.0f;
    float m_throttle = 0.0f;
    bool m_indicatorsVisible = true;
};

const size_t c_idxGearUp = 4;
const size_t c_idxGearDown = 5;
const size_t c_idxBrake = 3;
const size_t c_idxThrottle = 2;
const size_t c_idxRefBrake = 1;
const size_t c_idxRefThrottle = 0;


PedalGraph::PedalGraph () : Component()
    , m_showIndicators(new ComponentParameter<bool>("show pedal indicators", true, true))
    , m_showTarget(new ComponentParameter<bool>("show comparison target", true, true))
    , m_target(new ComponentParameter<QString>("Comparison target", "<none>", true))
{
    addComponentParameter(m_showIndicators);
    addComponentParameter(m_showTarget);
    addComponentParameter(m_target);
    m_widget = new PedalGraphWidget(nullptr);
    m_widget->setAttribute(Qt::WA_AcceptTouchEvents);
    m_widget->installEventFilter(this);
    m_widget->setIndicatorsVisible(m_showIndicators());
    m_widget->setWidth(400);
    m_widget->setYRange(0, 100);

    m_widget->setColor (c_idxRefBrake, QColor(95, 0, 0));
    m_widget->setColor (c_idxRefThrottle, QColor(0, 95, 0));
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

bool PedalGraph::eventFilter(QObject *obj, QEvent *event)
{
    if (obj == m_widget)
    {
        if (event->type() == QEvent::MouseButtonRelease)
        {
            const auto *mouseEvent = static_cast<QMouseEvent *>(event);
            if (mouseEvent->position().x() < m_widget->width() / 2.0)
            {
                callAction("togglePedalIndicators");
            }
            else
            {
                callAction("toggleComparisonTarget");
            }
        }
    }

    return Component::eventFilter(obj, event);
}

void PedalGraph::parameterChanged(const PComponentParameterBoolean & parameter)
{
    if (parameter == m_showIndicators)
    {
        m_widget->setIndicatorsVisible(m_showIndicators());
    }
    if (parameter == m_showTarget)
    {
        m_widget->setVisible(c_idxRefBrake, m_showTarget());
        m_widget->setVisible(c_idxRefThrottle, m_showTarget());
    }
}

QString PedalGraph::defaultTitle () const
{
    return "Pedals";
}

void PedalGraph::newPoint(PTelemetryPoint p)
{
    m_widget->setPedalLevels(p->brake(), p->throttle());
    m_widget->addValue(c_idxBrake, m_counter, p->brake());
    m_widget->addValue(c_idxThrottle, m_counter, p->throttle());

    if (state()->comparisonLaps.contains(m_target()))
    {
        auto ref = state()->comparisonLaps[m_target()];
        if (ref->hasClosestPoint)
        {
            m_widget->addValue (c_idxRefBrake, m_counter, ref->lap->points()[ref->closestPoint]->brake());
            m_widget->addValue (c_idxRefThrottle, m_counter, ref->lap->points()[ref->closestPoint]->throttle());
        }
    }

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
    QMap<QString, Action> result;
    result["togglePedalIndicators"] = { 1, "toggle pedal indicators", "Show or hide the brake and throttle indicators" };
    result["toggleComparisonTarget"] = { 1, "toggle comparison target", "Show or hide the comparison target" };
    return result;
}

void PedalGraph::callAction(QString action)
{
    if (action == "togglePedalIndicators")
    {
        m_showIndicators() = !m_showIndicators();
        parameterChanged(m_showIndicators);
    }
    if (action == "toggleComparisonTarget")
    {
        m_showTarget() = !m_showTarget();
        parameterChanged(m_showTarget);
    }
}

QString PedalGraph::componentId ()
{
    return "PedalGraph";
}

static ComponentFactory::RegisterComponent<PedalGraph> reg(true);
