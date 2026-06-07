#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include "sb/trackdata/TrackDetector.h"
#include "sb/widgets/Graph.h"

class TrackDetectDebug : public Component
{
public:
    TrackDetectDebug ();

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();


private:
    QWidget * m_widget = nullptr;
    ColorLabel * m_label = nullptr;
    Graph * m_graph = nullptr;
    PTrackDetector m_detect;
    float m_maxDist;
    float m_counter;
};
