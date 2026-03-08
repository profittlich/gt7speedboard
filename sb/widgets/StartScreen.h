#pragma once

#include "qscrollarea.h"
#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include "ImageLabel.hpp"

class StartScreen : public QWidget
{
    Q_OBJECT

public:
    StartScreen (QWidget * parent);

public slots:
    void startDashClicked();
    void selectLayout(unsigned idx);
    void setFontSize(float size);

signals:
    void startDash();

protected:
    void resizeEvent(QResizeEvent * e);

private:
    QLineEdit * m_leIP;
    ImageLabel * m_lbHead;
    QComboBox * m_selectedLayout;
};
