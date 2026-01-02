#include "sb/widgets/GaugeLabel.h"
#include "sb/system/Configuration.h"

GaugeLabel::GaugeLabel(QWidget * parent, const float base, const float spread, bool twoWay, bool vertical, bool displayExcess) : QLabel(parent), m_base(base), m_spread(spread), m_twoWay(twoWay), m_vertical(vertical), m_displayExcess(displayExcess)
{
    setMinimumSize(10, 10);
    setValue(m_base);
    m_backgroundColor = g_globalConfiguration.backgroundColor();


    m_minusGradient = QLinearGradient (0, 10,0,120);
    m_minusGradient.setColorAt(0.0, QColor(0x222222));
    m_minusGradient.setColorAt(0.2, QColor(0x222222));
    m_minusGradient.setColorAt(1.0, QColor(0xff0000));
    m_plusGradient = QLinearGradient (0, 10,0,120);
    m_plusGradient.setColorAt(0.0, QColor(0X222222));
    m_plusGradient.setColorAt(0.2, QColor(0x222222));
    m_plusGradient.setColorAt(1.0, QColor(0xff00));

}

void GaugeLabel::setValue (const float value)
{
    m_disabled = false;
    m_value = value;
}

void GaugeLabel::disable()
{
    m_disabled = true;
    m_value = 0.0;
}

void GaugeLabel::mousePressEvent(QMouseEvent * ev)
{

}

void GaugeLabel::paintEvent(QPaintEvent * ev)
{
    float a = (m_value - m_base) / m_spread;
    float b = a;

    if (a > 1)
    {
        a = 1;
    }
    else if (a < -1)
    {
        a = -1;
    }

    float start = 1;
    if (m_twoWay)
    {
        start = 0.5;
    }
    else
    {
        if (a < 0) a = 0;
    }

    m_painter.begin(this);

    m_painter.setPen(m_backgroundColor);
    m_painter.setBrush(m_backgroundColor);
    m_painter.drawRect(0, 0, width(), height());

    if (!m_disabled)
    {
        if (m_vertical)
        {
            if (a < 0)
            {
                m_minusGradient.setStart(0, start * height());
                m_minusGradient.setFinalStop(0, start * height() - a * start * height());
                m_painter.fillRect(0, start * height(), width(), -a * start * height(), m_minusGradient);
            }
            else
            {
                m_plusGradient.setStart(0, start * height());
                m_plusGradient.setFinalStop(0, start * height() - a * start * height());
                m_painter.fillRect(0, start * height(), width(), -a * start * height(), m_plusGradient);
            }
            if (fabs(b)<=1.0)
            {
                m_painter.setPen(QColor(255, 255, 255));
                m_painter.drawLine(0, start * height(), width(), start * height());
            }
        }
        else
        {
            start = 1 - start;
            if (a < 0)
            {
                m_minusGradient.setStart(start * width(), 0);
                m_minusGradient.setFinalStop(start * width() + a * start * width(), 0);
                m_painter.fillRect(start * width(), 0, a * start * width(), height(), m_minusGradient);
            }
            else
            {
                m_plusGradient.setStart(start * width(), 0);
                m_plusGradient.setFinalStop(start * width() + a * (1-start) * width(), 0);
                m_painter.fillRect(start * width(), 0, a * (1-start) * width(), height(), m_plusGradient);
            }
            if (fabs(b)<=1.0)
            {
                m_painter.setPen(QColor(255, 255, 255));
                m_painter.drawLine(start * width(), 0, start * width(), height());
            }
        }

        if (m_displayExcess)
        {
            if (fabs(b)>1.0)
            {
                setText(QString::number(round(10*b)/10));
            }
            else
            {
                setText(QString());
            }
        }
    }

    m_painter.end();

    if (!m_disabled)
    {
        QLabel::paintEvent(ev);
    }
}
