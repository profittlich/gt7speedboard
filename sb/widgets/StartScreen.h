#pragma once

#include "qscrollarea.h"
#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include <QtWidgets/qpushbutton.h>
#include <QtWidgets/qstackedlayout.h>
#include "ImageLabel.hpp"

class StartScreen : public QWidget
{
    Q_OBJECT

public:
    StartScreen (QWidget * parent, QStackedLayout *parentLayout);

public slots:
    void startDashClicked();
    void selectLayout(unsigned idx);
    void setFontSize(float size);
    void selectFontSize(int idx);
    void editIP();
    void gotNewIP();
    void textInputCancelled();

signals:
    void startDash();

protected:
    void resizeEvent(QResizeEvent * e);

private:
    QPushButton * m_btnIP;
    ImageLabel * m_lbHead;
    QComboBox * m_selectedLayout;
    QStackedLayout * m_parentLayout;
    QWidget * m_parent;
};
