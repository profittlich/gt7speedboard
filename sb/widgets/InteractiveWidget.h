#pragma once

#include <QWidget>
#include <QEvent>

class InteractiveWidget : public QWidget
{
    Q_OBJECT

public:
    InteractiveWidget()
    {
        installEventFilter(this);
    }

signals:
    void interceptEvent(QEvent * event);

protected:
    bool eventFilter(QObject *obj, QEvent *event)
    {/*
        if (event->type() != 39
            && event->type() != 12
            && event->type() != 76
            && event->type() != 100)
        {
            qDebug("Event: " + QString::number(event->type()).toLatin1());
        }*/
        if (event->type() == QEvent::MouseButtonPress)
        {
            qDebug("Event filter: MouseButtonPress");
            emit interceptEvent(event);
        }
        if (event->type() == QEvent::MouseButtonRelease)
        {
            qDebug("Event filter: MouseButtonRelease");
            emit interceptEvent(event);
        }
        return QObject::eventFilter(obj, event);
    }


    void mouseReleaseEvent(QMouseEvent *event)
    {
        qDebug("Mouse press");
    }
};
