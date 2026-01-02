#include "StartScreen.h"

#include <QtLogging>
#include <QVBoxLayout>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QResizeEvent>
#include <QStandardPaths>
#include <QComboBox>
#include <QDir>

#include "sb/system/Configuration.h"

StartScreen::StartScreen (QWidget * parent) : QWidget(parent)
{
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");

    QVBoxLayout * layout = new QVBoxLayout(this);
    m_lbHead = new QLabel(this);
    QFont font = m_lbHead->font();
    font.setPointSize(20);
    m_lbHead->setFont(font);
    //lbHead->setText ("SpeedBoard for GT7");
    m_lbHead->setAlignment(Qt::AlignmentFlag::AlignCenter | Qt::AlignmentFlag::AlignHCenter);
    m_lbHead->setPixmap(QPixmap(":/assets/assets/SpeedBoard_Logo_black_trans.png").scaled(300, 300, Qt::KeepAspectRatio, Qt::SmoothTransformation));


    //lbHead->setStyleSheet("height:300px;");
    layout->addWidget(m_lbHead);

    layout->addStretch();

    QLabel * lbLay = new QLabel(this);
    lbLay->setText ("Dashboard layout:");
    layout->addWidget(lbLay);

    m_selectedLayout = new QComboBox(this);
#if 0
#ifdef Q_OS_IOS
    m_selectedLayout->addItem("Last used layout", QStandardPaths::standardLocations(QStandardPaths::StandardLocation::DocumentsLocation)[0] + "/Documents/Last Used.sblayout");
#else
    m_selectedLayout->addItem("Last used layout", QStandardPaths::standardLocations(QStandardPaths::StandardLocation::AppDataLocation)[0] + "/Last Used.sblayout");
#endif
#endif

    QDir layoutFiles = QDir(":/assets/assets/");
    auto files = layoutFiles.entryList({"*.sblayout"});
    for (auto i : files)
    {
        m_selectedLayout->addItem(i.first(i.size() - strlen (".sblayout")), ":/assets/assets/" + i);
    }
    layout->addWidget(m_selectedLayout);
    connect(m_selectedLayout, &QComboBox::currentIndexChanged, this, &StartScreen::selectLayout);
    selectLayout(0);

    QLabel * lbIP = new QLabel(this);
    lbIP->setText ("PlayStation address:");
    layout->addWidget(lbIP);

    m_leIP = new QLineEdit (this);
    m_leIP->setText(g_globalConfiguration.hostAddress());
    m_leIP->setStyleSheet("background-color:#eee; color:black;");
    layout->addWidget(m_leIP);
    layout->addStretch();

    QPushButton * pbStart = new QPushButton(this);
    pbStart->setText("START");
    pbStart->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbStart->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbStart->setFont(font);
    connect (pbStart, &QPushButton::clicked, this, &StartScreen::startDashClicked);

    layout->addWidget(pbStart);
}

void StartScreen::selectLayout(unsigned idx)
{
    qDebug() << "Layout: " << m_selectedLayout->itemData(idx).toString();
    g_globalConfiguration.setSelectedLayout(m_selectedLayout->itemData(idx).toString());
}

void StartScreen::resizeEvent(QResizeEvent * e)
{
    unsigned targetSize = e->size().width();
    if (e->size().height() < targetSize)
    {
        targetSize = e->size().height();
    }
    targetSize *= 0.9;
    //qInfo("TS: %d %d %d", e->size().width(), e->size().height(), targetSize);
    //m_lbHead->setPixmap(QPixmap(":/assets/assets/SpeedBoard_Logo_black_trans.png").scaled (targetSize, targetSize, Qt::KeepAspectRatio, Qt::SmoothTransformation));
}

void StartScreen::startDashClicked()
{
    QSettings settings;
    settings.setValue("ip", m_leIP->text());
    settings.sync();

    g_globalConfiguration.setHostAddress(m_leIP->text());

    emit startDash();

}
