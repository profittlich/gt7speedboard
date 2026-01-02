#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include "sb/widgets/GaugeLabel.h"

class LapComparison : public Component
{
public:
    LapComparison (const QJsonValue config);

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void pointFinished(PTelemetryPoint p) override;
    virtual void presetSwitched() override;
    virtual QColor signalColor () override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();


private:
    ColorMapperGreenRed * m_colorMapper;
    QWidget * m_widget;
    ColorLabel * m_speed;
    GaugeLabel * m_time;
    PComponentParameterString m_target;
    PComparisonLap m_targetLap;
};
