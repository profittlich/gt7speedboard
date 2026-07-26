#pragma once

#include <QtOpenGL>
#include <QOpenGLWidget>
#include "src/cardata/TelemetryPoint.h"
#include "src/system/Laps.h"

class Map;

class SBGLMapWidget : public QOpenGLWidget
{
public:
    SBGLMapWidget(const Map * parent)
    {
        m_parent = parent;
    }

    virtual void addPoint(const PTelemetryPoint & p) = 0;
    virtual void nextLap() = 0;

    virtual void updateRefLap(PLap refLap) = 0;
    virtual void clearRefLap() = 0;
    virtual bool hasRefLap() = 0;

    virtual void updateRefLap2(PLap refLap) = 0;
    virtual void clearRefLap2() = 0;
    virtual bool hasRefLap2() = 0;

    virtual void updateRefLap3(PLap refLap) = 0;
    virtual void clearRefLap3() = 0;
    virtual bool hasRefLap3() = 0;

    void setShowCurrent(bool on) { m_showCurrent = on; }
    void setShowCurrentDot(bool on) { m_showCurrentDot = on; }
    void setShowPrevious(bool on) { m_showPrev = on; }


protected:
    bool m_initialized = false;
    const Map * m_parent = nullptr;
    bool m_showCurrent = true;
    bool m_showCurrentDot = false;
    bool m_showPrev = true;
};
