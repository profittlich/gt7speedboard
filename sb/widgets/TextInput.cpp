#include "TextInput.h"
#include "sb/system/Configuration.h"
#include <QtWidgets/qboxlayout.h>
#include <QTimer>
#include <QKeyEvent>

TextInput::TextInput(QWidget *parent, QString title, QString init)
{
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");

    QVBoxLayout * layout = new QVBoxLayout(this);

    QLabel * lbTitle = new QLabel(this);
    lbTitle->setText (title);

    lbTitle->setAlignment(Qt::AlignCenter);
    auto font = lbTitle->font();
    font.setPointSizeF(30);
    font.setBold(true);
    lbTitle->setFont(font);
    lbTitle->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");

    layout->addWidget(lbTitle);

    m_leText = new QLineEdit (this);
    m_leText->setText(init);
    //m_leIP->setStyleSheet("background-color:#0000;");
    auto fnt = m_leText->font();
    fnt.setPointSize(20);
    m_leText->setFont(fnt);
    m_leText->setMinimumHeight(30);
    m_leText->setStyleSheet ("background-color: #555;     border-style: none;  color:white;");

    layout->addWidget(m_leText);

    QWidget * buttons = new QWidget(this);
    QHBoxLayout * buttonsLayout = new QHBoxLayout(buttons);

    m_btnOK = new QPushButton(buttons);
    m_btnOK->setText("OK");
    m_btnOK->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = m_btnOK->font();
    font.setPointSizeF(23);
    font.setBold(true);
    m_btnOK->setFont(font);
    connect (m_btnOK, &QPushButton::clicked, this, &TextInput::okClicked);

    buttonsLayout->addWidget(m_btnOK);

    m_btnCancel = new QPushButton(buttons);
    m_btnCancel->setText("Cancel");
    m_btnCancel->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = m_btnCancel->font();
    font.setPointSizeF(23);
    font.setBold(true);
    m_btnCancel->setFont(font);
    connect (m_btnCancel, &QPushButton::clicked, this, &TextInput::cancelClicked);

    buttonsLayout->setContentsMargins(0,0,0,0);
    buttonsLayout->addWidget(m_btnCancel);

    layout->addWidget(buttons);

    layout->addStretch();

    QTimer::singleShot(0, m_leText, SLOT(setFocus()));
}

void TextInput::keyPressEvent(QKeyEvent *e)
{
    if (e->key() == Qt::Key_Escape) {
        emit cancelled();
    }
    else if (e->key() == Qt::Key_Return)
    {
        emit ok();
    }
}

QString TextInput::getResult()
{
    return m_leText->text();
}

void TextInput::okClicked()
{
    DBG_MSG << "OK with:" << m_leText->text();
    emit ok();
}

void TextInput::cancelClicked()
{
    DBG_MSG << "Cancel with:" << m_leText->text();
    emit cancelled();
}