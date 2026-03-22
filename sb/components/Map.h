#pragma once

#include "sb/components/Component.h"
#include <QtOpenGL>
#include <QOpenGLWidget>

class Map;

class SBGLWidget : public QOpenGLWidget
{
public:
    SBGLWidget(Map * parent)
    {
        m_parent = parent;
        m_minX = 1000000.0;
        m_maxX = -1000000.0;
        m_minY = 1000000.0;
        m_maxY = -1000000.0;
    }

    void addPoint(const PTelemetryPoint & p);
    void nextLap();
    void updateRefLap(PLap refLap);
    void clearRefLap();

protected:
    void initializeGL() override;
    void resizeGL(int w, int h) override;
    void paintGL() override;

private:
    GLuint m_programObject;
    GLuint m_vShader;
    GLuint m_fShader;
    QList<GLfloat> m_verticesPrev;
    QList<GLfloat> m_vertices;
    QList<GLfloat> m_verticesRef;
    float m_minX;
    float m_maxX;
    float m_minY;
    float m_maxY;
    QList<GLfloat> m_aspectMatrix;
    QList<GLfloat> m_centerMatrix;
    QList<GLfloat> m_scaleMatrix;
    bool m_initialized;
    Map * m_parent; 
};


class Map : public Component
{
public:
    Map (const QJsonValue json);

    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();

    QString target();

private:
    SBGLWidget * m_widget;
    PComponentParameterString m_target;
    PLap m_refLap;
    bool m_firstPointReceived;
};
