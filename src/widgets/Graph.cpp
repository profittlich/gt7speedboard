#include "Graph.h"
#include <QtOpenGL>
#include "src/system/Helpers.h"
#include "src/system/Configuration.h"

void Graph::addValue(size_t idx, float x, float y)
{
    while (m_values.size() < idx+1)
    {
        m_values.append(QList<float>());
    }
    while (m_colors.size() < idx+1)
    {
        m_colors.append(QColor(1,1,1));
    }
    m_values[idx].append(x);
    m_values[idx].append(y);
    m_values[idx].append(0);

    if (m_values[idx].size() > 3 * m_width)
    {
        m_values[idx].pop_front();
        m_values[idx].pop_front();
        m_values[idx].pop_front();
    }

    recalcExtents();
    update();
}

void Graph::setColor(size_t idx, QColor col)
{
    while (m_colors.size() < idx+1)
    {
        m_colors.append(QColor(1,1,1));
    }
    m_colors[idx] = col;
}

void Graph::clear()
{
    m_values.clear();
    m_colors.clear();
}

void Graph::recalcExtents()
{
    m_minX = 1000000.0;
    m_maxX = -1000000.0;
    m_minY = 1000000.0;
    m_maxY = -1000000.0;
    for (size_t idx = 0; idx < static_cast<size_t>(m_values.size()); idx++)
    {
        for (size_t i = 0; i < static_cast<size_t>(m_values[idx].size()); i+=3)
        {
            if (m_values[idx][i] < m_minX)
            {
                m_minX = m_values[idx][i];
            }
            if (m_values[idx][i] > m_maxX)
            {
                m_maxX = m_values[idx][i];
            }
            if (m_values[idx][i+1] < m_minY)
            {
                m_minY = m_values[idx][i+1];
            }
            if (m_values[idx][i+1] > m_maxY)
            {
                m_maxY = m_values[idx][i+1];
            }
        }
    }

    if (m_width > 0)
    {
        m_minX = m_maxX - m_width;
    }
    if (m_rangeMinY != m_rangeMaxY)
    {
        m_minY = m_rangeMinY;
        m_maxY = m_rangeMaxY;
    }
}

void Graph::initializeGL()
{
    m_initialized = false;

    m_centerMatrix.resize(16);
    m_centerMatrix[0] = 1.0;
    m_centerMatrix[5] = 1.0;
    m_centerMatrix[10] = 1.0;
    m_centerMatrix[15] = 1.0;

    m_scaleMatrix.resize(16);
    m_scaleMatrix[0] = 1.0;
    m_scaleMatrix[5] = 1.0;
    m_scaleMatrix[10] = 1.0;
    m_scaleMatrix[15] = 1.0;

    m_windowMatrix.resize(16);
    m_windowMatrix[0] = 1.0;
    m_windowMatrix[5] = 1.0;
    m_windowMatrix[10] = 1.0;
    m_windowMatrix[15] = 1.0;

    // Set up the rendering context, load shaders and other resources, etc.:
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();

    f->glClearColor(g_globalConfiguration.backgroundColor().redF(), g_globalConfiguration.backgroundColor().greenF(), g_globalConfiguration.backgroundColor().blueF(), 1.0f);
    GLint compiled = 1;

    m_programObject = f->glCreateProgram();
    if(m_programObject == 0)
    {
        DBG_MSG << ("Could not create program object");
        return;
    }

    m_vShader = f->glCreateShader(GL_VERTEX_SHADER);


    const char *vShaderStr =
        "attribute vec4 vPosition; \n"
        "uniform mat4 uCenterMatrix;\n"
        "uniform mat4 uScaleMatrix;\n"
        "uniform mat4 uWindowMatrix;\n"
        "void main() \n"
        "{ \n"
        " gl_Position[0] = vPosition[0]; \n"
        " gl_Position[1] = vPosition[1]; \n"
        " gl_Position[2] = vPosition[2]; \n"
        " gl_Position[3] = vPosition[3]; \n"
        " gl_Position =  gl_Position * uWindowMatrix * uScaleMatrix * uCenterMatrix;\n"
        //" gl_PointSize = 20.0;\n"
        "} \n";

    f->glShaderSource(m_vShader, 1, &vShaderStr, NULL);
    // Compile the shader
    f->glCompileShader(m_vShader);

    f->glGetShaderiv(m_vShader, GL_COMPILE_STATUS, &compiled);
    if(compiled == 0)
    {
        DBG_MSG << ("Could not compile vertex shader");

        GLint infoLen = 0;
        f->glGetShaderiv(m_vShader, GL_INFO_LOG_LENGTH, &infoLen);
        if(infoLen > 1)
        {
            char* infoLog = (char*)malloc(sizeof(char) * infoLen);
            f->glGetShaderInfoLog(m_vShader, infoLen, NULL, infoLog);
            DBG_MSG << ("Error compiling shader:\n%s\n", infoLog);
            free(infoLog);
        }

        f->glDeleteShader(m_vShader);
        return;
    }

    m_fShader = f->glCreateShader(GL_FRAGMENT_SHADER);

    const char* fShaderStr =
#ifdef Q_OS_ANDROID
        "precision mediump float;\n"
#endif
        "uniform vec3 uColor;\n"
        "void main() \n"
        "{ \n"
        " gl_FragColor = vec4(uColor[0], uColor[1], uColor[2], 1.0); \n"
        "} \n";

    f->glShaderSource(m_fShader, 1, &fShaderStr, NULL);
    // Compile the shader
    f->glCompileShader(m_fShader);

    f->glGetShaderiv(m_fShader, GL_COMPILE_STATUS, &compiled);
    if(compiled == 0)
    {
        qDebug("Could not compile fragment shader");

        GLint infoLen = 0;
        f->glGetShaderiv(m_fShader, GL_INFO_LOG_LENGTH, &infoLen);
        if(infoLen > 1)
        {
            char* infoLog = (char*)malloc(sizeof(char) * infoLen);
            f->glGetShaderInfoLog(m_fShader, infoLen, NULL, infoLog);
            qDebug("Error compiling shader:\n%s\n", infoLog);
            free(infoLog);
        }

        f->glDeleteShader(m_fShader);
        return;
    }

    f->glAttachShader(m_programObject, m_vShader);
    f->glAttachShader(m_programObject, m_fShader);

    f->glBindAttribLocation(m_programObject, 0, "vPosition");
    //glBindAttribLocation(m_programObject, 1, "uColor");

    f->glLinkProgram(m_programObject);

    GLint linked;
    f->glGetProgramiv(m_programObject, GL_LINK_STATUS, &linked);
    if(!linked)
    {
        qDebug("Could not link program");
        return;
    }

    m_initialized = true;

}

void Graph::resizeGL(int w, int h)
{

}

void Graph::paintGL()
{
    if (!m_initialized)
    {
        return;
    }

    auto dx = m_maxX - m_minX;
    auto cx = (m_maxX + m_minX)/2.0;
    auto dy = m_maxY - m_minY;
    auto cy = (m_maxY + m_minY)/2.0;

    float centerScale = 0;
    if (dx > dy)
    {
        centerScale = dx;
    }
    else
    {
        centerScale = dy;
    }

    //DBG_MSG << dx << dy;
    m_scaleMatrix[0] = 2/dx;//10000.0;//1.5/centerScale;
    m_scaleMatrix[5] = 2/dy;//100.0;//1.5/centerScale;
    m_scaleMatrix[10] = 1.0;//1.5/centerScale;
    m_scaleMatrix[15] = 1.0;

    m_centerMatrix[3] = -1;//-cx;
    m_centerMatrix[7] = -1;//-cy;

    m_windowMatrix[3] = -(m_maxX-m_width);
    m_windowMatrix[7] = 0;

    // Draw the scene:
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();
    f->glClear(GL_COLOR_BUFFER_BIT);

    auto uLoc = f->glGetUniformLocation(m_programObject, "uColor");
    auto uLocC = f->glGetUniformLocation(m_programObject, "uCenterMatrix");
    auto uLocS = f->glGetUniformLocation(m_programObject, "uScaleMatrix");
    auto uLocW = f->glGetUniformLocation(m_programObject, "uWindowMatrix");

    f->glUseProgram(m_programObject);
    f->glLineWidth(4);

    f->glUniformMatrix4fv(uLocC, 1, false, m_centerMatrix.data());
    f->glUniformMatrix4fv(uLocS, 1, false, m_scaleMatrix.data());
    f->glUniformMatrix4fv(uLocW, 1, false, m_windowMatrix.data());

    for (size_t idx = 0; idx < m_values.size(); ++idx)
    {
        if (m_values[idx].size())
        {
            f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, m_values[idx].data());
            f->glUniform3f(uLoc, m_colors[idx].redF(), m_colors[idx].greenF(), m_colors[idx].blueF());
            f->glEnableVertexAttribArray(0);
            f->glDrawArrays(GL_LINE_STRIP, 0, m_values[idx].size()/3);
        }
    }

    /*QPainter painter(this);
    painter.setPen(Qt::white);
    painter.setFont(QFont("Arial", 56));
    painter.drawText(0, 0, width(), height(), Qt::AlignCenter, "Hello World!");
    painter.end();*/
}