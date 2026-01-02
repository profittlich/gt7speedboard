#ifndef MAINWIDGET_H
#define MAINWIDGET_H

#include <QWidget>
#include <QLabel>
#include <sb/widgets/ColorLabel.h>
#include <sb/receiver/GT7TelemetryReceiver.h>
#include <sb/system/Controller.h>
#include <QVBoxLayout>


class MainWidget : public QWidget
{
    Q_OBJECT

public:
    MainWidget(QWidget *parent = nullptr);
    ~MainWidget();

public slots:
    void startDash();
    void showStartScreen();

protected:
    void keyPressEvent(QKeyEvent *event);

private:
    PController m_controller;
    PTelemetryReceiver m_receiver;
    PDash m_dash;
    QWidget * m_widget;
    QVBoxLayout * m_layout;
    bool m_inDash;
};
#endif // MAINWIDGET_H
