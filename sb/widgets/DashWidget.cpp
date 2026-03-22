#include "DashWidget.h"
#include "DialogWidget.h"

DashWidget::DashWidget (QWidget * parent, PDash dash) : QStackedWidget(parent)
{
    DialogWidget * dialog = new DialogWidget(this, dash);
    addWidget(dialog);
    m_color = g_globalConfiguration.dimColor();
}

void DashWidget::paintEvent(QPaintEvent * ev)
{
    m_painter.begin(this);
    m_painter.setPen(m_color);
    m_painter.setBrush(m_color);
    m_painter.drawRect(0, 0, width(), height());
    m_painter.end();

    QStackedWidget::paintEvent(ev);
}

void DashWidget::setColor (const QColor & color)
{
    m_color = color;
}
