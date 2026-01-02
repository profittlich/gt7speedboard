#pragma once

#include <QLabel>
#include <QMouseEvent>
#include <QPainter>


class ButtonLabel : public QLabel
{
    Q_OBJECT

public:
    ButtonLabel(QWidget * parent = nullptr);

protected:
    void mousePressEvent(QMouseEvent * ev);

signals:
    void labelClicked();
};
