#include "sb/components/LapTimes.h"

#include "sb/components/ComponentFactory.h"

#include <QScroller>
#include <QtWidgets/qboxlayout.h>



LapTimes::LapTimes (const QJsonValue config) : Component(config)
{
    m_scroller = new QScrollArea();
    QVBoxLayout * layout = new QVBoxLayout(m_scroller);

    m_widget = new QLabel();
    layout->addWidget(m_widget);
    //m_scroller->setWidget(m_widget);

    m_widget->setAlignment(Qt::AlignLeft);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff; padding:10px;");

    m_widget->setText("no times yet\nno times yet\nno times yet\nno times yet\nno times yet\nno times yet\nno times yet\nno times yet\nno times yet\nno times yet\n");

    //setupScroller(m_scroller);
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
