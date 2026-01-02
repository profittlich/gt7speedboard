#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

class RPM : public Component
{
public:
    RPM (const QJsonValue config);

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();


private:
    ColorLabel * m_widget;
};
