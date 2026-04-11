#include "MainMenuScreen.h"
#include "sb/widgets/DashWidget.h"
#include <QFileDialog>

// Main menu
MainMenuScreen::MainMenuScreen (MainWidget * parent, PDash dash, PState pstate) : MenuScreen(parent, dash, pstate)
{
    QPushButton * pbExit = new QPushButton(widget());
    pbExit->setText("EXIT DASH");
    pbExit->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    auto font = pbExit->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbExit->setFont(font);
    connect (pbExit, &QPushButton::clicked, this, &MainMenuScreen::exitClicked);

    QPushButton * pbReset = new QPushButton(widget());
    pbReset->setText("RESET DATA");
    pbReset->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbReset->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbReset->setFont(font);
    connect (pbReset, &QPushButton::clicked, this, &MainMenuScreen::resetClicked);


    QPushButton * pbClearRefA = nullptr;
    if (state()->comparisonLaps.contains("ref-a"))
    {
        pbClearRefA = new QPushButton(widget());
        pbClearRefA->setText("CLEAR REF-A");
        pbClearRefA->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbClearRefA->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbClearRefA->setFont(font);
        connect (pbClearRefA, &QPushButton::clicked, this, &MainMenuScreen::clearRefAClicked);
    }

    QPushButton * pbSave = nullptr;
    if (state()->comparisonLaps.contains("best"))
    {
        pbSave = new QPushButton(widget());
        pbSave->setText("SAVE BEST AS REF-A");
        pbSave->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbSave->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbSave->setFont(font);
        connect (pbSave, &QPushButton::clicked, this, &MainMenuScreen::saveBestClicked);
    }

    QPushButton * pbImport = new QPushButton(widget());
    pbImport->setText("IMPORT REF-A");
    pbImport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbImport->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbImport->setFont(font);
    connect (pbImport, &QPushButton::clicked, this, &MainMenuScreen::importRefAClicked);

    QPushButton * pbExport = nullptr;
    if (state()->comparisonLaps.contains("ref-a"))
    {
        pbExport = new QPushButton(widget());
        pbExport->setText("EXPORT REF-A");
        pbExport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbExport->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbExport->setFont(font);
        connect (pbExport, &QPushButton::clicked, this, &MainMenuScreen::exportRefAClicked);
    }

    layout()->addWidget(pbReset);
    if (pbClearRefA != nullptr)
    {
        layout()->addWidget(pbClearRefA);
    }
    if (pbSave != nullptr)
    {
        layout()->addWidget(pbSave);
    }
    layout()->addWidget(pbImport);
    if (pbExport != nullptr)
    {
        layout()->addWidget(pbExport);
    }

    layout()->addWidget(pbExit);
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
    auto filePath = QFileDialog::getOpenFileName(this, "Load lap", QString(), "Laps (*.gt7lap)");
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
