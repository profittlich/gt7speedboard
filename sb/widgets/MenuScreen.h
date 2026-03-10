#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include "sb/system/DashBuilder.h"
#include "MainWidget.h"

class MenuScreen : public QWidget
{
    Q_OBJECT

public:
    MenuScreen (MainWidget * parent, PDash dash);

public slots:
    void exitClicked();
    void closeClicked();
    void resetClicked();

private:
    ButtonLabel * m_exit;
    ButtonLabel * m_close;
    PDash m_dash;

};
