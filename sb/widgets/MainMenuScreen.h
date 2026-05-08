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
    void saveBestClicked();
    void clearRefAClicked();
    void importRefAClicked();
    void exportRefAClicked();

};