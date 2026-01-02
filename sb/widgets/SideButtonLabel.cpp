#include "sb/widgets/SideButtonLabel.h"
#include "sb/system/Configuration.h"
#include <QFileDialog>

const unsigned g_margin = 10;
const unsigned g_spacing = 17;

SideButtonLabel::SideButtonLabel(QWidget * parent) : ButtonLabel(parent)
{
}

void SideButtonLabel::mousePressEvent(QMouseEvent * ev)
{
    if (ev->pos().x() < height() + g_margin)
    {
        qInfo("Side button clicked");
        emit buttonClicked();
    }
    else
    {
        qInfo("Label clicked");
        emit labelClicked();
    }
}

void SideButtonLabel::paintEvent(QPaintEvent * ev)
{
    m_painter.begin(this);
    m_painter.setPen(g_globalConfiguration.backgroundColor());
    m_painter.setBrush(g_globalConfiguration.backgroundColor());

    QPolygon poly(3);
    poly.setPoint(0, QPoint(g_margin, height()/2));
    poly.setPoint(1, QPoint(g_margin + height()/2, g_margin));
    poly.setPoint(2, QPoint(g_margin + height()/2, height() - g_margin));
    m_painter.drawPolygon(poly);
    m_painter.drawRect(3*g_margin, height()/2-g_margin,     height()-2*g_margin, 2*g_margin);
    m_painter.end();

    QLabel::paintEvent(ev);
}
