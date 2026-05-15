#pragma once

#include "MenuScreen.h"

class LapMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    LapMenuScreen (MainWidget * parent, PDash dash, PState state, QString lap);

public slots:
    void saveAsRefClicked();
    void clearClicked();
    void importClicked();
    void exportClicked();

private:
    QString m_lap;
};