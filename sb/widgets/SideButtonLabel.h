#pragma once

#include <QLabel>
#include <QMouseEvent>
#include <QPainter>

#include "sb/widgets/ButtonLabel.h"


class SideButtonLabel : public ButtonLabel
{
    Q_OBJECT

public:
    SideButtonLabel(QWidget * parent = nullptr);

protected:
    void mousePressEvent(QMouseEvent * ev);
    void paintEvent(QPaintEvent * ev);

signals:
    void buttonClicked();

private:
    QPainter m_painter;
};
