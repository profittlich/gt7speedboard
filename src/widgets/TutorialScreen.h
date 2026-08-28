#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include <QValidator>
#include <QtWidgets/qpushbutton.h>

class TutorialScreen : public QWidget
{
    Q_OBJECT

public:
    TutorialScreen (QWidget * parent);

public slots:
    void okClicked();

protected:
    void keyPressEvent(QKeyEvent *e) override;

private:
    QString m_title;
    QPushButton * m_btnOK = nullptr;
    QLabel * m_lbText;
    unsigned m_step = 1;
};
