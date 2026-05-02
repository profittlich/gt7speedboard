#include "sb/components/LapComparison.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

#include <QVBoxLayout>

QString LapComparison::s_fullScreenTarget;
QList<LapComparison*> LapComparison::s_allLapComparisons;
PComponentParameterFloat LapComparison::s_offset;

LapComparison::LapComparison () : Component(), m_currentTarget (new ComponentParameter<float>("currentTarget",1, true)), m_firstTarget (new ComponentParameter<QString>("target","last", true)), m_secondTarget (new ComponentParameter<QString>("secondTarget","", true)), m_thirdTarget (new ComponentParameter<QString>("thirdTarget","", true))
{
    if (s_offset.isNull())
    {
        s_offset = PComponentParameterFloat( new ComponentParameter<float> ("offset", 0, true));
    }

    addComponentParameter(m_currentTarget);
    addComponentParameter(m_firstTarget);
    addComponentParameter(m_secondTarget);
    addComponentParameter(m_thirdTarget);
    addComponentParameter(s_offset);

    m_colorMapper = new ColorMapperGreenRed(0, 10);
    m_widget = new QWidget();

    m_speed = new ColorLabel(m_widget);
    m_offset = new ColorLabel(m_widget);
    m_time = new GaugeLabel(m_widget, 0, 1, true, true, true);

    m_speed->setAlignment(Qt::AlignCenter);
    QFont font = m_speed->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_speed->setFont(font);
    m_speed->setStyleSheet("color : #fff;font-weight:bold;");

    m_speed->setText((*currentTarget())().toUpper());

    connect(m_speed, &ColorLabel::clicked, this, &LapComparison::goFullscreen);

    m_offset->setAlignment(Qt::AlignCenter);
    font = m_offset->font();
    font.setPointSizeF(baseFontSize() * 2);
    m_offset->setFont(font);
    m_offset->setStyleSheet("color : #fff;font-weight:bold;");

    m_time->setAlignment(Qt::AlignCenter);
    font = m_time->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_time->setFont(font);
    m_time->setStyleSheet("color : #7f7f7f;");

    connect(m_time, &GaugeLabel::clicked, this, &LapComparison::rotateTargets);

    QVBoxLayout * layout = new QVBoxLayout(m_widget);
    layout->setContentsMargins(0,0,0,0);
    layout->addWidget(m_speed);
    layout->addWidget(m_offset);
    layout->addWidget(m_time);
    layout->setStretch(0, 6);
    layout->setStretch(1, 1);
    layout->setStretch(2, 6);

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
        return m_firstTarget;
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
        m_targetLap = state()->comparisonLaps[(*currentTarget())()];
    }
    else
    {
        m_targetLap.clear();
    }

    if (!m_targetLap.isNull() && m_targetLap->hasClosestPoint)
    {
        auto compPt = m_targetLap->lap->points()[m_targetLap->closestPoint];

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

        if (idx >= 0 && m_targetLap->lap->valid())
        {
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
    if ((*s_offset)() == 0)
    {
        m_offset->setText("");
    }
    else
    {
        m_offset->setText(QString((*s_offset)() > 0 ? "+" : "") + QString::number(round((*s_offset)() * 1000.0 / c_FPS)) + " ms");
    }
}

void LapComparison::completedLap(PLap, bool)
{
    updateLabel();
}

void LapComparison::updateLabel()
{
    DBG_MSG << (*currentTarget())();
    DBG_MSG << state().get();
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
    int curPtIdx = m_targetLap->closestPoint + (*s_offset)();
    if (curPtIdx < 0)
    {
        curPtIdx += m_targetLap->lap->points().size();
    }
    else if (curPtIdx >= m_targetLap->lap->points().size())
    {
        curPtIdx -= m_targetLap->lap->points().size();
    }

    auto curPt = m_targetLap->lap->points()[curPtIdx];

    if (curPt->brake() > 2)
    {
        return QColor (0xffff00 - (unsigned (curPt->brake() * 2.55) << 8));
    }

    int nextBrakeIn = m_targetLap->nextBrake - (*s_offset)() - m_targetLap->closestPoint;

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
    result["incOffset"] = { 3, "offset +", "increase the offser for brake point timing"};
    result["decOffset"] = { 4, "offset -", "decrease the offser for brake point timing"};

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
    else if (a == "incOffset")
    {
        (*s_offset)() += 1;
    }
    else if (a == "decOffset")
    {
        (*s_offset)() -= 1;
    }
}

QString LapComparison::componentId ()
{
    return "LapComparison";
}


static ComponentFactory::RegisterComponent<LapComparison> reg(true);