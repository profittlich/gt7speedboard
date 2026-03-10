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

#include "sb/system/Configuration.h"

MenuScreen::MenuScreen (MainWidget * parent, PDash dash) : QWidget(parent)
{
    setContentsMargins(5,5,5,5);
    m_dash = dash;
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

    /*QPushButton * pbSave = new QPushButton(this);
    pbSave->setText("SAVE DASH");
    pbSave->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbSave->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbSave->setFont(font);
    pbSave->setEnabled(false);
    //connect (pbSave, &QPushButton::clicked, this, &MenuScreen::exitClicked);*/

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
    //layout->addWidget(pbSave);


    layout->addWidget(pbExit);
    layout->insertStretch(3);
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
