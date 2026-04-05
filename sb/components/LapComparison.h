#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include "sb/widgets/GaugeLabel.h"

class LapComparison : public Component
{
    Q_OBJECT
public:
    LapComparison (const QJsonValue config);
    ~LapComparison();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void pointFinished(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;
    virtual void presetSwitched() override;
    virtual QColor signalColor () const override;
    virtual void callAction(QString a) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

public slots:
    void goFullscreen();
    void rotateTargets();

protected:
    PComponentParameterString currentTarget();
    void updateLabel();


private:
    ColorMapperGreenRed * m_colorMapper;
    QWidget * m_widget;
    ColorLabel * m_speed;
    GaugeLabel * m_time;
    PComponentParameterFloat m_currentTarget;
    PComponentParameterString m_target;
    PComponentParameterString m_secondTarget;
    PComponentParameterString m_thirdTarget;
    PComparisonLap m_targetLap;
    bool m_prevFullScreenPermission;

    static QString s_fullScreenTarget;
    static QList<LapComparison*> s_allLapComparisons;
};
