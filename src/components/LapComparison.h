#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"
#include "src/widgets/GaugeLabel.h"

class LapComparison : public Component
{
    Q_OBJECT
public:
    LapComparison ();
    ~LapComparison();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void pointFinished(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;
    virtual void newTrack(PTrack track) override;
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
    ColorMapperGreenRed * m_colorMapper = nullptr;
    QWidget * m_widget = nullptr;
    ColorLabel * m_speed = nullptr;
    GaugeLabel * m_time = nullptr;
    ColorLabel * m_offset = nullptr;
    PComponentParameterFloat m_currentTarget;
    PComponentParameterString m_firstTarget;
    PComponentParameterString m_secondTarget;
    PComponentParameterString m_thirdTarget;
    static PComponentParameterFloat s_offset;
    PComparisonLap m_targetLap;

    bool m_prevFullScreenPermission = false;

    static QString s_fullScreenTarget;
    static QList<LapComparison*> s_allLapComparisons;
};
