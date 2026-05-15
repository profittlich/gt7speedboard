#include "MainMenuScreen.h"
#include "sb/widgets/DashWidget.h"
#include "LapsMenuScreen.h"
#include <QFileDialog>

/*
 *  Menu structure
 *
 *  NEXT PAGE
 *  PREV PAGE
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
    addPageFlipper();
    addButton ("RESET DATA", this, &MainMenuScreen::resetClicked);
    addButton ("LAPS", this, &MainMenuScreen::lapsClicked);
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

void MainMenuScreen::lapsClicked()
{
    DBG_MSG << "Replace component";
    MainWidget * mw = dynamic_cast<MainWidget*> (parent());
    MenuScreen * men = new LapsMenuScreen (mw, dash(), state());
    mw->m_layout->insertWidget(0,men);
    mw->m_layout->setCurrentIndex(0);

    deleteLater();
}

void MainMenuScreen::prevPageClicked()
{
    size_t pages = dash()->pages.size();
    size_t curPage = dash()->widget->currentIndex();
    curPage--;
    if (curPage == 0)
    {
        curPage = pages;
    }
    dash()->widget->setCurrentIndex(curPage);
    m_curPage->setText(QString::number(curPage) + " / " + QString::number(pages));
    deleteLater();
}

void MainMenuScreen::nextPageClicked()
{
    size_t pages = dash()->pages.size();
    size_t curPage = dash()->widget->currentIndex();
    curPage++;
    if (curPage > pages)
    {
        curPage = 1;
    }
    dash()->widget->setCurrentIndex(curPage);
    m_curPage->setText(QString::number(curPage) + " / " + QString::number(pages));
    deleteLater();
}

void MainMenuScreen::addPageFlipper()
{
    QWidget * flipper = new QWidget(widget());
    QHBoxLayout * flipLayout = new QHBoxLayout(flipper);
    flipLayout->setContentsMargins(0,0,0,0);

    QPushButton * prev = new QPushButton(flipper);
    prev->setText("|<");
    prev->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    auto font = prev->font();
    font.setPointSizeF(23);
    font.setBold(true);
    prev->setFont(font);
    connect (prev, &QPushButton::clicked, this, &MainMenuScreen::prevPageClicked);
    flipLayout->addWidget(prev);

    m_curPage = new QLabel(flipper);
    size_t pages = dash()->pages.size();
    size_t curPage = dash()->widget->currentIndex();
    m_curPage->setText(QString::number(curPage) + " / " + QString::number(pages));
    m_curPage->setStyleSheet ("height: 100px;     border-style: none;  color:white;");
    m_curPage->setAlignment(Qt::AlignCenter);
    font = m_curPage->font();
    font.setPointSizeF(23);
    font.setBold(true);
    m_curPage->setFont(font);
    flipLayout->addWidget(m_curPage);

    QPushButton * next = new QPushButton(flipper);
    next->setText(">|");
    next->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = next->font();
    font.setPointSizeF(23);
    font.setBold(true);
    next->setFont(font);
    connect (next, &QPushButton::clicked, this, &MainMenuScreen::nextPageClicked);
    flipLayout->addWidget(next);


    layout()->addWidget(flipper);
}