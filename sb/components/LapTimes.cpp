#include "sb/components/LapTimes.h"

#include "sb/components/ComponentFactory.h"

#include <QScroller>
#include <QtWidgets/qboxlayout.h>



LapTimes::LapTimes (const QJsonValue config) : Component(config)
{
    m_widget = new QLabel();

    m_widget->setAlignment(Qt::AlignLeft);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff; padding:10px;");

    m_widget->setText("no times yet");

    m_scroller = new QScrollArea();
    m_scroller->setWidgetResizable(true);
    m_scroller->setWidget(m_widget);

    setupScroller(m_scroller);
}

void LapTimes::setupScroller(QScrollArea *area)
{
    QScroller::grabGesture(area->viewport(), QScroller::LeftMouseButtonGesture);
    QVariant OvershootPolicy = QVariant::fromValue<QScrollerProperties::OvershootPolicy>(QScrollerProperties::OvershootAlwaysOff);
    QScrollerProperties ScrollerProperties = QScroller::scroller(area->viewport())->scrollerProperties();
    ScrollerProperties.setScrollMetric(QScrollerProperties::VerticalOvershootPolicy, OvershootPolicy);
    ScrollerProperties.setScrollMetric(QScrollerProperties::HorizontalOvershootPolicy, OvershootPolicy);
    QScroller::scroller(area->viewport())->setScrollerProperties(ScrollerProperties);
}

QWidget * LapTimes::getWidget() const
{
    //QWidget * temp = new QWidget();
    //temp->setEnabled(false);
    return m_scroller;
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
        if (i == "best"
         || i == "last"
         || i == "median"
         || i == "opt"
         || i == "ref-a"
         || i == "ref-b"
         || i == "ref-c"
        )
        {
            auto lapTime = state()->comparisonLaps[i]->lap->lapTime();

            if (lapTime >= 0)
            {
                txt += i + ": " + msToTime(lapTime)  + "\n";
            }
            else
            {
                lapTime = state()->comparisonLaps[i]->lap->estimateLapTime();
                DBG_MSG << "Got estimated lap time " << lapTime;
                if (lapTime >= 0)
                {
                    txt += i + ": " + msToTime(lapTime)  + " (est.)\n";
                }
                else
                {
                    txt += i + ": N/A\n";
                }
            }
        }
    }
    txt += "\n";
    size_t numLaps = state()->previousLaps.size();
    for (size_t i = 0; i < numLaps; ++i)
    {
        PLap cur = state()->previousLaps[numLaps - i - 1];
        if (cur->points()[0]->currentLap() >= 1)
        {
            auto lapTime = cur->lapTime();
            DBG_MSG << "Got lap time " << lapTime;
            if (lapTime >= 0)
            {
                txt += QString::number (cur->points()[0]->currentLap()) + ": " + msToTime(lapTime);
            }
            else
            {
                lapTime = cur->estimateLapTime();
                if (lapTime >= 0)
                {
                    txt += QString::number (cur->points()[0]->currentLap()) + ": " + msToTime(lapTime);
                }
                else
                {
                    txt += QString::number (cur->points()[0]->currentLap()) + ": N/A";
                }
            }
            if (!cur->valid())
            {
                txt += " <invalid>";
            }
            txt += "\n";
        }
    }
    m_widget->setText(txt);
}


QString LapTimes::description ()
{
    return "Show the lap lap times of comparison laps";
}

QMap<QString, Action> LapTimes::actions ()
{
    return QMap<QString, Action>();
}

QString LapTimes::componentId ()
{
    return "LapTimes";
}


static ComponentFactory::RegisterComponent<LapTimes> reg;

