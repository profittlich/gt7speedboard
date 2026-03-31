#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include "sb/system/DashBuilder.h"
#include "MainWidget.h"
#include "sb/widgets/ButtonLabel.h"

class MenuScreen : public QWidget
{
    Q_OBJECT

public:
    MenuScreen (MainWidget * parent, PDash dash, PState state);

public slots:
    void exitClicked();
    void closeClicked();
    void resetClicked();
    void saveBestClicked();
    void clearRefAClicked();
    void importRefAClicked();
    void exportRefAClicked();

private:
    ButtonLabel * m_exit;
    ButtonLabel * m_close;
    PDash m_dash;
    PState m_state;

};
