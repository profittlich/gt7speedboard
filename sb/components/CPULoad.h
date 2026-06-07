#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/GaugeLabel.h"
#include "sb/widgets/ColorLabel.h"
#include <QtCore/qdatetime.h>

class CPULoad : public Component
{
public:
    CPULoad ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();


private:
    QWidget * m_widget = nullptr;
    GaugeLabel * m_widgetCpu = nullptr;
    GaugeLabel * m_widgetFps = nullptr;
    ColorLabel * m_widgetDrops = nullptr;
};
