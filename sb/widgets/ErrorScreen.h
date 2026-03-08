#pragma once

#include "qscrollarea.h"
#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include "sb/system/DashBuilder.h"
#include "ImageLabel.hpp"

class ErrorScreen : public QWidget
{
    Q_OBJECT

public:
    ErrorScreen (QWidget * parent, QString message, PDash dash);

public slots:
    void okClicked();

private:
    QLabel * m_lbMessage;
    PDash m_dash;

};
