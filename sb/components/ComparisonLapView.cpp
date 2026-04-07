#include "sb/components/ComparisonLapView.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"

ComparisonLapView::ComparisonLapView () : Component()
{
    m_scrollWidget = new QScrollArea();
    m_widget = new ColorLabel(m_scrollWidget);

    m_widget->setAlignment(Qt::AlignLeft);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 1.3);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("");
    //m_widget->setMinimumHeight(100);
    //m_widget->setMinimumWidth(200);
    m_scrollWidget->setWidget(m_widget);
    m_scrollWidget->setStyleSheet("background-color : " + g_globalConfiguration.backgroundColor().name() + ";");
}

QWidget * ComparisonLapView::getWidget() const
{
    return m_scrollWidget;
}

QString ComparisonLapView::defaultTitle () const
{
    return "Comp Laps";
}

void ComparisonLapView::newPoint(PTelemetryPoint p)
{
}

void ComparisonLapView::completedLap(PLap lastLap, bool isFullLap)
{
    QString txt = "";
    txt +=  "lastLap: " + QString::number(lastLap->points().size()) + " points, " + (lastLap->valid() ? "valid" : "invalid") + "\n";
    for (auto i : state()->comparisonLaps.keys())
    {
        auto l = state()->comparisonLaps[i];
        txt += i + ": " + QString::number(l->lap->points().size()) + " points, " + (l->lap->valid() ? "valid" : "invalid") + "\n";
    }
    m_widget->setText(m_widget->text() + "\nLap: " + QString::number(lastLap->points()[0]->currentLap()) + "\n" + txt);
    m_widget->adjustSize();
}

void ComparisonLapView::newSession()
{
    m_widget->setText(m_widget->text() + "\nNew session");
    m_widget->adjustSize();
}


void ComparisonLapView::pitStop()
{
    m_widget->setText(m_widget->text() + "\nPit stop");
    m_widget->adjustSize();

}

void ComparisonLapView::newTrack(PTrack track)
{
    m_widget->setText(m_widget->text() + "\nNew track");
    m_widget->adjustSize();

}

void ComparisonLapView::maybeNewTrack(PTrack track)
{
    m_widget->setText(m_widget->text() + "\nMaybe new track ");

}

void ComparisonLapView::leftTrack()
{
    m_widget->setText(m_widget->text() + "\nLeft track");
    m_widget->adjustSize();

}


QString ComparisonLapView::description ()
{
    return "List comparison laps for debugging purposes";
}

QMap<QString, Action> ComparisonLapView::actions ()
{
    return QMap<QString, Action>();
}

QString ComparisonLapView::componentId ()
{
    return "ComparisonLapView";
}

static ComponentFactory::RegisterComponent<ComparisonLapView> reg;
