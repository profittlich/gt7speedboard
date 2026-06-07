#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

#include <QElapsedTimer>

class RaceTime : public Component
{
public:
    RaceTime ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    virtual void callAction(QString a) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

public slots:
    void touched();


private:
    ColorLabel * m_widget = nullptr;
    PTelemetryPoint m_curPoint;
    QElapsedTimer m_timer;
    int m_elapsed;
    bool m_started;
    bool m_readyToStart;
    PComponentParameterFloat m_raceLength;
    PComponentParameterBoolean m_showLaps;
};
