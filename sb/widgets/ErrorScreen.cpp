#include "ErrorScreen.h"
#include "sb/system/Helpers.h"

#include <QtLogging>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QResizeEvent>
#include <QStandardPaths>
#include <QComboBox>
#include <QSpinBox>
#include <QDir>

#include "sb/system/Configuration.h"

ErrorScreen::ErrorScreen (QWidget * parent, QString message, PDash dash) : QWidget(parent)
{
    m_dash = dash;
    //setMinimumSize(500, 500);
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");

    QVBoxLayout * layout = new QVBoxLayout(this);

    m_lbMessage = new QLabel(this);
    m_lbMessage->setAlignment(Qt::AlignmentFlag::AlignCenter | Qt::AlignmentFlag::AlignHCenter);
    m_lbMessage->setText("Error:\n" + message);
    auto font = m_lbMessage->font();
    font.setPointSizeF(23);
    font.setBold(true);
    m_lbMessage->setFont(font);
    layout->addWidget(m_lbMessage);

    QPushButton * pbClose = new QPushButton(this);
    pbClose->setText("CLOSE");
    pbClose->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbClose->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbClose->setFont(font);
    connect (pbClose, &QPushButton::clicked, this, &ErrorScreen::okClicked);

    layout->addWidget(pbClose);
}


void ErrorScreen::okClicked()
{
    if (!m_dash.isNull())
    {
        m_dash->widget->exitDash();
        deleteLater();
    }
    else
    {
        deleteLater();
    }
}
