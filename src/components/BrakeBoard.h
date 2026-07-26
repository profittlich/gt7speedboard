#pragma once

#include <QRandomGenerator>

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"
#include "src/widgets/GaugeLabel.h"

class BrakeBoard : public Component
{
public:
    BrakeBoard ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;
    virtual void callAction(QString a) override;

    void parameterChanged(const PComponentParameterInt &) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:


    void updateLabels();
    void cycleModes();
    void cycleDifficulty();
    void updateMode();
    void updateDifficulty();

    void brakeTarget(PTelemetryPoint p);
    void brakeTiming(PTelemetryPoint p);

private:
    QWidget * m_widget;
    ColorLabel * m_topLabel;
    ColorLabel * m_mainLabel;
    ColorLabel * m_bottomLabel;
    GaugeLabel * m_deviation;

    float m_brakeTargetLevel = 50;
    QTime m_brakeDownTime;
    bool m_brakeFromFull = false;
    QList<float> m_prevBrakes;

    QTime m_startTime;
    QTime m_targetTime;
    float m_delayTime = 5000;

    enum { Begin, Braking, BrakingFull, BrakeLevelReached, BrakePoint, Countdown1, Countdown2, Countdown3, Result } m_state = Begin;
    PComponentParameterInt m_difficulty;
    PComponentParameterInt m_mode;

    QList<QString> m_difficultyNames = { "EASY", "MEDIUM", "HARD", "SENNA" };

    float m_brakeHoldTime = 60;
    float m_brakeHoldCorridor = 5;
    float m_brakeLevelTolerance = 12;
    float m_brakeTimingTolerance = 0.08;

    const float c_brakeMinimumLevel = 2;

};
