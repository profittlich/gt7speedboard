#pragma once

#include <QLabel>
#include <QMouseEvent>
#include <QPainter>


class GaugeLabel : public QLabel
{
    Q_OBJECT

public:
    GaugeLabel(QWidget * parent, const float base, const float spread, bool twoWay, bool vertical, bool displayExcess=false);

    void setValue(const float value);
    void setSpread(float s);
    void setBase (float b);
    void disable();
    void setStickyBars(bool on);
    void setBarColors (QColor neg, QColor pos);

protected:
    void mouseReleaseEvent(QMouseEvent * ev);
    void paintEvent(QPaintEvent * ev);

signals:
    void clicked();

private:
    QColor m_backgroundColor;
    QColor m_minusColor;
    QColor m_plusColor;
    QPainter m_painter;
    QLinearGradient m_minusGradient;
    QLinearGradient m_plusGradient;
    float m_value = 0;
    float m_base = 0;
    float m_spread = 0;
    bool m_twoWay = false;
    bool m_vertical = false;
    bool m_displayExcess = false;
    bool m_disabled = false;
    bool m_stickyBars = false;
    float m_stickyPos = 0;
    float m_stickyNeg = 0;
    unsigned m_countdownPos = 0;
    unsigned m_countdownNeg = 0;
};
