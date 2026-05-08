#pragma once


#include "sb/components/Component.h"

class ProgressManager : public Component
{
public:
    ProgressManager ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:

private:
};