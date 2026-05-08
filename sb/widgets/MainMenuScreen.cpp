#include "MainMenuScreen.h"
#include "sb/widgets/DashWidget.h"
#include <QFileDialog>

/*
 *  Menu structure
 *
 *  next page
 *  prev page
 *  RESET DATA
 *  laps
 *      REF-A
 *          CLEAR REF-A
 *          SAVE BEST AS REF-A
 *          save opt as ref-a
 *          IMPORT REF-A
 *          EXPORT REF-A
 *      ref-b
 *      ref-c
 *      best
 *          export best lap
 *      opt
 *          export opt lap
 *      last
 *          export last lap
 *      all
 *          export all laps
 *  layout
 *      save layout
 *      save layout as
 *      export layout
 *      import layout
 *  EXIT DASH
 *
 */

// Main menu
MainMenuScreen::MainMenuScreen (MainWidget * parent, PDash dash, PState pstate) : MenuScreen(parent, dash, pstate)
{
    addButton ("RESET DATA", this, &MainMenuScreen::resetClicked);

    if (state()->comparisonLaps.contains("ref-a"))
    {
        addButton("CLEAR REF-A", this, &MainMenuScreen::clearRefAClicked);
    }

    if (state()->comparisonLaps.contains("best"))
    {
        addButton("SAVE BEST AS REF-A", this, &MainMenuScreen::saveBestClicked);
    }

    addButton("IMPORT REF-A", this, &MainMenuScreen::importRefAClicked);

    if (state()->comparisonLaps.contains("ref-a"))
    {
        addButton("EXPORT REF-A", this, &MainMenuScreen::exportRefAClicked);
    }

    addButton ("EXIT DASH", this, &MainMenuScreen::exitClicked);

    layout()->insertStretch(layout()->count()-1);
}

void MainMenuScreen::exitClicked()
{
    DBG_MSG << "Exit";
    if (!dash().isNull())
    {
        dash()->widget->exitDash();
        deleteLater();
    }
    else
    {
        deleteLater();
    }
}

void MainMenuScreen::resetClicked()
{
    DBG_MSG << "Reset data";
    MainWidget * main = dynamic_cast<MainWidget*> (this->parent());
    main->startDash();
    deleteLater();
}

void MainMenuScreen::saveBestClicked()
{
    DBG_MSG << "Save lap";
    state()->saveComparisonLap("best", "ref-a");
    state()->loadComparisonLap("ref-a", "ref-a");
    //QFileDialog::getOpenFileName();
    deleteLater();
}

void MainMenuScreen::clearRefAClicked()
{
    if (state()->comparisonLaps.contains("ref-a"))
    {
        state()->comparisonLaps.remove("ref-a");
    }
    deleteLater();
}

void MainMenuScreen::importRefAClicked()
{
    auto filePath = QFileDialog::getOpenFileName(this, "Load lap", QString(), "Laps (*.gt7lap, *.gt7track)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Load" << filePath << "as ref-a";
        state()->loadComparisonLap("ref-a", filePath, true);
        state()->saveComparisonLap("ref-a", "ref-a");
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}

void MainMenuScreen::exportRefAClicked()
{
    auto filePath = QFileDialog::getSaveFileName(this, "Save lap", QDate::currentDate().toString("yyyy-MM-dd") + " Reference Lap.gt7lap", "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save" << filePath << "from ref-a";
        state()->saveComparisonLap("ref-a", filePath, true);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}
