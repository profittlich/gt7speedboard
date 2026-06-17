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

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

    QString target() const;

protected:
    bool targetLapUsable() const;

private:
    mutable SBGLMapWidget * m_widget = nullptr;
    PComponentParameterString m_target;
    PComponentParameterString m_renderer;
    PLap m_refLap;
    bool m_firstPointReceived = false;
};
