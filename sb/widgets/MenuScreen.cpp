#include "MenuScreen.h"
#include "sb/system/Helpers.h"

#include <QtLogging>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QResizeEvent>
#include <QStandardPaths>
#include <QComboBox>
#include <QSpinBox>
#include <QDir>
#include <QFileDialog>

#include "sb/system/Configuration.h"
#include "sb/widgets/DashWidget.h"
#include "sb/widgets/SideButtonLabel.h"

MenuScreen::MenuScreen (MainWidget * parent, PDash dash, PState state) : QWidget(parent)
{
    setContentsMargins(5,5,5,5);
    m_dash = dash;
    m_state = state;
    //setMinimumSize(500, 500);
    setStyleSheet("background-color: " + g_globalConfiguration.backgroundColor().name() + ";");

    QVBoxLayout * layout = new QVBoxLayout(this);

    QPushButton * pbExit = new QPushButton(this);
    pbExit->setText("EXIT DASH");
    pbExit->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    auto font = pbExit->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbExit->setFont(font);
    connect (pbExit, &QPushButton::clicked, this, &MenuScreen::exitClicked);

    QPushButton * pbReset = new QPushButton(this);
    pbReset->setText("RESET DATA");
    pbReset->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbReset->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbReset->setFont(font);
    connect (pbReset, &QPushButton::clicked, this, &MenuScreen::resetClicked);


    QPushButton * pbClearRefA = nullptr;
    if (m_state->comparisonLaps.contains("ref-a"))
    {
        pbClearRefA = new QPushButton(this);
        pbClearRefA->setText("CLEAR REF-A");
        pbClearRefA->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbClearRefA->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbClearRefA->setFont(font);
        connect (pbClearRefA, &QPushButton::clicked, this, &MenuScreen::clearRefAClicked);
    }

    QPushButton * pbSave = new QPushButton(this);
    pbSave->setText("SAVE BEST AS REF-A");
    pbSave->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbSave->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbSave->setFont(font);
    connect (pbSave, &QPushButton::clicked, this, &MenuScreen::saveBestClicked);

    QPushButton * pbImport = new QPushButton(this);
    pbImport->setText("IMPORT REF-A");
    pbImport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbImport->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbImport->setFont(font);
    connect (pbImport, &QPushButton::clicked, this, &MenuScreen::importRefAClicked);

    QPushButton * pbExport = new QPushButton(this);
    pbExport->setText("EXPORT REF-A");
    pbExport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbExport->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbExport->setFont(font);
    connect (pbExport, &QPushButton::clicked, this, &MenuScreen::exportRefAClicked);

    SideButtonLabel * pbClose = new SideButtonLabel(this, SideButtonLabel::Close);
    pbClose->setText("MENU");
    pbClose->setAlignment(Qt::AlignCenter);
    font = pbClose->font();
    font.setPointSizeF(60);
    font.setBold(true);
    pbClose->setFont(font);
    pbClose->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");
    connect (pbClose, &SideButtonLabel::buttonClicked, this, &MenuScreen::closeClicked);

    layout->addWidget(pbClose);
    layout->addWidget(pbReset);
    if (pbClearRefA != nullptr)
    {
        layout->addWidget(pbClearRefA);
    }
    layout->addWidget(pbSave);
    layout->addWidget(pbImport);
    if (pbClearRefA != nullptr)
    {
        layout->addWidget(pbExport);
    }


    layout->addWidget(pbExit);
    layout->insertStretch(layout->count()-1);
}


void MenuScreen::exitClicked()
{
    DBG_MSG << "Exit";
    if (!m_dash.isNull())
    {
        m_dash->widget->exitDash();
        deleteLater();
    }
    else
    {
        deleteLater();
    }
}


void MenuScreen::closeClicked()
{
    DBG_MSG << "Close";
    deleteLater();
}

void MenuScreen::resetClicked()
{
    DBG_MSG << "Reset data";
    MainWidget * main = dynamic_cast<MainWidget*> (this->parent());
    main->startDash();
    deleteLater();
}

void MenuScreen::saveBestClicked()
{
    DBG_MSG << "Save lap";
    m_state->saveComparisonLap("best", "ref-a");
    m_state->loadComparisonLap("ref-a", "ref-a");
    //QFileDialog::getOpenFileName();
    deleteLater();
}

void MenuScreen::clearRefAClicked()
{
    if (m_state->comparisonLaps.contains("ref-a"))
    {
        m_state->comparisonLaps.remove("ref-a");
    }
    deleteLater();
}

void MenuScreen::importRefAClicked()
{
    auto filePath = QFileDialog::getOpenFileName(this, "Load lap", QString(), "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Load" << filePath << "as ref-a";
        m_state->loadComparisonLap("ref-a", filePath, true);
        m_state->saveComparisonLap("ref-a", "ref-a");
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}

void MenuScreen::exportRefAClicked()
{
    auto filePath = QFileDialog::getSaveFileName(this, "Save lap", QDate::currentDate().toString("yyyy-MM-dd") + " Reference Lap.gt7lap", "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save" << filePath << "from ref-a";
        m_state->saveComparisonLap("ref-a", filePath, true);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}
