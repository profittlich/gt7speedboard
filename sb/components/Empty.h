#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include <QtCore/qdatetime.h>

class Empty : public Component
{
public:
    Empty (const QJsonValue json);

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void parameterChanged(const PComponentParameterString &) override;
    virtual void parameterChanged(const PComponentParameterFloat & p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    ColorLabel * m_widget;
    PComponentParameterString m_text;
    PComponentParameterString m_color;
    PComponentParameterFloat m_hideWidget;
};
