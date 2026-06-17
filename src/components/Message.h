#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"

class Message : public Component
{
public:
    Message ();

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;
    virtual void newSession() override;
    virtual bool raise() override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

private:
    QList<QString> m_messageQueue;
    ColorLabel * m_widget = nullptr;
    int m_countdown = 0;
};
