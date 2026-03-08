#include "StartScreen.h"
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

StartScreen::StartScreen (QWidget * parent) : QWidget(parent)
{
#if !defined(Q_OS_IOS) && !defined(Q_OS_ANDROID)
    setMinimumSize(500, 500);
#endif

    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");

    QVBoxLayout * layout = new QVBoxLayout(this);

    m_lbHead = new ImageLabel(this);
    m_lbHead->setAlignment(Qt::AlignmentFlag::AlignCenter | Qt::AlignmentFlag::AlignHCenter);
    QPixmap logo = QPixmap(":/assets/assets/SpeedBoard_Logo_black_trans.png");
    QRect logoCrop (logo.width() * 0.25, logo.height() * 0.25, logo.width() * 0.5, logo.height() * 0.5);
    m_lbHead->setPixmap(logo.copy(logoCrop));
    layout->addWidget(m_lbHead);

    QLabel * lbLay = new QLabel(this);
    lbLay->setText ("Dashboard layout:");
    layout->addWidget(lbLay);

    m_selectedLayout = new QComboBox(this);

    QDir storeLoc = getStorageLocation();
    m_selectedLayout->addItem("Last used layout", storeLoc.absolutePath() + "/Last Used.sblayout");


    auto fnt = m_selectedLayout->font();
    fnt.setPointSize(20);
    m_selectedLayout->setFont(fnt);
    m_selectedLayout->setMinimumHeight(30);
    //m_selectedLayout->setStyleSheet("border-style:auto;");

    QDir layoutFiles = QDir(":/assets/assets/");
    auto files = layoutFiles.entryList({"*.sblayout"});
    for (const auto &i : std::as_const(files))
    {
        m_selectedLayout->addItem((i.first(i.size() - strlen (".sblayout"))).replace("_", " "), ":/assets/assets/" + i);
    }

    layoutFiles = QDir(storeLoc.absolutePath());
    files = layoutFiles.entryList({"*.sblayout"});
    for (const auto &i : std::as_const(files))
    {
        m_selectedLayout->addItem((i.first(i.size() - strlen (".sblayout"))).replace("_", " "), storeLoc.absolutePath() + "/" + i);
    }

    layout->addWidget(m_selectedLayout);
    connect(m_selectedLayout, &QComboBox::currentIndexChanged, this, &StartScreen::selectLayout);
    selectLayout(0);

    QLabel * lbIP = new QLabel(this);
    lbIP->setText ("PlayStation address:");
    layout->addWidget(lbIP);

    m_leIP = new QLineEdit (this);
    m_leIP->setText(g_globalConfiguration.hostAddress());
    //m_leIP->setStyleSheet("background-color:#0000;");
    fnt = m_leIP->font();
    fnt.setPointSize(20);
    m_leIP->setFont(fnt);
    m_leIP->setMinimumHeight(30);
    layout->addWidget(m_leIP);

    QLabel * lbFont = new QLabel(this);
    lbFont->setText ("Font size:");
    layout->addWidget(lbFont);

    auto sbFont = new QSpinBox(this);
    sbFont->setMinimum(10);
    sbFont->setMaximum(300);
    sbFont->setValue(g_globalConfiguration.fontScale()*100/g_globalConfiguration.platformFontScale());
    sbFont->setSuffix("%");
    fnt = sbFont->font();
    fnt.setPointSize(20);
    sbFont->setFont(fnt);
    sbFont->setMinimumHeight(30);
    layout->addWidget(sbFont);
    //sbFont->setStyleSheet("background-color:#0000;");
    connect(sbFont, &QSpinBox::valueChanged, this, &StartScreen::setFontSize);

//layout->addStretch();

    QPushButton * pbStart = new QPushButton(this);
    pbStart->setText("START");
    pbStart->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    auto font = pbStart->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbStart->setFont(font);
    connect (pbStart, &QPushButton::clicked, this, &StartScreen::startDashClicked);

    layout->addWidget(pbStart);
}

void StartScreen::selectLayout(unsigned idx)
{
    DBG_MSG << "Layout: " << m_selectedLayout->itemData(idx).toString();
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

    //m_lbHead->setPixmap(QPixmap(":/assets/assets/SpeedBoard_Logo_black_trans.png").scaled (targetSize, targetSize, Qt::KeepAspectRatio, Qt::SmoothTransformation));
}

void StartScreen::startDashClicked()
{
    QSettings settings;
    settings.setValue("ip", m_leIP->text());
    settings.setValue("fontScale", g_globalConfiguration.fontScale());
    settings.sync();

    g_globalConfiguration.setHostAddress(m_leIP->text());

    emit startDash();

}

void StartScreen::setFontSize(float size)
{
    g_globalConfiguration.setFontScale(size/100.0);
}
