#pragma once

#include "src/components/Component.h"
#include "src/widgets/Graph.h"

class PedalGraphWidget;

class PedalGraph : public Component
{
public:
    PedalGraph ();

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;
    virtual void callAction(QString action) override;
    virtual void parameterChanged(const PComponentParameterBoolean &) override;
    bool eventFilter(QObject *obj, QEvent *event) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    PedalGraphWidget * m_widget = nullptr;
    PComponentParameterBoolean m_showIndicators;
    PComponentParameterBoolean m_showTarget;
    PComponentParameterString m_target;
    int m_counter = 0;
    PTelemetryPoint m_previous;
};
