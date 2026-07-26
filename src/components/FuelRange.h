#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"

class FuelRange : public Component
{
public:
    FuelRange ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

    virtual void callAction(QString a) override;


private:
    ColorLabel * m_widget = nullptr;
    PComponentParameterBoolean m_showTime;
};
