#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"

class Speed : public Component
{
public:
    Speed ();

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;

    virtual QColor signalColor() const override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    ColorLabel * m_widget = nullptr;
    float m_curSpeed = 0;
};
