#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

class Throttle : public Component
{
public:
    Throttle (const QJsonValue config);

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;

    virtual QColor signalColor() const override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();

private:
    ColorLabel * m_widget;
    float m_curThrottle;
};
