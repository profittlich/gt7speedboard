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


protected:
    bool m_initialized = false;
    const Map * m_parent = nullptr;
};
