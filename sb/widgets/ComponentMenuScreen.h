#pragma once

#include "MenuScreen.h"

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
