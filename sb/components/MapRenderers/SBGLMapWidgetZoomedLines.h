#pragma once

#include "SBGLMapWidget.h"

class SBGLMapWidgetZoomedLines : public SBGLMapWidget
{
public:
    SBGLMapWidgetZoomedLines(const Map * parent) : SBGLMapWidget(parent)
    {
        recalcExtents();
    }

    void addPoint(const PTelemetryPoint & p) override;
    void nextLap() override;
    void updateRefLap(PLap refLap) override;
    void clearRefLap() override;

protected:
    void recalcExtents();

    void initializeGL() override;
    void resizeGL(int w, int h) override;
    void paintGL() override;

private:
    QList<GLfloat> m_verticesPrev;
    QList<GLfloat> m_vertices;
    QList<GLfloat> m_verticesRef;
    float m_minX = 0;
    float m_maxX = 0;
    float m_minY = 0;
    float m_maxY = 0;

    GLuint m_programObject = 0;
    GLuint m_vShader = 0;
    GLuint m_fShader = 0;
    QList<GLfloat> m_aspectMatrix;
    QList<GLfloat> m_centerMatrix;
    QList<GLfloat> m_scaleMatrix;
    QList<GLfloat> m_rotateMatrix;
};
