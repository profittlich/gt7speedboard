#pragma once

#include <QStackedWidget>
#include <QPainter>
#include <QVBoxLayout>
#include <QPushButton>
#include "sb/system/Dash.h"

class DashWidget : public QStackedWidget
{
    Q_OBJECT

public:
    DashWidget (QWidget * parent, PDash dash);
    void setColor (const QColor & color);

protected:
    void paintEvent(QPaintEvent * ev);

signals:
    void exitDash();
    void showMenu();

private:
    QPainter m_painter;
    QColor m_color;
};


