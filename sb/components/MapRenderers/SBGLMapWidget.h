#pragma once

#include <QtOpenGL>
#include <QOpenGLWidget>
#include "sb/cardata/TelemetryPoint.h"
#include "sb/system/Laps.h"

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
    bool m_initialized;
    const Map * m_parent = nullptr;
};
