#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include <QtWidgets/qpushbutton.h>

class TextInput : public QWidget
{
    Q_OBJECT

public:
    TextInput (QWidget * parent, QString title, QString init);
    QString getResult();

public slots:
    void okClicked();
    void cancelClicked();

signals:
    void ok();
    void cancelled();

private:
    QLineEdit * m_leText;
    QPushButton * m_btnOK;
    QPushButton * m_btnCancel;
};
