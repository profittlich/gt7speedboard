#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>

class StartScreen : public QWidget
{
    Q_OBJECT

public:
    StartScreen (QWidget * parent);

public slots:
    void startDashClicked();
    void selectLayout(unsigned idx);

signals:
    void startDash();

protected:
    void resizeEvent(QResizeEvent * e);

private:
    QLineEdit * m_leIP;
    QLabel * m_lbHead;
    QComboBox * m_selectedLayout;
};
