#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"

class Gear : public Component
{
public:
    Gear ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();


private:
    ColorLabel * m_widget = nullptr;
};
