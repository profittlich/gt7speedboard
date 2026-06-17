#pragma once

#include <QOpenGLWidget>

class Graph : public QOpenGLWidget
{
public:
    Graph(QWidget * parent) : QOpenGLWidget(parent)
    {
        m_width = -1;
        m_rangeMinY = 0;
        m_rangeMaxY = 0;
    }

    void addValue(size_t idx, float x, float y);
    void setColor(size_t idx, QColor col);

    void clear();
    void setWidth (float px)
    {
        m_width = px;
    }
    void setYRange (float min, float max)
    {
        m_rangeMinY = min;
        m_rangeMaxY = max;
    }

protected:
    void recalcExtents();

    void initializeGL() override;
    void resizeGL(int w, int h) override;
    void paintGL() override;

private:
    bool m_initialized = false;
    GLuint m_programObject;
    GLuint m_vShader;
    GLuint m_fShader;
    QList<GLfloat> m_scaleMatrix;
    QList<GLfloat> m_centerMatrix;
    QList<GLfloat> m_windowMatrix;

    float m_minX = 0;
    float m_maxX = 0;
    float m_minY = 0;
    float m_maxY = 0;

    int m_width = 0;
    float m_rangeMinY = 0;
    float m_rangeMaxY = 0;

    QList <QList<float>> m_values;
    QList <QColor> m_colors;
};
