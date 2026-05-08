#pragma once

#include <QLabel>
#include <QMouseEvent>
#include <QPainter>


class ColorLabel : public QLabel
{
    Q_OBJECT

public:
    ColorLabel(QWidget * parent = nullptr, QColor col = QColor());

    void setColor(const QColor & col);
    void setTextColor(const QColor & col);

protected:
    void mouseReleaseEvent(QMouseEvent * ev);
    void paintEvent(QPaintEvent * ev);

signals:
    void clicked();

private:
    QColor m_color;
    QPainter m_painter;
};
