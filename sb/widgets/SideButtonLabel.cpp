#include "sb/widgets/SideButtonLabel.h"
#include "sb/system/Configuration.h"
#include "sb/system/Helpers.h"
#include <QFileDialog>

const unsigned g_margin = 10;
const unsigned g_spacing = 17;

SideButtonLabel::SideButtonLabel(QWidget * parent, Type type) : ButtonLabel(parent), m_type(type)
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
    QLabel::paintEvent(ev);

    m_painter.begin(this);
    QColor col;
    col.setRed(96);
    col.setGreen(96);
    col.setBlue(96);
    col.setAlpha(160);
    m_painter.setBrush(col);
    col.setAlpha(0);
    m_painter.setPen(col);

    auto margin = height() * g_margin / 70.0;

    if (m_type == Back)
    {
        QPolygon poly(3);
        poly.setPoint(0, QPoint(margin, height()/2));
        poly.setPoint(1, QPoint(margin + height()/2, margin));
        poly.setPoint(2, QPoint(margin + height()/2, height() - margin));
        m_painter.drawPolygon(poly);
        m_painter.drawRect(3*margin, height()/2-margin,     height()-2*margin, 2*margin);
    }
    else if (m_type == Menu)
    {
        m_painter.drawRect(0, height()/2-0.6*margin - 2 * margin,     height()-margin, 1.1*margin);
        m_painter.drawRect(0, height()/2-0.6*margin,              height()-margin, 1.1*margin);
        m_painter.drawRect(0, height()/2-0.6*margin + 2 * margin,     height()-margin, 1.1*margin);
    }
    else if (m_type == Close)
    {
        QPen pen;
        col.setAlpha(160);
        pen.setColor(col);
        pen.setWidth(10);
        m_painter.setPen(pen);
        //m_painter.drawRect(0, height()/2-0.6*margin - 2 * margin,     height()-margin, 1.1*margin);
        m_painter.drawLine(margin,margin,height()-margin,height()-margin);
        m_painter.drawLine(margin,height()-margin,height()-margin,margin);
    }


    m_painter.end();
}
