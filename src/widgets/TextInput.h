#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include <QValidator>
#include <QtWidgets/qpushbutton.h>

class TextInput : public QWidget
{
    Q_OBJECT

public:
    TextInput (QWidget * parent, QString title, QString init, QValidator * validator = nullptr);
    QString getResult();
    QString getTitle();

public slots:
    void okClicked();
    void cancelClicked();

signals:
    void ok();
    void cancelled();

protected:
    void keyPressEvent(QKeyEvent *e) override;

private:
    QLineEdit * m_leText = nullptr;
    QString m_title;
    QPushButton * m_btnOK = nullptr;
    QPushButton * m_btnCancel = nullptr;
    QValidator * m_validator = nullptr;
};
