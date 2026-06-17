#pragma once

#include "DashWidget.h"

class DialogWidget : public QWidget
{
    Q_OBJECT

public:
    DialogWidget (QWidget * parent, PDash dash) : QWidget(parent)
    {
        m_dash = dash;
        QLayout * layout = new QVBoxLayout(this);
        QPushButton * btn = new QPushButton(this);
        btn->setText("Dismiss");
        connect(btn, &QPushButton::clicked, this, &DialogWidget::returnToDash);
        layout->addWidget(btn);
    }

public slots:
    void returnToDash()
    {
        m_dash->widget->setCurrentIndex(1);
    }

private:
    PDash m_dash;
};
