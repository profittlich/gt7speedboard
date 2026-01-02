#include "sb/widgets/ColorLabel.h"
#include "sb/system/Configuration.h"

ColorLabel::ColorLabel(QWidget * parent, QColor col) : QLabel(parent)
{
    setMinimumSize(10, 10);
    if (col.isValid())
    {
        setColor(col);
    }
    else
    {
        setColor(g_globalConfiguration.backgroundColor());
    }
}

void ColorLabel::setColor(const QColor & col)
{
    m_color = col;
}


void ColorLabel::mousePressEvent(QMouseEvent * ev)
{

}

void ColorLabel::paintEvent(QPaintEvent * ev)
{
    m_painter.begin(this);
    m_painter.setPen(m_color);
    m_painter.setBrush(m_color);
    m_painter.drawRect(0, 0, width(), height());
    m_painter.end();

    QLabel::paintEvent(ev);
}
