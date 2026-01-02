#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

class Message : public Component
{
public:
    Message (const QJsonValue config);

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;
    virtual void newSession() override;
    virtual bool raise() override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();

private:
    ColorLabel * m_widget;
    int m_countdown;
};
