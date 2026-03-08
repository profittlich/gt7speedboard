#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

class LapTimes : public Component
{
public:
    LapTimes (const QJsonValue config);

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();


private:
    ColorLabel * m_widget;
};
