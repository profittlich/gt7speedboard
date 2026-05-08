#include "ImageLabel.hpp"
#include <QResizeEvent>
#include <sb/system/Helpers.h>


ImageLabel::ImageLabel(QWidget * parent, QPixmap pm) : QLabel(parent), m_pixmap(pm)
{
    setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);
}

void ImageLabel::setPixmap(const QPixmap & pm)
{
    m_pixmap = pm;

    //QLabel::setPixmap(pm.scaled(width(), height(), Qt::KeepAspectRatio, Qt::SmoothTransformation));
}

void ImageLabel::resizeEvent(QResizeEvent * ev)
{
    DBG_MSG << this->sizePolicy();
    DBG_MSG << "resizeEvent" << ev->size().width() << ev->size().height() << m_pixmap.width() << m_pixmap.height();

    QLabel::setPixmap(m_pixmap.scaled(ev->size().width(), ev->size().height(), Qt::KeepAspectRatio, Qt::SmoothTransformation));
    QLabel::resizeEvent(ev);
DBG_MSG << "resizeEvent-End" << width() << height();
}
