#include "StartScreen.h"
#include "src/system/Helpers.h"
#include "TextInput.h"

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
#include <QFileDialog>

#include "src/system/Configuration.h"

StartScreen::StartScreen (QWidget * parent, QStackedLayout *parentLayout) : QWidget(parent)
{
    m_parent = parent;
    m_parentLayout = parentLayout;
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
    m_selectedLayout->setStyleSheet ("height: 30px; background-color: #555;     border-style: none;  color:white; text-align:left;");

    auto fnt = m_selectedLayout->font();
    fnt.setPointSize(20);
    m_selectedLayout->setFont(fnt);
    m_selectedLayout->setMinimumHeight(30);
    //m_selectedLayout->setStyleSheet("border-style:auto;");

    QDir storeLoc = getStorageLocation();
    QFile llTest (storeLoc.absolutePath() + "/Last Used.sblayout.autosave");
    if (llTest.exists())
    {
        m_selectedLayout->addItem("Last used layout", storeLoc.absolutePath() + "/Last Used.sblayout.autosave");
        m_selectedLayout->insertSeparator(m_selectedLayout->count());
    }


    QDir layoutFiles = QDir(":/assets/assets/");
    auto files = layoutFiles.entryList({"*.sblayout"});
    for (const auto &i : std::as_const(files))
    {
        m_selectedLayout->addItem((i.first(i.size() - strlen (".sblayout"))).replace("_", " "), ":/assets/assets/" + i);
    }

    m_selectedLayout->insertSeparator(m_selectedLayout->count());

    layoutFiles = QDir(storeLoc.absolutePath());
    files = layoutFiles.entryList({"*.sblayout"});
    for (const auto &i : std::as_const(files))
    {
        m_selectedLayout->addItem((i.first(i.size() - strlen (".sblayout"))).replace("_", " "), storeLoc.absolutePath() + "/" + i);
    }

    m_selectedLayout->insertSeparator(m_selectedLayout->count());
    m_selectedLayout->addItem("Import...", "<IMPORT>");

    layout->addWidget(m_selectedLayout);
    connect(m_selectedLayout, &QComboBox::currentIndexChanged, this, &StartScreen::selectLayout);
    selectLayout(0);

    QLabel * lbIP = new QLabel(this);
    lbIP->setText ("PlayStation address:");
    layout->addWidget(lbIP);

    m_btnIP = new QPushButton(this);
    m_btnIP->setText(g_globalConfiguration.hostAddress());
    m_btnIP->setStyleSheet ("height: 30px; background-color: #555;     border-style: none;  color:white; text-align:left;");
    auto font = m_btnIP->font();
    font.setPointSizeF(23);
    font.setBold(false);
    m_btnIP->setFont(font);
    connect (m_btnIP, &QPushButton::clicked, this, &StartScreen::editIP);

    layout->addWidget(m_btnIP);

    QLabel * lbFont = new QLabel(this);
    lbFont->setText ("Font size:");
    layout->addWidget(lbFont);

    /*
    auto sbFont = new QSpinBox(this);
    sbFont->setMinimum(25);
    sbFont->setMaximum(300);
    sbFont->setValue(g_globalConfiguration.globalFontScale()*100);
    sbFont->setSuffix("%");
    fnt = sbFont->font();
    fnt.setPointSize(20);
    sbFont->setFont(fnt);
    sbFont->setMinimumHeight(30);
    layout->addWidget(sbFont);
    sbFont->setStyleSheet ("background-color: #555;     border-style: none;  color:white;");
    //sbFont->setStyleSheet("background-color:#0000;");
    connect(sbFont, &QSpinBox::valueChanged, this, &StartScreen::setFontSize);
    */

    auto cbFont = new QComboBox(this);
    cbFont->setStyleSheet ("background-color: #555;     border-style: none;  color:white;");
    fnt = cbFont->font();
    fnt.setPointSize(20);
    cbFont->setFont(fnt);
    cbFont->setMinimumHeight(30);
    cbFont->addItem("25%", 25);
    cbFont->addItem("50%", 50);
    cbFont->addItem("75%", 75);
    cbFont->addItem("100%", 100);
    cbFont->addItem("125%", 125);
    cbFont->addItem("150%", 150);
    cbFont->addItem("200%", 200);
    cbFont->addItem("250%", 250);
    cbFont->addItem("300%", 300);

    cbFont->setCurrentIndex(3);

    float curSize = g_globalConfiguration.globalFontScale()*100;
    if (curSize < 26)
    {
        cbFont->setCurrentIndex(0);
    }
    else if (curSize < 51)
    {
        cbFont->setCurrentIndex(1);
    }
    else if (curSize < 76)
    {
        cbFont->setCurrentIndex(2);
    }
    else if (curSize < 101)
    {
        cbFont->setCurrentIndex(3);
    }
    else if (curSize < 126)
    {
        cbFont->setCurrentIndex(4);
    }
    else if (curSize < 151)
    {
        cbFont->setCurrentIndex(5);
    }
    else if (curSize < 201)
    {
        cbFont->setCurrentIndex(6);
    }
    else if (curSize < 251)
    {
        cbFont->setCurrentIndex(7);
    }
    else if (curSize < 301)
    {
        cbFont->setCurrentIndex(8);
    }
    connect(cbFont, &QComboBox::currentIndexChanged, this, &StartScreen::selectFontSize);
    layout->addWidget(cbFont);



//layout->addStretch();

    QPushButton * pbStart = new QPushButton(this);
    pbStart->setText("START");
    pbStart->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbStart->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbStart->setFont(font);
    connect (pbStart, &QPushButton::clicked, this, &StartScreen::startDashClicked);

    layout->addWidget(pbStart);

    QLabel * lbVersion = new QLabel(this);
    lbVersion->setText("SpeedBoard for GT7 " + c_version);
    lbVersion->setStyleSheet("color:#777");
    layout->addWidget(lbVersion);
}

void StartScreen::selectLayout(unsigned idx)
{
    auto sel = m_selectedLayout->itemData(idx).toString();
    DBG_MSG << "Layout: " << sel;
    if (sel == "<IMPORT>")
    {
        DBG_MSG << "Import layout";
        auto filePath = QFileDialog::getOpenFileName(this, "Load layout", QString(), "Dashboard Layout (*.sblayout)");
        if(!filePath.isNull())
        {
            QFileInfo inf(filePath);
            QFile f(filePath);
            auto storeLoc = getStorageLocation().absolutePath();
            f.copy(storeLoc + "/" + inf.fileName());

            m_selectedLayout->addItem((inf.fileName().first(inf.fileName().size() - strlen (".sblayout"))).replace("_", " "), storeLoc + "/" + inf.fileName());
            m_selectedLayout->setCurrentIndex(m_selectedLayout->count()-1);

        }
        else
        {
            DBG_MSG << "No file selected";
            m_selectedLayout->setCurrentIndex(0);
        }
    }
    else
    {
        g_globalConfiguration.setSelectedLayout(m_selectedLayout->itemData(idx).toString());
    }
}

void StartScreen::editIP()
{
    TextInput * inp = new TextInput(m_parent, "PlayStation IP", g_globalConfiguration.hostAddress());
    connect(inp, &TextInput::ok, this, &StartScreen::gotNewIP);
    connect(inp, &TextInput::cancelled, this, &StartScreen::textInputCancelled);
    m_parentLayout->insertWidget(0,inp);
    m_parentLayout->setCurrentIndex(0);

}

void StartScreen::gotNewIP()
{
    TextInput *inp = dynamic_cast<TextInput*> (sender());
    m_btnIP->setText(inp->getResult());
    DBG_MSG << "New IP:" << inp->getResult();
    inp->deleteLater();
}

void StartScreen::textInputCancelled()
{
    TextInput *inp = dynamic_cast<TextInput*> (sender());
    inp->deleteLater();
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
    settings.setValue("ip", m_btnIP->text());
    settings.setValue("fontScale", g_globalConfiguration.globalFontScale());
    settings.sync();

    g_globalConfiguration.setHostAddress(m_btnIP->text());

    emit startDash();

}

void StartScreen::selectFontSize(int idx)
{
    QComboBox * cbFont = dynamic_cast<QComboBox*>(sender());
    float size = cbFont->currentData().toFloat();
    setFontSize(size);
}

void StartScreen::setFontSize(float size)
{
    g_globalConfiguration.setFontScale(size/100.0);
}
