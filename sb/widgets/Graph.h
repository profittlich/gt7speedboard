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
    bool m_initialized;
    GLuint m_programObject;
    GLuint m_vShader;
    GLuint m_fShader;
    QList<GLfloat> m_scaleMatrix;
    QList<GLfloat> m_centerMatrix;
    QList<GLfloat> m_windowMatrix;

    float m_minX;
    float m_maxX;
    float m_minY;
    float m_maxY;

    int m_width;
    float m_rangeMinY;
    float m_rangeMaxY;

    QList <QList<float>> m_values;
    QList <QColor> m_colors;
};
