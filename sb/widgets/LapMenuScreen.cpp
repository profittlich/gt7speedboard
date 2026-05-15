#include "LapMenuScreen.h"

#include <QFileDialog>

LapMenuScreen::LapMenuScreen (MainWidget * parent, PDash dash, PState pstate, QString lap) : MenuScreen(parent, dash, pstate), m_lap(lap)
{
    setTitle(lap.toUpper());

    QPushButton * btn;

    addButton("CLEAR", this, &LapMenuScreen::clearClicked);

    if (lap != "ref-a")
    {
        btn = addButton("SAVE AS REF-A", this, &LapMenuScreen::saveAsRefClicked);
        btn->setProperty("target", "ref-a");
    }

    if (lap != "ref-b")
    {
        btn = addButton("SAVE AS REF-B", this, &LapMenuScreen::saveAsRefClicked);
        btn->setProperty("target", "ref-b");
    }

    if (lap != "ref-c")
    {
        btn = addButton("SAVE AS REF-C", this, &LapMenuScreen::saveAsRefClicked);
        btn->setProperty("target", "ref-c");
    }

    addButton("IMPORT", this, &LapMenuScreen::importClicked);
    addButton("EXPORT", this, &LapMenuScreen::exportClicked);

    layout()->insertStretch(layout()->count());
}

void LapMenuScreen::saveAsRefClicked()
{
    DBG_MSG << "save as";
    QString target = sender()->property("target").toString();
    state()->saveComparisonLap(m_lap, target);
    state()->loadComparisonLap(target, target);
    //QFileDialog::getOpenFileName();
    deleteLater();
}

void LapMenuScreen::clearClicked()
{
    DBG_MSG << "clear";
    if (state()->comparisonLaps.contains(m_lap))
    {
        state()->comparisonLaps.remove(m_lap);
    }
    deleteLater();

}

void LapMenuScreen::importClicked()
{
    DBG_MSG << "import";
    auto filePath = QFileDialog::getOpenFileName(this, "Load lap", QString(), "Laps (*.gt7lap; *.gt7track)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Load" << filePath << "as" << m_lap;
        state()->loadComparisonLap(m_lap, filePath, true);
        state()->saveComparisonLap(m_lap, m_lap);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();

}

void LapMenuScreen::exportClicked()
{
    DBG_MSG << "export";
    auto filePath = QFileDialog::getSaveFileName(this, "Save lap", QDate::currentDate().toString("yyyy-MM-dd") + " Reference Lap.gt7lap", "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save" << filePath << "from" << m_lap;
        state()->saveComparisonLap(m_lap, filePath, true);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();

}