#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

class CarName : public Component
{
public:
    CarName (const QJsonValue config);

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();


private:
    ColorLabel * m_widget;
};
