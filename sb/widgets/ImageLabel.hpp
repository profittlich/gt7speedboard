#pragma once

#include <QLabel>
#include <QPixmap>
#include <QPainter>


class ImageLabel : public QLabel
{
    Q_OBJECT

public:
    ImageLabel(QWidget * parent = nullptr, QPixmap pm = QPixmap());

    void setPixmap(const QPixmap & pm);

protected:
    void resizeEvent(QResizeEvent * ev);

private:
    QPixmap m_pixmap;
};
