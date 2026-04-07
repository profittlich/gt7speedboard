#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include "sb/system/Helpers.h"

class PresetSelector : public Component
{
public:
    PresetSelector ();

    virtual QWidget * getWidget() const;

    virtual QString defaultTitle () const;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

    virtual void callAction(QString a) override;
    virtual void presetSwitched() override;

private:
    QWidget * m_widget;
    ColorLabel * m_label;

    PComponentParameterString m_preset;
    PComponentParameterString m_presetListParameter;
    QStringList m_presetList;
    int m_currentPreset;
};
