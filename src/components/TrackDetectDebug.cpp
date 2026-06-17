#include "src/components/TrackDetectDebug.h"

#include "src/cardata/TelemetryPointGT7.h"
#include "src/components/ComponentFactory.h"
#include "src/system/Configuration.h"

#include <sstream>
#include <QVBoxLayout>



TrackDetectDebug::TrackDetectDebug () : Component()
{
    m_widget = new QWidget();
    QVBoxLayout * layout = new QVBoxLayout(m_widget);
    layout->setContentsMargins(0,0,0,0);

    m_label = new ColorLabel(m_widget);
    layout->addWidget(m_label);

    m_label->setAlignment(Qt::AlignCenter);
    QFont font = m_label->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_label->setFont(font);
    m_label->setStyleSheet("color : #fff;");

    m_label->setWordWrap(true);

    m_graph = new Graph(m_widget);
    m_graph->addValue(0, 0,0);
    m_graph->setWidth(1000);
    //m_graph->setYRange(0, 40);
    m_graph->setColor (0, QColor(255, 255, 0));
    m_graph->setColor (1, QColor(127, 127, 255));
    layout->addWidget(m_graph);

    m_detect = PTrackDetector(new TrackDetector());
    m_maxDist = 0.0;
    m_counter = 0;
}

QWidget * TrackDetectDebug::getWidget() const
{
    return m_widget;
}

QString TrackDetectDebug::defaultTitle () const
{
    return "TD Debug";
}

void TrackDetectDebug::newPoint(PTelemetryPoint p)
{
    if (!m_detect->trackFound())
    {
        m_detect->addPoint(p);
        m_label->setText ("Detecting...");

    }
    else
    {
        PTrack track = m_detect->detectedTrack();
        size_t index;
        float dist;
        bool on = track->isOnTrack(p, index, 0, false, &dist);
        if (on)
        {
        m_maxDist = std::max (dist, m_maxDist);
        std::stringstream conv;
        conv << track->name().toStdString() << "\n" << index << " - " << round(dist) << " - " << round(m_maxDist);
        m_label->setText(conv.str().c_str());
        m_graph->addValue(0, m_counter, m_maxDist);
        m_graph->addValue(1, m_counter++, dist);
        }
    }
}


QString TrackDetectDebug::description ()
{
    return "Show debugging info for track detection (developer tool)";
}

QMap<QString, Action> TrackDetectDebug::actions ()
{
    return QMap<QString, Action>();
}

QString TrackDetectDebug::componentId ()
{
    return "TrackDetectDebug";
}


static ComponentFactory::RegisterComponent<TrackDetectDebug> reg(true);
