#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include <QScrollArea>
#include "sb/system/DashBuilder.h"
#include "MainWidget.h"
#include "sb/widgets/ButtonLabel.h"

class MenuScreen : public QScrollArea
{
    Q_OBJECT

public:
    MenuScreen (MainWidget * parent, PDash dash, PState state);
    MenuScreen (MainWidget * parent, PDash dash, PComponent comp);

public slots:
    void exitClicked();
    void closeClicked();
    void resetClicked();
    void saveBestClicked();
    void clearRefAClicked();
    void importRefAClicked();
    void exportRefAClicked();

    void actionClicked();

protected:
    void setupScroller(QScrollArea *area);
    void updateParams();

private:
    ButtonLabel * m_exit;
    ButtonLabel * m_close;
    PDash m_dash;
    PState m_state;
    PComponent m_component;
    QLabel * m_lbParam;

};
