#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"
#include "src/trackdata/TrackDetector.h"
#include "src/widgets/Graph.h"

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
    float m_maxDist = 0;
    float m_counter = 0;
};
