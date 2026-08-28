#include "TutorialScreen.h"
#include "src/system/Configuration.h"
#include <QtWidgets/qboxlayout.h>
#include <QTimer>
#include <QKeyEvent>

TutorialScreen::TutorialScreen(QWidget * parent) : QWidget(parent)
{
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");

    QVBoxLayout * layout = new QVBoxLayout(this);

    QLabel * lbTitle = new QLabel(this);
    lbTitle->setText ("TUTORIAL");

    lbTitle->setAlignment(Qt::AlignCenter);
    auto font = lbTitle->font();
    font.setPointSizeF(30);
    font.setBold(true);
    lbTitle->setFont(font);
    lbTitle->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");

    layout->addWidget(lbTitle);

    m_lbText = new QLabel (this);
    m_lbText->setText("This is a test.");
    auto fnt = m_lbText->font();
    fnt.setPointSize(16);
    m_lbText->setFont(fnt);
    m_lbText->setMinimumHeight(30);
    m_lbText->setStyleSheet ("background-color: #555;     border-style: none;  color:white;");

    layout->addWidget(m_lbText);

    QWidget * buttons = new QWidget(this);
    QHBoxLayout * buttonsLayout = new QHBoxLayout(buttons);

    m_btnOK = new QPushButton(buttons);
    m_btnOK->setText("OK");
    m_btnOK->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = m_btnOK->font();
    font.setPointSizeF(23);
    font.setBold(true);
    m_btnOK->setFont(font);
    connect (m_btnOK, &QPushButton::clicked, this, &TutorialScreen::okClicked);

    buttonsLayout->addWidget(m_btnOK);
    buttonsLayout->setContentsMargins(0,0,0,0);

    layout->addWidget(buttons);

    layout->addStretch();
}

void TutorialScreen::keyPressEvent(QKeyEvent *e)
{
    if (e->key() == Qt::Key_Return)
    {
        okClicked();

    }
}


void TutorialScreen::okClicked()
{
    switch (m_step)
    {
    case 1:
        m_lbText->setText("Another text");
        m_step++;
        break;
    case 2:
        this->deleteLater();
        break;
    default:
        assert(false);
        this->deleteLater();
        break;
    }
}

