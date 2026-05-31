#pragma once

#include "SBGLMapWidget.h"

class SBGLMapWidgetLines : public SBGLMapWidget
{
public:
    SBGLMapWidgetLines(const Map * parent) : SBGLMapWidget(parent)
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
    float m_minX;
    float m_maxX;
    float m_minY;
    float m_maxY;

    GLuint m_programObject;
    GLuint m_vShader;
    GLuint m_fShader;
    QList<GLfloat> m_aspectMatrix;
    QList<GLfloat> m_centerMatrix;
    QList<GLfloat> m_scaleMatrix;
};
