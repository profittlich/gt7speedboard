#pragma once

#include <QLabel>
#include <QMouseEvent>
#include <QPainter>

#include "sb/widgets/ButtonLabel.h"


class SideButtonLabel : public ButtonLabel
{
    Q_OBJECT

public:
    enum Type { Menu, Close, Back };
    SideButtonLabel(QWidget * parent = nullptr, Type type = Menu);

protected:
    void mousePressEvent(QMouseEvent * ev);
    void paintEvent(QPaintEvent * ev);

signals:
    void buttonClicked();

private:
    QPainter m_painter;
    Type m_type;
};
