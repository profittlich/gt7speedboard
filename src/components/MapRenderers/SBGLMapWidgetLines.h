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
    bool hasRefLap() override;
    void updateRefLap2(PLap refLap) override;
    void clearRefLap2() override;
    bool hasRefLap2() override;
    void updateRefLap3(PLap refLap) override;
    void clearRefLap3() override;
    bool hasRefLap3() override;

protected:
    void recalcExtents();

    void initializeGL() override;
    void resizeGL(int w, int h) override;
    void paintGL() override;

private:
    QList<GLfloat> m_verticesPrev;
    QList<GLfloat> m_vertices;
    QList<GLfloat> m_verticesRef;
    QList<GLfloat> m_verticesRef2;
    QList<GLfloat> m_verticesRef3;
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
};
