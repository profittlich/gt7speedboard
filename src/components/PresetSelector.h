#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"

class PresetSelector : public Component
{
public:
    PresetSelector ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

    virtual void callAction(QString a) override;
    virtual void presetSwitched() override;

private:
    QWidget * m_widget = nullptr;
    ColorLabel * m_label = nullptr;

    PComponentParameterString m_preset;
    PComponentParameterString m_presetListParameter;
    QStringList m_presetList;
    int m_currentPreset = 0;
};
