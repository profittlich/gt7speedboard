#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/Graph.h"

class PedalGraph : public Component
{
public:
    PedalGraph ();

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    Graph * m_widget = nullptr;
    int m_counter = 0;
    PTelemetryPoint m_previous;
};
