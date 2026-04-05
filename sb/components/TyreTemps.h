#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include "sb/widgets/GaugeLabel.h"
#include "sb/system/Helpers.h"

class TyreTemps : public Component
{
public:
    TyreTemps (const QJsonValue config);

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();

    //virtual QList<ComponentParameter<float>> getFloatParameters() override;
    //virtual ComponentParameter<float> floatParameter(const QString & key) override;
    //virtual void loatParameter (ComponentParameter<float> &) override;

    virtual void callAction(QString a) override;

    bool eventFilter(QObject *obj, QEvent *event) override;

    virtual void presetSwitched() override;
    //virtual void switchToPreset(QString preset) override;

private:
    QWidget * m_widget;
    ColorLabel * m_fl;
    ColorLabel * m_fr;
    ColorLabel * m_rl;
    ColorLabel * m_rr;

    ColorMapper * m_colorMapper;

    PComponentParameterFloat m_target;
    PComponentParameterFloat m_spread;
};
