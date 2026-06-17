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
    QPushButton * m_btnIP = nullptr;
    ImageLabel * m_lbHead = nullptr;
    QComboBox * m_selectedLayout = nullptr;
    QStackedLayout * m_parentLayout = nullptr;
    QWidget * m_parent = nullptr;
};
