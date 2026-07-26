#include "src/components/BrakeBoard.h"

#include "src/components/ComponentFactory.h"
#include "src/system/Configuration.h"
#include "src/widgets/ColorLabel.h"
#include "src/widgets/GaugeLabel.h"
#include <QtWidgets/qgridlayout.h>
#include <numeric>
#include <algorithm>

BrakeBoard::BrakeBoard () : Component(), m_difficulty (new ComponentParameter<int>("difficulty",0, true)), m_mode (new ComponentParameter<int>("mode",0, true))
{
    addComponentParameter(m_difficulty);
    addComponentParameter(m_mode);

    m_widget = new QWidget();
    m_widget->setStyleSheet("color : #fff;");
    auto * layout = new QGridLayout(m_widget);
    layout->setContentsMargins(0,0,0,0);

    m_topLabel = new ColorLabel(m_widget);
    m_topLabel->setAlignment(Qt::AlignmentFlag::AlignCenter);
    m_topLabel->setAutoFillBackground(true);
    auto font = m_topLabel->font();
    font.setPointSizeF(baseFontSize() * 6);
    font.setBold(true);
    m_topLabel->setFont(font);

    m_mainLabel = new ColorLabel(m_widget);
    m_mainLabel->setAlignment(Qt::AlignmentFlag::AlignCenter);
    m_mainLabel->setAutoFillBackground(true);
    font = m_mainLabel->font();
    font.setPointSizeF(baseFontSize() * 20);
    font.setBold(true);
    m_mainLabel->setFont(font);

    m_bottomLabel = new ColorLabel(m_widget);
    m_bottomLabel->setAlignment(Qt::AlignmentFlag::AlignCenter);
    m_bottomLabel->setAutoFillBackground(true);
    font = m_bottomLabel->font();
    font.setPointSizeF(baseFontSize() * 5);
    font.setBold(true);
    m_bottomLabel->setFont(font);

    m_deviation = new GaugeLabel(m_widget, 0, 20, true, false);
    m_deviation->setBarColors(0xffff00, 0xffff00);

    layout->addWidget(m_topLabel, 0, 0);
    layout->addWidget(m_mainLabel, 1, 0, 3, 1);
    layout->addWidget(m_bottomLabel, 5, 0);
    layout->addWidget(m_deviation, 6, 0);

    //updateLabels();

    m_brakeTargetLevel = QRandomGenerator::global()->bounded(1,4) * 25;
    m_brakeFromFull = QRandomGenerator::global()->bounded(0,2) == 1;
    DBG_MSG << m_brakeFromFull;

    updateDifficulty();
    updateMode();
}

void BrakeBoard::updateLabels()
{
    /*QString arrow = "\u2197";
    if (m_brakeFromFull)
    {
        arrow = "\u2198";
    }
    m_mainLabel->setText(QString("%1 %2%").arg(arrow).arg(m_brakeTargetLevel));
    if (m_brakeFromFull)
    {
        m_bottomLabel->setText(QString("PRESS THE BRAKE PEDAL FULLY, THEN GO BACK TO %1% AND HOLD").arg(m_brakeTargetLevel));
    }
    else
    {
        m_bottomLabel->setText(QString("PRESS THE BRAKE PEDAL TO %1% AND HOLD").arg(m_brakeTargetLevel));
    }*/
}

void BrakeBoard::cycleDifficulty()
{
    m_difficulty() += 1;
    if (m_difficulty() >= m_difficultyNames.size())
    {
        m_difficulty() = 0;
    }
    updateDifficulty();
    updateMode();
}

void BrakeBoard::cycleModes()
{
    if (m_mode() == 1)
    {
        m_mode() = 0;
    }
    else
    {
        m_mode() = 1;
    }
    updateMode();
}

void BrakeBoard::updateDifficulty()
{
    switch (m_difficulty())
    {
    case 0:
        m_brakeHoldTime = 60;
        m_brakeHoldCorridor = 5;
        m_brakeLevelTolerance = 12;
        m_brakeTimingTolerance = 80;
        break;
    case 1:
        m_brakeHoldTime = 30;
        m_brakeHoldCorridor = 5;
        m_brakeLevelTolerance = 8;
        m_brakeTimingTolerance = 40;
        break;
    case 2:
        m_brakeHoldTime = 30;
        m_brakeHoldCorridor = 5;
        m_brakeLevelTolerance = 4;
        m_brakeTimingTolerance = 20;
        break;
    case 3:
        m_brakeHoldTime = 15;
        m_brakeHoldCorridor = 5;
        m_brakeLevelTolerance = 1;
        m_brakeTimingTolerance = 10;
        break;
    }
}

void BrakeBoard::updateMode()
{
    m_state = Begin;
    DBG_MSG << m_mode() << m_brakeTargetLevel << m_brakeFromFull << "XXXXXXXXXXXXXXXX";

    switch (m_mode())
    {
    case 0:
        m_topLabel->setText("MODE: BRAKE LEVEL, " + m_difficultyNames[m_difficulty()]);
        if (m_brakeFromFull)
        {
            m_mainLabel->setText("\u2198 " + QString::number(m_brakeTargetLevel) + "%");
            m_bottomLabel->setText("PRESS THE BRAKE PEDAL FULLY, THEN GO BACK TO " + QString::number(m_brakeTargetLevel) + "%" + " AND HOLD");
        } else {
            m_mainLabel->setText("\u2197 " + QString::number(m_brakeTargetLevel) + "%");
            m_bottomLabel->setText("PRESS THE BRAKE PEDAL TO " + QString::number(m_brakeTargetLevel) + "%" + " AND HOLD");
        }

        m_prevBrakes.clear();
        m_deviation->setSpread(5 * m_brakeLevelTolerance);
        //m_deviation->setColorScaleMode(1, m_brakeLevelTolerance, 3 * m_brakeLevelTolerance);
        break;
    case 1:
        m_topLabel->setText("MODE: BRAKE TIMING, " + m_difficultyNames[m_difficulty()]);
        m_bottomLabel->setText("PRESS THE BRAKE PEDAL AT THE RIGHT TIME");
        m_mainLabel->setText("WAIT");
        m_startTime = QTime::currentTime();
        m_delayTime = QRandomGenerator::global()->bounded(1000,5001);
        m_deviation->setSpread(10 * m_brakeTimingTolerance);
        //m_deviation->setColorScaleMode(1, m_brakeTimingTolerance, 3 * m_brakeTimingTolerance);
        break;
    }
}

QWidget * BrakeBoard::getWidget() const
{
    return m_widget;
}

QString BrakeBoard::defaultTitle () const
{
    return "BrakeBoard";
}

void BrakeBoard::newPoint(PTelemetryPoint p)
{
    switch (m_mode())
    {
    case 0:
        brakeTarget(p);
        break;
    case 1:
        brakeTiming(p);
        break;
    }
}

void BrakeBoard::parameterChanged(const PComponentParameterInt &)
{
    updateDifficulty();
    updateMode();
}

void BrakeBoard::brakeTarget(PTelemetryPoint p)
{
    switch (m_state)
    {
    case Begin:
        if (!m_brakeFromFull && p->brake() > 2) // todo: global constant
        {
            DBG_MSG << "Begin --> Braking";
            m_state = Braking;
            m_prevBrakes.append(p->brake());
        }
        else if (m_brakeFromFull && p->brake() == 100)
        {
            DBG_MSG << "Begin --> BrakingFull";
            m_state = BrakingFull;
            m_bottomLabel->setText("GO BACK TO " + QString::number(m_brakeTargetLevel) + "%" + " AND HOLD");
        }
        break;
    case BrakingFull:
        if (p->brake() < 98)
        {
            DBG_MSG << "BrakingFull --> Braking";
            m_state = Braking;
            m_prevBrakes.append(p->brake());
        }
        break;
    case Braking:
        m_prevBrakes.append(p->brake());
        if (m_prevBrakes.size() > m_brakeHoldTime)
        {
            m_prevBrakes = m_prevBrakes.last(m_brakeHoldTime);
        }
        DBG_MSG << p->brake() << m_prevBrakes.size() << m_brakeHoldTime << "MAXMIN" << *std::max_element(m_prevBrakes.begin(), m_prevBrakes.end()) << *std::min_element(m_prevBrakes.begin(), m_prevBrakes.end());
        if (std::accumulate(m_prevBrakes.begin(), m_prevBrakes.end(), 0)/m_prevBrakes.size() < 2)
        {
            m_state = Begin;
            DBG_MSG << "Braking --> Begin";
            if (m_brakeFromFull)
            {
                m_bottomLabel->setText("PRESS THE BRAKE PEDAL FULLY, THEN GO BACK TO " + QString::number(m_brakeTargetLevel) + "%" + " AND HOLD");
            }
        }
        else if (m_prevBrakes.size() == m_brakeHoldTime && abs(*std::max_element(m_prevBrakes.begin(), m_prevBrakes.end()) - *std::min_element(m_prevBrakes.begin(), m_prevBrakes.end())) < m_brakeHoldCorridor)
        {
            m_state = BrakeLevelReached;
            DBG_MSG << "Braking --> BrakeLevelReached";
            auto lastBrakes = m_prevBrakes.last(3);
            m_deviation->setValue(m_brakeTargetLevel - round(std::accumulate(lastBrakes.begin(), lastBrakes.end(), 0)/lastBrakes.size()));
            m_deviation->update();
        }

        break;
    case BrakeLevelReached:
        if (p->brake() < 2)
        {
            DBG_MSG << "BrakeLevelReached --> Begin";
            m_state = Begin;
            m_prevBrakes.clear();

            m_brakeTargetLevel = QRandomGenerator::global()->bounded(1,4) * 25;
            m_brakeFromFull = QRandomGenerator::global()->bounded(0,2) == 1;
            DBG_MSG << m_brakeFromFull;
            if (m_brakeFromFull)
            {
                m_mainLabel->setText("\u2198 " + QString::number(m_brakeTargetLevel) + "%");
                m_bottomLabel->setText("PRESS THE BRAKE PEDAL FULLY, THEN GO BACK TO " + QString::number(m_brakeTargetLevel) + "%" + " AND HOLD");
            } else {
                m_mainLabel->setText("\u2197 " + QString::number(m_brakeTargetLevel) + "%");
                m_bottomLabel->setText("PRESS THE BRAKE PEDAL TO " + QString::number(m_brakeTargetLevel) + "%" + " AND HOLD");
            }
            m_deviation->setValue(0);
            m_deviation->update();
        } else {
            auto lastBrakes = m_prevBrakes.last(3);
            auto avgBrake = std::accumulate(lastBrakes.begin(), lastBrakes.end(), 0) / lastBrakes.size();
            if ((m_brakeTargetLevel - avgBrake) >= m_brakeLevelTolerance)
            {
                m_mainLabel->setText("TOO SOFT");
            }
            else if ((m_brakeTargetLevel - avgBrake) <= -m_brakeLevelTolerance)
            {
                m_mainLabel->setText("TOO HARD");
            }
            else if (round(m_brakeTargetLevel - avgBrake) > 0)
            {
                m_mainLabel->setText("GOOD");
            }
            else if (round(m_brakeTargetLevel - avgBrake) < 0)
            {
                m_mainLabel->setText("GOOD");
            }
            else
            {
                m_mainLabel->setText("PERFECT");
            }
            m_bottomLabel->setText(QString::number (round(avgBrake)) + "% vs " + QString::number(m_brakeTargetLevel) + "%");

        }
        break;
    default:
        DBG_MSG << "Invalid state for target mode:" << m_state;
        m_state = Begin;
        break;
    }
}




void BrakeBoard::brakeTiming(PTelemetryPoint p)
{
    QTime now = QTime::currentTime();
    if (m_state != Begin && p->brake() > c_brakeMinimumLevel && m_brakeDownTime.isNull())
    {
        DBG_MSG << "Init Braking Time";
        m_brakeDownTime = now;
    }

    auto elapsed = m_startTime.msecsTo(now);
    int brakeElapsed;

    switch (m_state)
    {
    case Begin:
        if (elapsed >= m_delayTime)
        {
            DBG_MSG << "Begin --> Countdown3";
            m_state = Countdown3;
            m_startTime = now;
            m_mainLabel->setText("3");
            m_mainLabel->setColor(QColor(0x0000ff));
        }
        break;
    case Countdown3:
        if (elapsed >= 1000)
        {
            DBG_MSG << "Countdown3 --> Countdown2";
            m_state = Countdown2;
            m_startTime = now;
            m_mainLabel->setText("2");
            m_mainLabel->setColor(QColor(0x7f7fff));
        }
        else if (elapsed >= 500)
        {
            m_mainLabel->setColor(g_globalConfiguration.backgroundColor());
            m_mainLabel->update();
        }
        break;
    case Countdown2:
        if (elapsed >= 1000)
        {
            DBG_MSG << "Countdown2 --> Countdown1";
            m_state = Countdown1;
            m_startTime = now;
            m_mainLabel->setText("1");
            m_mainLabel->setStyleSheet("color:black;");
            m_mainLabel->setColor(QColor(0xffffff));
        }
        else if (elapsed >= 500)
        {
            m_mainLabel->setColor(g_globalConfiguration.backgroundColor());
            m_mainLabel->setStyleSheet("");
            m_mainLabel->update();
        }
        break;
    case Countdown1:
        if (elapsed >= 1000)
        {
            DBG_MSG << "Countdown1 --> BrakePoint";
            m_state = BrakePoint;
            m_targetTime = m_startTime = now;
            m_mainLabel->setText("BRAKE!");
            m_mainLabel->setStyleSheet("");
            m_mainLabel->setColor(g_globalConfiguration.backgroundColor());
        }
        else if (elapsed >= 750)
        {
            m_mainLabel->setColor(g_globalConfiguration.backgroundColor());
            m_mainLabel->setStyleSheet("");
            m_mainLabel->update();
        }
        else if (elapsed >= 500)
        {
            m_mainLabel->setColor(QColor(0xffffff));
            m_mainLabel->setStyleSheet("color:black;");
            m_mainLabel->update();
        }
        else if (elapsed >= 250)
        {
            m_mainLabel->setColor(g_globalConfiguration.backgroundColor());
            m_mainLabel->setStyleSheet("");
            m_mainLabel->update();
        }
        break;
    case BrakePoint:
        if (elapsed >= 3000 || !m_brakeDownTime.isNull())
        {
            DBG_MSG << "BrakePoint --> Result";
            m_mainLabel->setStyleSheet("");
            m_state = Result;
            m_startTime = now;

            if (!m_brakeDownTime.isNull())
            {
                brakeElapsed = m_brakeDownTime.msecsTo(m_targetTime);
            }
            DBG_MSG << brakeElapsed << elapsed << m_brakeDownTime << m_brakeTimingTolerance;
            if (m_brakeDownTime.isNull())
            {
                m_mainLabel->setText("MISS!");
                m_deviation->setValue(1000);
                m_deviation->update();
            }
            else if (brakeElapsed < -m_brakeTimingTolerance)
            {
                m_mainLabel->setText("LATE");
                m_bottomLabel->setText(QString::number(-brakeElapsed) + "ms");
                m_deviation->setValue(-brakeElapsed);
                m_deviation->update();
            }
            else if (brakeElapsed > m_brakeTimingTolerance)
            {
                m_mainLabel->setText("EARLY");
                m_bottomLabel->setText(QString::number(-brakeElapsed) + "ms");
                m_deviation->setValue(-brakeElapsed);
                m_deviation->update();
            }
            else if (brakeElapsed < -10.0)
            {
                DBG_MSG << brakeElapsed << m_brakeTimingTolerance;
                m_mainLabel->setText("GOOD");
                m_bottomLabel->setText(QString::number(-brakeElapsed) + "ms");
                m_deviation->setValue(-brakeElapsed);
                m_deviation->update();
            }
            else if (brakeElapsed > 10.0)
            {
                m_mainLabel->setText("GOOD");
                DBG_MSG << brakeElapsed << m_brakeTimingTolerance;
                m_bottomLabel->setText(QString::number(-brakeElapsed) + "ms");
                m_deviation->setValue(-brakeElapsed);
                m_deviation->update();
            }
            else
            {
                m_mainLabel->setText("PERFECT!");
                m_deviation->setValue(0);
                m_deviation->update();
            }
        }
        break;
    case Result:
        if (elapsed >= 3000)
        {
            DBG_MSG << "Result --> Begin";
            m_state = Begin;
            m_startTime = now;
            m_brakeDownTime = QTime();
            m_mainLabel->setText("WAIT");
            m_bottomLabel->setText("PRESS THE BRAKE PEDAL AT THE RIGHT TIME");
            m_delayTime = QRandomGenerator::global()->bounded(1000,5001);
            m_deviation->setValue(0);
            m_deviation->update();
        }
        break;
    default:
        DBG_MSG << "Invalid state for timing mode:" << m_state;
        m_state = Begin;
        break;
    }
}

void BrakeBoard::callAction(QString a)
{
    if (a == "cycleMode")
    {
        cycleModes();
    }
    else if (a == "cycleDifficulty")
    {
        cycleDifficulty();
    }
}

QString BrakeBoard::description ()
{
    return "BrakeBoard braking coach";
}

QMap<QString, Action> BrakeBoard::actions ()
{
    QMap<QString, Action> result;

    result["cycleMode"] = { 1, "next mode", "select the next BrakeBoard mode"};
    result["cycleDifficulty"] = { 2, "next difficulty", "cycle through difficulty levels"};

    return result;
}

QString BrakeBoard::componentId ()
{
    return "BrakeBoard";
}

static ComponentFactory::RegisterComponent<BrakeBoard> reg(true);
