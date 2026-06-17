#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"
#include "src/widgets/GaugeLabel.h"
#include "src/system/Helpers.h"

class TyreTemps : public Component
{
public:
    TyreTemps ();

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    virtual void newPoint(PTelemetryPoint p);

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

    //virtual QList<ComponentParameter<float>> getFloatParameters() override;
    //virtual ComponentParameter<float> floatParameter(const QString & key) override;
    //virtual void loatParameter (ComponentParameter<float> &) override;

    virtual void callAction(QString a) override;

    bool eventFilter(QObject *obj, QEvent *event) override;

    virtual void presetSwitched() override;
    //virtual void switchToPreset(QString preset) override;

private:
    QWidget * m_widget = nullptr;
    ColorLabel * m_fl = nullptr;
    ColorLabel * m_fr = nullptr;
    ColorLabel * m_rl = nullptr;
    ColorLabel * m_rr = nullptr;

    ColorMapper * m_colorMapper = nullptr;

    PComponentParameterFloat m_target;
    PComponentParameterFloat m_spread;
};
