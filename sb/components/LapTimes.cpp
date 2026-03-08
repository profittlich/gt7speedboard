#include "sb/components/LapTimes.h"

#include "sb/components/ComponentFactory.h"



LapTimes::LapTimes (const QJsonValue config) : Component(config)
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignLeft);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff; padding:10px;");

    m_widget->setText("no times yet");
}

QWidget * LapTimes::getWidget() const
{
    return m_widget;
}

QString LapTimes::defaultTitle () const
{
    return "Times";
}

void LapTimes::completedLap(PLap, bool)
{
    QString txt = "";
    for (auto i : state()->comparisonLaps.keys())
    {
        txt += i + ": " + msToTime(state()->comparisonLaps[i]->lapTime) + " (" + QString::number(state()->comparisonLaps[i]->lapTime) + " ms)\n";
    }
    m_widget->setText(txt);
}


QString LapTimes::description ()
{
    return "Show the lap lap times of comparison laps";
}

QList<QString> LapTimes::actions ()
{
    return QList<QString>();
}

QString LapTimes::componentId ()
{
    return "LapTimes";
}


static ComponentFactory::RegisterComponent<LapTimes> reg;
