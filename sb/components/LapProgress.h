#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

class LapProgress : public Component
{
public:
    LapProgress ();

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    ColorLabel * m_widget;
    float m_curProgress;
};
