#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"

class FuelRange : public Component
{
public:
    FuelRange ();

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

    virtual void callAction(QString a) override;


private:
    ColorLabel * m_widget = nullptr;
    PComponentParameterBoolean m_showTime;
};
