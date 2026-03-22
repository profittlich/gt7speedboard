#include "sb/components/Map.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

Map::Map (const QJsonValue json) : Component(json), m_target (new ComponentParameter<QString>("target","last", true)), m_firstPointReceived(false)
{
    addComponentParameter(m_target);
    m_widget = new SBGLWidget(this);
}

QWidget * Map::getWidget() const
{
    return m_widget;
}

QString Map::defaultTitle () const
{
    return "Map";
}

QString Map::description ()
{
    return "Map widget with customizable text";
}

QString Map::componentId ()
{
    return "Map";
}

QString Map::target()
{
    return (*m_target)();
}

void Map::newPoint(PTelemetryPoint p)
{
    m_widget->addPoint(p);
    if (!m_firstPointReceived)
    {
        m_firstPointReceived = true;

        if (state()->comparisonLaps.contains((*m_target)()) && (m_refLap.isNull() || state()->comparisonLaps[(*m_target)()]->lap != m_refLap))
        {
            DBG_MSG << "Set up ref lap" << m_refLap.isNull();
            m_refLap = state()->comparisonLaps[(*m_target)()]->lap;
            m_widget->updateRefLap(m_refLap);
        }
    }
    if (!state()->comparisonLaps.contains((*m_target)()))
    {
        m_refLap.clear();
        m_widget->clearRefLap();
    }

    m_widget->update();
}

void Map::completedLap(PLap lastLap, bool isFullLap)
{
    if (state()->comparisonLaps.contains((*m_target)()) && (m_refLap.isNull() || state()->comparisonLaps[(*m_target)()]->lap != m_refLap))
    {
        m_refLap = state()->comparisonLaps[(*m_target)()]->lap;
        m_widget->updateRefLap(m_refLap);
    }
    m_widget->nextLap();
}

void SBGLWidget::clearRefLap()
{
    m_verticesRef.clear();
}

void SBGLWidget::updateRefLap(PLap refLap)
{
    m_verticesRef.clear();
    for (auto i : refLap->points())
    {
        if (i->position().x() < m_minX)
        {
            m_minX = i->position().x();
        }
        if (i->position().x() > m_maxX)
        {
            m_maxX = i->position().x();
        }
        if (i->position().z() < m_minY)
        {
            m_minY = i->position().z();
        }
        if (i->position().z() > m_maxY)
        {
            m_maxY = i->position().z();
        }
        m_verticesRef.append(i->position().x());
        m_verticesRef.append(i->position().y());
        m_verticesRef.append(i->position().z());
    }
    DBG_MSG << "New ref lap size: " << m_verticesRef.size();
}

void SBGLWidget::addPoint(const PTelemetryPoint & p)
{
    if (p->position().x() < m_minX)
    {
        m_minX = p->position().x();
    }
    if (p->position().x() > m_maxX)
    {
        m_maxX = p->position().x();
    }
    if (p->position().z() < m_minY)
    {
        m_minY = p->position().z();
    }
    if (p->position().z() > m_maxY)
    {
        m_maxY = p->position().z();
    }
    m_vertices.append(p->position().x());
    m_vertices.append(p->position().y());
    m_vertices.append(p->position().z());
}

void SBGLWidget::nextLap()
{
    if (m_vertices.size() > 3)
    {
        DBG_MSG << "set previous lap data" << m_vertices.size() << m_verticesPrev.size();
        m_verticesPrev = m_vertices;
    }
    m_vertices.clear();
}

void SBGLWidget::initializeGL()
{
    m_aspectMatrix.resize(16);
    m_aspectMatrix[0] = 1.0;
    m_aspectMatrix[5] = 1.0;
    m_aspectMatrix[10] = 1.0;
    m_aspectMatrix[15] = 1.0;

    m_scaleMatrix.resize(16);
    m_scaleMatrix[0] = 1.0;
    m_scaleMatrix[5] = 1.0;
    m_scaleMatrix[10] = 1.0;
    m_scaleMatrix[15] = 1.0;

    m_centerMatrix.resize(16);
    m_centerMatrix[0] = 1.0;
    m_centerMatrix[5] = 1.0;
    m_centerMatrix[10] = 1.0;
    m_centerMatrix[15] = 1.0;

    m_initialized = false;
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
        "uniform mat4 uAspectMatrix;\n"
        "uniform mat4 uCenterMatrix;\n"
        "uniform mat4 uScaleMatrix;\n"
        "void main() \n"
        "{ \n"
        " gl_Position[0] = vPosition[0]; \n"
        " gl_Position[1] = -vPosition[2]; \n"
        " gl_Position[2] = vPosition[1]; \n"
        " gl_Position[3] = vPosition[3]; \n"
        " gl_Position =  gl_Position * uCenterMatrix * uScaleMatrix * uAspectMatrix;\n"
        " gl_PointSize = 20.0;\n"
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

void SBGLWidget::resizeGL(int w, int h)
{
    if (w > h)
    {
        m_aspectMatrix[0] = (float(h)/float(w));
        m_aspectMatrix[5] = 1.0;
        m_aspectMatrix[10] = 1.0;
        m_aspectMatrix[15] = 1.0;
    }
    else
    {
        m_aspectMatrix[0] = 1.0;
        m_aspectMatrix[5] = (float(w)/float(h));
        m_aspectMatrix[10] = 1.0;
        m_aspectMatrix[15] = 1.0;
    }


}


void SBGLWidget::paintGL()
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

    m_scaleMatrix[0] = 1.5/centerScale;
    m_scaleMatrix[5] = 1.5/centerScale;
    m_scaleMatrix[10] = 1.5/centerScale;
    m_scaleMatrix[15] = 1.0;

    m_centerMatrix[3] = -cx;
    m_centerMatrix[7] = cy;

    // Draw the scene:
    QOpenGLFunctions *f = QOpenGLContext::currentContext()->functions();
    f->glClear(GL_COLOR_BUFFER_BIT);

    auto uLoc = f->glGetUniformLocation(m_programObject, "uColor");
    auto uLocA = f->glGetUniformLocation(m_programObject, "uAspectMatrix");
    auto uLocT = f->glGetUniformLocation(m_programObject, "uCenterMatrix");
    auto uLocS = f->glGetUniformLocation(m_programObject, "uScaleMatrix");

    f->glUseProgram(m_programObject);
    f->glLineWidth(5);

    f->glUniformMatrix4fv(uLocA, 1, false, m_aspectMatrix.data());
    f->glUniformMatrix4fv(uLocT, 1, false, m_centerMatrix.data());
    f->glUniformMatrix4fv(uLocS, 1, false, m_scaleMatrix.data());

    f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, m_verticesPrev.data());
    f->glUniform3f(uLoc, 0.5, 0.5, 0.5);
    f->glEnableVertexAttribArray(0);
    f->glDrawArrays(GL_LINE_STRIP, 0, m_verticesPrev.size()/3);

    if (m_verticesRef.size() >= 3)
    {
        f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, m_verticesRef.data());
        f->glUniform3f(uLoc, 1.0, 0.0, 0.0);
        f->glEnableVertexAttribArray(0);
        f->glDrawArrays(GL_LINE_STRIP, 0, m_verticesRef.size()/3);
    }

    if (m_vertices.size() >= 3)
    {


        f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, m_vertices.data());
        f->glUniform3f(uLoc, 1.0, 1.0, 1.0);
        f->glEnableVertexAttribArray(0);
        f->glDrawArrays(GL_LINE_STRIP, 0, m_vertices.size()/3);

#ifndef Q_OS_IOS
#ifndef Q_OS_ANDROID
        f->glEnable(GL_PROGRAM_POINT_SIZE);
        f->glEnable(GL_POINT_SMOOTH);
#endif
#endif

        f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, m_vertices.data() + m_vertices.size() - 3);
        f->glUniform3f(uLoc, 1.0, 1.0, 1.0);
        f->glEnableVertexAttribArray(0);
        f->glDrawArrays(GL_POINTS, 0, 1);
    }
    {
        if (m_parent->state()->comparisonLaps.contains(m_parent->target()))
        {
            auto compLap = m_parent->state()->comparisonLaps[m_parent->target()];
            if (compLap->hasClosestPoint)
            {

                //auto startP = m_parent->state()->currentLap->findClosestPoint(compLap->lap->points()[0]).first;
                auto startP = compLap->lap->findClosestPoint(m_parent->state()->currentLap->points()[0]).first;
                //qDebug() << "Last start at = " << startP;
                float lastPoints[3];
                int idx = m_parent->state()->currentLap->points().size() + startP;

                auto lp = compLap->lap->points()[startP];
                //auto lp = last->lap->points()[last->closestPoint];
                lastPoints[0] = lp->position().x();
                lastPoints[1] = lp->position().y();
                lastPoints[2] = lp->position().z();

                /*
                f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, lastPoints);
                f->glUniform3f(uLoc, 0.3, 0.3, 1);
                f->glEnableVertexAttribArray(0);
                f->glDrawArrays(GL_POINTS, 0, 1);
                */

                if (idx >= 0 && idx < compLap->lap->points().size())
                {

                    auto lp = compLap->lap->points()[idx];
                    //auto lp = last->lap->points()[last->closestPoint];
                    lastPoints[0] = lp->position().x();
                    lastPoints[1] = lp->position().y();
                    lastPoints[2] = lp->position().z();

                    f->glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, lastPoints);
                    f->glUniform3f(uLoc, 0.7, 0.3, 0.3);
                    f->glEnableVertexAttribArray(0);
                    f->glDrawArrays(GL_POINTS, 0, 1);
                }
            }
        }
    }
}


static ComponentFactory::RegisterComponent<Map> reg;
