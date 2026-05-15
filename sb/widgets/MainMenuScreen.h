#pragma once

#include "MenuScreen.h"

class MainMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    MainMenuScreen (MainWidget * parent, PDash dash, PState state);

public slots:
    void exitClicked();
    void resetClicked();
    void lapsClicked();
    void prevPageClicked();
    void nextPageClicked();

protected:
    void addPageFlipper();

private:
    QLabel * m_curPage;
};