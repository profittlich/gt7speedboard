#pragma once

#include "MenuScreen.h"

class LapsMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    LapsMenuScreen (MainWidget * parent, PDash dash, PState state);

public slots:
    void lapClicked();

};