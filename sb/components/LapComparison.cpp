#include "sb/components/LapComparison.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

#include <QVBoxLayout>

QString LapComparison::s_fullScreenTarget;
QList<LapComparison*> LapComparison::s_allLapComparisons;

LapComparison::LapComparison (const QJsonValue config) : Component(config), m_currentTarget (new ComponentParameter<float>("currentTarget",1, true)), m_target (new ComponentParameter<QString>("target","last", true)), m_secondTarget (new ComponentParameter<QString>("secondTarget","", true)), m_thirdTarget (new ComponentParameter<QString>("thirdTarget","", true))
{
    addComponentParameter(m_currentTarget);
    addComponentParameter(m_target);
    addComponentParameter(m_secondTarget);
    addComponentParameter(m_thirdTarget);

    m_colorMapper = new ColorMapperGreenRed(0, 10);
    m_widget = new QWidget();

    m_speed = new ColorLabel(m_widget);
    m_time = new GaugeLabel(m_widget, 0, 1, true, true, true);

    m_speed->setAlignment(Qt::AlignCenter);
    QFont font = m_speed->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_speed->setFont(font);
    m_speed->setStyleSheet("color : #fff;font-weight:bold;");

    m_speed->setText((*currentTarget())().toUpper());

    connect(m_speed, &ColorLabel::clicked, this, &LapComparison::goFullscreen);

    m_time->setAlignment(Qt::AlignCenter);
    font = m_time->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_time->setFont(font);
    m_time->setStyleSheet("color : #7f7f7f;");

    connect(m_time, &GaugeLabel::clicked, this, &LapComparison::rotateTargets);

    QVBoxLayout * layout = new QVBoxLayout(m_widget);
    layout->setContentsMargins(0,0,0,0);
    layout->addWidget(m_speed);
    layout->addWidget(m_time);

    s_allLapComparisons.append(this);
}

LapComparison::~LapComparison()
{
    s_allLapComparisons.removeAll(this);
}

QWidget * LapComparison::getWidget() const
{
    return m_widget;
}

PComponentParameterString LapComparison::currentTarget()
{
    if ((*m_currentTarget)() > 2.5)
    {
        return m_thirdTarget;
    }
    else if ((*m_currentTarget)() > 1.5)
    {
        return m_secondTarget;
    }
    else
    {
        return m_target;
    }
}

QString LapComparison::defaultTitle () const
{
    return "COMPARE";
}

void LapComparison::presetSwitched()
{
    m_speed->setText((*currentTarget())().toUpper());
}

void LapComparison::goFullscreen()
{
    DBG_MSG << "toggleFullscreen click";
    callAction("toggleFullscreen");
}


void LapComparison::rotateTargets()
{
    DBG_MSG << "rotateTargets click";
    callAction("nextTarget");
}

void LapComparison::pointFinished(PTelemetryPoint p)
{
    if (canFullScreenSignal() && s_fullScreenTarget == "")
    {
        s_fullScreenTarget = (*currentTarget())();
        DBG_MSG << "Init global target" << s_fullScreenTarget;
    }
    if ((canFullScreenSignal() && s_fullScreenTarget == (*currentTarget())()) != m_prevFullScreenPermission)
    {
        m_prevFullScreenPermission = (canFullScreenSignal() && s_fullScreenTarget == (*currentTarget())());
        if (s_fullScreenTarget == (*currentTarget())())
        {
            DBG_MSG << "Underline" << (*currentTarget())();
            m_speed->setStyleSheet("color : #fff;font-weight:bold;text-decoration:underline;");
        }
        else
        {
            DBG_MSG << "No underline" << (*currentTarget())();
            m_speed->setStyleSheet("color : #fff;font-weight:bold;");
        }
    }
    if (state()->comparisonLaps.contains((*currentTarget())()))
    {
        m_targetLap = state()->comparisonLaps[(*m_target)()];
    }
    else
    {
        m_targetLap.clear();
    }

    if (!m_targetLap.isNull() && m_targetLap->hasClosestPoint)
    {
        //qDebug() << "Closest: "<< state()->comparisonLaps[(*m_target)()]->closestPoint << "of" << state()->comparisonLaps[(*currentTarget())()]->lap->points().size();
        auto compPt = m_targetLap->lap->points()[m_targetLap->closestPoint];
        //m_speed->setText (QString::number(round(p->carSpeed() - compPt->carSpeed())));

        m_speed->setColor(m_colorMapper->getColor(compPt->carSpeed() - p->carSpeed()));
        m_speed->update();

        //auto startP = state()->currentLap->findClosestPoint(m_targetLap->lap->points()[0]).first;
        //int idx = state()->currentLap->points().size() - startP;

        //DBG_MSG << "findClosest";
        int startP = 0;//m_targetLap->lap->findClosestPoint(state()->currentLap->points()[0]).first;

        //if (startP > m_targetLap->lap->points().size()/2)
        //{
        //    startP -= m_targetLap->lap->points().size();
        //}

        int idx = state()->currentLap->points().size() + startP;
        //DBG_MSG << (*m_target)() << "start p:" << startP << idx << m_targetLap->closestPoint << ((int(m_targetLap->closestPoint) - idx) / c_FPS);

        if (idx >= 0 && m_targetLap->lap->valid())
        {
            //qDebug() << "DBG = " << idx << " " << state()->comparisonLaps[(*m_target)()]->closestPoint << " " << (int(state()->comparisonLaps[(*currentTarget())()]->closestPoint) - idx) * c_FPS / 1000.0;

            m_time->setValue((int(m_targetLap->closestPoint) - idx) / c_FPS);
        }
        else
        {
            m_time->disable();
        }

    }
    else
    {
        //m_speed->setText ("");
        m_speed->setColor(g_globalConfiguration.backgroundColor());
        m_time->disable();
    }
    m_time->update();
}

void LapComparison::completedLap(PLap, bool)
{
    updateLabel();
}

void LapComparison::updateLabel()
{
    DBG_MSG << (*currentTarget())();
    if (state()->comparisonLaps.contains((*currentTarget())()))
    {
        if (state()->comparisonLaps[(*currentTarget())()]->lap->valid())
        {
            m_speed->setText((*currentTarget())().toUpper());
        }
        else
        {
            m_speed->setText("(" + (*currentTarget())().toUpper() + ")");
        }
    }
    else
    {
        m_speed->setText( (*currentTarget())().toUpper());
        m_speed->setColor(g_globalConfiguration.backgroundColor());
    }
    if (s_fullScreenTarget == (*currentTarget())())
    {
        DBG_MSG << "Underline" << (*currentTarget())();
        m_speed->setStyleSheet("color : #fff;font-weight:bold;text-decoration:underline;");
        for (auto d : s_allLapComparisons)
        {
            if (d != this) {
                d->m_speed->setStyleSheet("color : #fff;font-weight:bold;");
            }
        }
    }
    else
    {
        DBG_MSG << "No underline" << (*currentTarget())();
        m_speed->setStyleSheet("color : #fff;font-weight:bold;");
    }
}

QColor LapComparison::signalColor() const
{
    if (!m_prevFullScreenPermission)
    {
        return QColor();
    }
    if (m_targetLap.isNull() || !m_targetLap->hasClosestPoint)
    {
        return QColor();
    }
    size_t nextBrakeIn = m_targetLap->nextBrake - m_targetLap->closestPoint;
    auto curPt = m_targetLap->lap->points()[m_targetLap->closestPoint];
    if (nextBrakeIn > 15 && nextBrakeIn <= 30)
    {
        return QColor (0xffffff);
    }
    if (nextBrakeIn > 45 && nextBrakeIn <= 60)
    {
        return QColor (0xffffff);
    }
    if (nextBrakeIn > 90 && nextBrakeIn <= 120)
    {
        return QColor (0x7f7fff);
    }
    if (nextBrakeIn > 150 && nextBrakeIn <= 180)
    {
        return QColor (0x0000ff);
    }
    if (curPt->brake() > 2)
    {
        return QColor (0xffff00 - (unsigned (curPt->brake() * 2.55) << 8));
    }
    return QColor();
}

QString LapComparison::description ()
{
    return "Compare current speed and time to another lap";
}

QMap<QString, Action> LapComparison::actions ()
{
    QMap<QString, Action> result;

    result["toggleFullscreen"] = { 1, "toggle fullscreen signal", "toggle wether the signalling of countdowns and positions should color the full screen"};
    result["nextTarget"] = { 2, "next target", "switch to the next configured comparison target lap"};

    return result;
}

void LapComparison::callAction(QString a)
{
    if (a == "toggleFullscreen")
    {
        if (s_fullScreenTarget == (*currentTarget())())
        {
            DBG_MSG << "No target" << m_prevFullScreenPermission;
            s_fullScreenTarget = "<none>";
        }
        else
        {
            DBG_MSG << "Target" << (*currentTarget())() << m_prevFullScreenPermission;
            s_fullScreenTarget = (*currentTarget())();
        }
        updateLabel();
    }
    else if (a == "nextTarget")
    {
        DBG_MSG << "next target";
        (*m_currentTarget)() += 1.0;

        if ((*m_currentTarget)() > 3.5)
        {
            (*m_currentTarget)() = 1.0;
        }

        if ((*currentTarget())() == "")
        {
            (*m_currentTarget)() += 1.0;
            if ((*m_currentTarget)() > 3.5)
            {
                (*m_currentTarget)() = 1.0;
            }
        }

        if ((*currentTarget())() == "")
        {
            (*m_currentTarget)() += 1.0;
            if ((*m_currentTarget)() > 3.5)
            {
                (*m_currentTarget)() = 1.0;
            }
        }

        updateLabel();

        DBG_MSG << currentTarget()->name();
    }
}

QString LapComparison::componentId ()
{
    return "LapComparison";
}


static ComponentFactory::RegisterComponent<LapComparison> reg;