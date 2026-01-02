#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include <QtCore/qdatetime.h>

class CPULoad : public Component
{
public:
    CPULoad (const QJsonValue config);

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();


private:
    ColorLabel * m_widget;
};
