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
#include <QScroller>

#include "sb/system/Configuration.h"
#include "sb/widgets/DashWidget.h"
#include "sb/widgets/ComponentWidget.h"
#include "sb/components/ComponentFactory.h"

// Abstract menu
MenuScreen::MenuScreen (MainWidget * parent, PDash dash, PState state) : QScrollArea(parent), m_dash(dash), m_state(state)
{
    setContentsMargins(5,5,5,5);
    setStyleSheet("background-color: " + g_globalConfiguration.backgroundColor().name() + ";");

    QWidget * widget = new QWidget();
    widget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

    m_layout = new QVBoxLayout(widget);

    m_pbClose = new SideButtonLabel(widget, SideButtonLabel::Close);
    m_pbClose->setText("MENU");
    m_pbClose->setAlignment(Qt::AlignCenter);
    auto font = m_pbClose->font();
    font.setPointSizeF(60);
    font.setBold(true);
    m_pbClose->setFont(font);
    m_pbClose->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");
    connect (m_pbClose, &SideButtonLabel::buttonClicked, this, &MenuScreen::closeClicked);

    layout()->addWidget(m_pbClose);

    setWidget(widget);
    setupScroller(this);
}

void MenuScreen::setTitle (QString t)
{
    m_pbClose->setText(t);
}

void MenuScreen::setupScroller(QScrollArea *area)
{
    setWidgetResizable(true);
    QScroller::grabGesture(area->viewport(), QScroller::LeftMouseButtonGesture);
    QVariant OvershootPolicy = QVariant::fromValue<QScrollerProperties::OvershootPolicy>(QScrollerProperties::OvershootAlwaysOff);
    QScrollerProperties ScrollerProperties = QScroller::scroller(area->viewport())->scrollerProperties();
    ScrollerProperties.setScrollMetric(QScrollerProperties::VerticalOvershootPolicy, OvershootPolicy);
    ScrollerProperties.setScrollMetric(QScrollerProperties::HorizontalOvershootPolicy, OvershootPolicy);
    QScroller::scroller(area->viewport())->setScrollerProperties(ScrollerProperties);
}

void MenuScreen::closeClicked()
{
    DBG_MSG << "Close";
    //DBG_MSG << this->size() << this->widget()->size();
    deleteLater();
}

void MenuScreen::stackMenu(MenuScreen * menu)
{
    MainWidget * mw = dynamic_cast<MainWidget*> (parent());

    mw->m_layout->insertWidget(0,menu);
    mw->m_layout->setCurrentIndex(0);

    deleteLater();
}