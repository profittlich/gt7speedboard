#pragma once

#include <QWidget>
#include <QLineEdit>
#include <QLabel>
#include <QComboBox>
#include <QScrollArea>
#include "sb/system/DashBuilder.h"
#include "MainWidget.h"
#include "sb/widgets/ButtonLabel.h"
#include "sb/widgets/SideButtonLabel.h"

class MenuScreen : public QScrollArea
{
    Q_OBJECT

public:
    MenuScreen (MainWidget * parent, PDash dash, PState state);

public slots:
    void closeClicked();

protected:
    void stackMenu(MenuScreen * menu);

    void setupScroller(QScrollArea *area);
    QVBoxLayout * layout() { return m_layout; }
    QWidget * widget () { return m_widget; }
    PDash dash() { return m_dash; }
    PState state() { return m_state; }
    void setTitle (QString t);

    template<typename PointerToMemberFunction>
    QPushButton* addButton(QString label, QObject * target, PointerToMemberFunction clicked)
    {
        QPushButton * button = new QPushButton(widget());
        button->setText(label);
        button->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        auto font = button->font();
        font.setPointSizeF(23);
        font.setBold(true);
        button->setFont(font);
        connect (button, &QPushButton::clicked, target, clicked);

        layout()->addWidget(button);

        return button;
    }

private:
    PDash m_dash;
    PState m_state;
    QWidget * m_widget;
    QVBoxLayout * m_layout;
    SideButtonLabel * m_pbClose;
};
