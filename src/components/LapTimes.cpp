#include "src/components/LapTimes.h"

#include "src/components/ComponentFactory.h"
#include "src/cardata/TelemetryPointGT7.h"

#include <QScroller>
#include <QtWidgets/qboxlayout.h>
#include <QFileDialog>



LapTimes::LapTimes () : Component()
{
    m_widget = new QLabel();

    m_widget->setTextFormat(Qt::TextFormat::RichText);
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

void LapTimes::completedLap(PLap lap, bool)
{
    QString txt = "";
    for (auto i : state()->comparisonLaps.keys())
    {
        if (!state()->invisibleComparisonLaps.contains(i))
        {
            auto lapTime = state()->comparisonLaps[i]->lap->lapTime();

            if (lapTime >= 0)
            {
                txt += i + ": " + msToTime(lapTime);
            }
            else
            {
                lapTime = state()->comparisonLaps[i]->lap->estimateLapTime();
                DBG_MSG << "Got estimated lap time " << lapTime;
                if (lapTime >= 0)
                {
                    txt += i + ": " + msToTime(lapTime)  + " (est.)";
                }
                else
                {
                    txt += i + ": N/A";
                }
            }
            PTelemetryPointGT7 pgt7 = state()->comparisonLaps[i]->lap->points()[0].dynamicCast<TelemetryPointGT7>();
            QString carName = "unknown car";
            if (!pgt7.isNull())
            {
                carName = g_globalConfiguration.carName(pgt7->carID());
            }
            txt += " <font color=\"gray\">(" + state()->comparisonLaps[i]->lap->trackName() + ", " + carName + ")</font><br>";
        }
    }
    txt += "<br>";
    size_t numLaps = state()->previousLaps.size();
    for (size_t i = 0; i < numLaps; ++i)
    {
        PLap cur = state()->previousLaps[numLaps - i - 1];
        if (cur->points()[0]->currentLap() >= 1)
        {
            auto lapTime = cur->lapTime();
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
            PTelemetryPointGT7 pgt7 = lap->points()[0].dynamicCast<TelemetryPointGT7>();
            QString carName = "unknown car";
            if (!pgt7.isNull())
            {
                carName = g_globalConfiguration.carName(pgt7->carID());
            }
            txt += " <font color=\"gray\">(" + cur->trackName(true) + ", " + carName + ")</font>";
            txt += "<br>";
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
    QMap<QString, Action> result;

    result["exportCSV"] = { 1, "export CSV", "export listed lap times to a CSV file"};

    return result;
}

void LapTimes::callAction(QString a)
{
    if (a == "exportCSV")
    {
        exportCSV();
    }
}

void LapTimes::exportCSV()
{
    QString trackName = state()->currentLap->trackName(true);
    if (trackName.isNull())
    {
        trackName = "";
    }
    else
    {
        trackName = " - " + trackName + " -";
    }
    QString filename = QDate::currentDate().toString("yyyy-MM-dd") + " " + QTime::currentTime().toString("HHmm") + "h" + trackName +  " lap times.csv";
    auto filePath = QFileDialog::getSaveFileName(nullptr, "Save lap times", filename, "CSV (*.csv)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save lap times to" << filePath;
        QFile f(filePath);
        f.open(QFile::WriteOnly);
        if (f.isOpen())
        {
            f.write("Index\tLap\tms\tTime\tValid\tTrack\tCar\n");
            DBG_MSG << "write data";
            size_t numLaps = state()->previousLaps.size();
            for (size_t i = 0; i < numLaps; ++i)
            {
                PLap cur = state()->previousLaps[i];
                if (cur->points()[0]->currentLap() == 0)
                {
                    continue;
                }
                QString lapTimeStr = "";
                if (cur->lapTime() != -1)
                {
                    lapTimeStr = msToTime(cur->lapTime());
                }
                PTelemetryPointGT7 pgt7 = cur->points()[0].dynamicCast<TelemetryPointGT7>();
                QString carName = "unknown car";
                if (!pgt7.isNull())
                {
                    carName = g_globalConfiguration.carName(pgt7->carID());
                }
                f.write(QString(
                    QString::number(i) + "\t" +
                    QString::number(cur->points()[0]->currentLap()) + "\t" +
                    QString::number(cur->lapTime()) + "\t" +
                    lapTimeStr + "\t" +
                    (cur->valid() ? "1" : "0") + "\t" +
                    cur->trackName(true) + "\t" +
                    carName +
                    "\n"
                    ).toStdString().c_str());
            }

            f.close();
        }
        else
        {
            DBG_MSG << "Could not open" << filePath;
        }

    }
    else
    {
        DBG_MSG << "No file selected";
    }
}

QString LapTimes::componentId ()
{
    return "LapTimes";
}


static ComponentFactory::RegisterComponent<LapTimes> reg(true);

