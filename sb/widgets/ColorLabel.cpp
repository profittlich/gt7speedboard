#include "sb/widgets/ColorLabel.h"
#include "sb/system/Configuration.h"

ColorLabel::ColorLabel(QWidget * parent, QColor col) : QLabel(parent)
{
    //DBG_MSG << minimumHeight() << minimumHeight() << sizeHint();
    setMinimumSize(10, 0);
    //setSizePolicy (QSizePolicy::Preferred, QSizePolicy::Preferred);
    setColor(col);
}

void ColorLabel::setColor(const QColor & col)
{
    if (!col.isValid())
    {
        m_color = g_globalConfiguration.backgroundColor();
    }
    else
    {
        m_color = col;
    }
}


void ColorLabel::mouseReleaseEvent(QMouseEvent * ev)
{
    emit clicked();
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
