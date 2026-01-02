#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

class FuelPerLap : public Component
{
public:
    FuelPerLap (const QJsonValue config);

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();


private:
    ColorLabel * m_widget;
};
