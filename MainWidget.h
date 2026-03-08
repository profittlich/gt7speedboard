#ifndef MAINWIDGET_H
#define MAINWIDGET_H

#include <QWidget>
#include <QLabel>
#include <sb/widgets/ColorLabel.h>
#include <sb/receiver/GT7TelemetryReceiver.h>
#include <sb/system/Controller.h>
#include <sb/system/RawRecorder.h>
#include <QVBoxLayout>
#include <QStackedLayout>


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
    void resizeEvent(QResizeEvent * ev);

private:
    PController m_controller;
    PTelemetryReceiver m_receiver;
    PRawRecorder m_debugRecorder;
    PDash m_dash;
    QWidget * m_widget;
    QStackedLayout * m_layout;
    bool m_inDash;
};
#endif // MAINWIDGET_H
