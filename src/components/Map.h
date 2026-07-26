#pragma once

#include "src/components/Component.h"
#include "src/components/MapRenderers/SBGLMapWidget.h"

class Map : public Component
{
public:
    Map ();

    virtual void loaded() override;
    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    virtual void parameterChanged(const PComponentParameterBoolean &) override;

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

    QString target() const;
    QString target2() const;
    QString target3() const;

protected:
    bool targetLapUsable(QString key) const;

private:
    mutable SBGLMapWidget * m_widget = nullptr;
    PComponentParameterString m_target;
    PComponentParameterString m_target2;
    PComponentParameterString m_target3;
    PComponentParameterString m_renderer;
    PComponentParameterBoolean m_showCurrent;
    PComponentParameterBoolean m_showCurrentDot;
    PComponentParameterBoolean m_showPrev;
    PLap m_refLap;
    PLap m_refLap2;
    PLap m_refLap3;
    size_t m_prevSize = 0;
    size_t m_prevSize2 = 0;
    size_t m_prevSize3 = 0;
    bool m_firstPointReceived = false;
};
