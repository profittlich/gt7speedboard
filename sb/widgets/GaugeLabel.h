#pragma once

#include <QLabel>
#include <QMouseEvent>
#include <QPainter>

#include "sb/system/Helpers.h"

class GaugeLabel : public QLabel
{
    Q_OBJECT

public:
    GaugeLabel(QWidget * parent, const float base, const float spread, bool twoWay, bool vertical, bool displayExcess=false);

    void setValue(const float value);
    void disable();

protected:
    void mousePressEvent(QMouseEvent * ev);
    void paintEvent(QPaintEvent * ev);

signals:
    void clicked();

private:
    QColor m_backgroundColor;
    QPainter m_painter;
    QLinearGradient m_minusGradient;
    QLinearGradient m_plusGradient;
    float m_value;
    float m_base;
    float m_spread;
    bool m_twoWay;
    bool m_vertical;
    bool m_displayExcess;
    bool m_disabled;
    bool m_stickyBars;
    float m_stickyPos;
    float m_stickyNeg;
    unsigned m_countdownPos;
    unsigned m_countdownNeg;
};
