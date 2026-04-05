#include "sb/components/PresetSelector.h"

#include "sb/components/ComponentFactory.h"

#include<QGridLayout>
#include <QJsonObject>

PresetSelector::PresetSelector (const QJsonValue conf) : Component(conf), m_preset(new ComponentParameter<QString> ("preset", "", false)), m_presetListParameter (new ComponentParameter<QString> ("presetList", "SOFT;MEDIUM;HARD;INTER;WET", false)), m_currentPreset(-1)
{
    addComponentParameter(m_preset);
    addComponentParameter(m_presetListParameter);
    m_widget = new QWidget();

    QGridLayout * layout = new QGridLayout(m_widget);
    layout->setContentsMargins(0,0,0,0);

    m_label = new ColorLabel();
    layout->addWidget(m_label, 0, 0);

    QFont font = m_label->font();
    font.setPointSizeF(baseFontSize() * 8);

    m_label->setAlignment(Qt::AlignCenter);
    m_label->setFont(font);
    m_label->setStyleSheet("color : #fff;");
    m_label->setText("<none>");

    m_presetList = (*m_presetListParameter)().split(";");
}

QWidget * PresetSelector::getWidget() const
{
    return m_widget;
}

QString PresetSelector::defaultTitle () const
{
    return "Preset";
}

QString PresetSelector::description ()
{
    return "Change presets via key or touch";
}

QMap<QString, Action> PresetSelector::actions ()
{
    QMap<QString, Action> result;

    result["nextPreset"] = { 1, "next preset", "switch to the next parameter preset"};
    result["prevPreset"] = { 2, "previous preset", "switch to the previous parameter preset"};

    return result;
}

void PresetSelector::presetSwitched()
{
    m_presetList = (*m_presetListParameter)().split(";");
}

QString PresetSelector::componentId ()
{
    return "PresetSelector";
}


void PresetSelector::callAction(QString a)
{
    if (a == "nextPreset")
    {
        m_currentPreset++;
        if (m_currentPreset >= m_presetList.count())
        {
            m_currentPreset = 0;
        }
        m_label->setText(m_presetList[m_currentPreset]);
        state()->currentPreset = m_presetList[m_currentPreset];
        state()->presetChanged = true;
    }
    else if (a == "prevPreset")
    {
        m_currentPreset--;
        if (m_currentPreset < 0)
        {
            m_currentPreset = m_presetList.count() - 1;
        }
        m_label->setText(m_presetList[m_currentPreset]);
        state()->currentPreset = m_presetList[m_currentPreset];
        state()->presetChanged = true;
    }
}

static ComponentFactory::RegisterComponent<PresetSelector> reg;
