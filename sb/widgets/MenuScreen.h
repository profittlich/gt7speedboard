#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include <QScrollArea>
#include "sb/system/DashBuilder.h"
#include "MainWidget.h"
#include "sb/widgets/ButtonLabel.h"
#include "sb/widgets/SideButtonLabel.h"

class MenuScreen : public QScrollArea
{
    Q_OBJECT

public:
    MenuScreen (MainWidget * parent, PDash dash, PState state);

public slots:
    void closeClicked();

protected:
    void setupScroller(QScrollArea *area);
    QVBoxLayout * layout() { return m_layout; }
    QWidget * widget () { return m_widget; }
    PDash dash() { return m_dash; }
    PState state() { return m_state; }
    void setTitle (QString t);

private:
    PDash m_dash;
    PState m_state;
    QWidget * m_widget;
    QVBoxLayout * m_layout;
    SideButtonLabel * m_pbClose;
};

class MainMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    MainMenuScreen (MainWidget * parent, PDash dash, PState state);

public slots:
    void exitClicked();
    void resetClicked();
    void saveBestClicked();
    void clearRefAClicked();
    void importRefAClicked();
    void exportRefAClicked();

};


class ComponentContextMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    ComponentContextMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp);

public slots:
    void actionClicked();
    void replaceClicked();

protected:
    void updateParams();

private:
    PState m_state;
    PComponent m_component;
    QLabel * m_lbParam;

};

class ComponentSelectionMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    ComponentSelectionMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp);

public slots:
    void componentClicked();

private:
    PComponent m_component;
};
