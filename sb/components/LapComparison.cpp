#include "sb/components/LapComparison.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

#include <QVBoxLayout>



LapComparison::LapComparison (const QJsonValue config) : Component(config), m_target (new ComponentParameter<QString>("target","last", true))
{
    addComponentParameter(m_target);

    m_colorMapper = new ColorMapperGreenRed(0, 10);
    m_widget = new QWidget();

    m_speed = new ColorLabel(m_widget);
    m_time = new GaugeLabel(m_widget, 0, 1, true, true, true);

    m_speed->setAlignment(Qt::AlignCenter);
    QFont font = m_speed->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_speed->setFont(font);
    m_speed->setStyleSheet("color : #fff;");

    m_speed->setText((*m_target)().toUpper());

    m_time->setAlignment(Qt::AlignCenter);
    font = m_time->font();
    font.setPointSizeF(baseFontSize() * 5);
    m_time->setFont(font);
    m_time->setStyleSheet("color : #7f7f7f;");

    QVBoxLayout * layout = new QVBoxLayout(m_widget);
    layout->setContentsMargins(0,0,0,0);
    layout->addWidget(m_speed);
    layout->addWidget(m_time);
}

QWidget * LapComparison::getWidget() const
{
    return m_widget;
}

QString LapComparison::defaultTitle () const
{
    return "COMPARE";
}

void LapComparison::presetSwitched()
{
    m_speed->setText((*m_target)().toUpper());
}

void LapComparison::pointFinished(PTelemetryPoint p)
{
    if (state()->comparisonLaps.contains((*m_target)()))
    {
        m_targetLap = state()->comparisonLaps[(*m_target)()];
    }
    else
    {
        m_targetLap.clear();
    }

    if (!m_targetLap.isNull() && m_targetLap->hasClosestPoint)
    {
        //qDebug() << "Closest: "<< state()->comparisonLaps[(*m_target)()]->closestPoint << "of" << state()->comparisonLaps[(*m_target)()]->lap->points().size();
        auto compPt = m_targetLap->lap->points()[m_targetLap->closestPoint];
        //m_speed->setText (QString::number(round(p->carSpeed() - compPt->carSpeed())));

        m_speed->setColor(m_colorMapper->getColor(compPt->carSpeed() - p->carSpeed()));
        m_speed->update();

        //auto startP = state()->currentLap->findClosestPoint(m_targetLap->lap->points()[0]).first;
        //int idx = state()->currentLap->points().size() - startP;

        int startP = m_targetLap->lap->findClosestPoint(state()->currentLap->points()[0]).first;

        if (startP > m_targetLap->lap->points().size()/2)
        {
            startP -= m_targetLap->lap->points().size();
        }

        int idx = state()->currentLap->points().size() + startP;
        //DBG_MSG << (*m_target)() << "start p:" << startP << idx << m_targetLap->closestPoint << ((int(m_targetLap->closestPoint) - idx) / c_FPS);

        if (idx >= 0 && m_targetLap->lap->valid())
        {
            //qDebug() << "DBG = " << idx << " " << state()->comparisonLaps[(*m_target)()]->closestPoint << " " << (int(state()->comparisonLaps[(*m_target)()]->closestPoint) - idx) * c_FPS / 1000.0;

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

QColor LapComparison::signalColor()
{
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
        return QColor (unsigned (curPt->brake() * 2.55) << 16);
    }
    return QColor();
}

QString LapComparison::description ()
{
    return "Compare current speed and time to another lap";
}

QList<QString> LapComparison::actions ()
{
    return QList<QString>();
}

QString LapComparison::componentId ()
{
    return "LapComparison";
}


static ComponentFactory::RegisterComponent<LapComparison> reg;
