#include "MenuScreen.h"
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
#include <QFileDialog>
#include <QScroller>

#include "sb/system/Configuration.h"
#include "sb/widgets/DashWidget.h"
#include "sb/widgets/SideButtonLabel.h"

MenuScreen::MenuScreen (MainWidget * parent, PDash dash, PState state) : QScrollArea(parent)
{
    setContentsMargins(5,5,5,5);
    m_dash = dash;
    m_state = state;
    //setMinimumSize(500, 500);
    setStyleSheet("background-color: " + g_globalConfiguration.backgroundColor().name() + ";");

    QWidget * widget = new QWidget();
    widget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

    QVBoxLayout * layout = new QVBoxLayout(widget);

    QPushButton * pbExit = new QPushButton(widget);
    pbExit->setText("EXIT DASH");
    pbExit->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    auto font = pbExit->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbExit->setFont(font);
    connect (pbExit, &QPushButton::clicked, this, &MenuScreen::exitClicked);

    QPushButton * pbReset = new QPushButton(widget);
    pbReset->setText("RESET DATA");
    pbReset->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbReset->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbReset->setFont(font);
    connect (pbReset, &QPushButton::clicked, this, &MenuScreen::resetClicked);


    QPushButton * pbClearRefA = nullptr;
    if (m_state->comparisonLaps.contains("ref-a"))
    {
        pbClearRefA = new QPushButton(widget);
        pbClearRefA->setText("CLEAR REF-A");
        pbClearRefA->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbClearRefA->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbClearRefA->setFont(font);
        connect (pbClearRefA, &QPushButton::clicked, this, &MenuScreen::clearRefAClicked);
    }

    QPushButton * pbSave = nullptr;
    if (m_state->comparisonLaps.contains("best"))
    {
        pbSave = new QPushButton(widget);
        pbSave->setText("SAVE BEST AS REF-A");
        pbSave->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbSave->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbSave->setFont(font);
        connect (pbSave, &QPushButton::clicked, this, &MenuScreen::saveBestClicked);
    }

    QPushButton * pbImport = new QPushButton(widget);
    pbImport->setText("IMPORT REF-A");
    pbImport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbImport->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbImport->setFont(font);
    connect (pbImport, &QPushButton::clicked, this, &MenuScreen::importRefAClicked);

    QPushButton * pbExport = nullptr;
    if (m_state->comparisonLaps.contains("ref-a"))
    {
        pbExport = new QPushButton(widget);
        pbExport->setText("EXPORT REF-A");
        pbExport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbExport->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbExport->setFont(font);
        connect (pbExport, &QPushButton::clicked, this, &MenuScreen::exportRefAClicked);
    }

    SideButtonLabel * pbClose = new SideButtonLabel(widget, SideButtonLabel::Close);
    pbClose->setText("MENU");
    pbClose->setAlignment(Qt::AlignCenter);
    font = pbClose->font();
    font.setPointSizeF(60);
    font.setBold(true);
    pbClose->setFont(font);
    pbClose->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");
    connect (pbClose, &SideButtonLabel::buttonClicked, this, &MenuScreen::closeClicked);

    layout->addWidget(pbClose);
    layout->addWidget(pbReset);
    if (pbClearRefA != nullptr)
    {
        layout->addWidget(pbClearRefA);
    }
    if (pbSave != nullptr)
    {
        layout->addWidget(pbSave);
    }
    layout->addWidget(pbImport);
    if (pbExport != nullptr)
    {
        layout->addWidget(pbExport);
    }

    layout->addWidget(pbExit);
    layout->insertStretch(layout->count()-1);

    setWidget(widget);
    setupScroller(this);
}

MenuScreen::MenuScreen (MainWidget * parent, PDash dash, PComponent comp) : QScrollArea(parent)
{
    setContentsMargins(5,5,5,5);
    m_dash = dash;
    m_component = comp;
    //setMinimumSize(500, 500);
    setStyleSheet("background-color: " + g_globalConfiguration.backgroundColor().name() + ";");

    QWidget * widget = new QWidget();

    QVBoxLayout * layout = new QVBoxLayout(widget);

    m_lbParam = new QLabel(widget);
    auto font = m_lbParam->font();
    font.setPointSizeF(30);
    font.setBold(true);
    m_lbParam->setFont(font);
    updateParams();

    SideButtonLabel * pbClose = new SideButtonLabel(widget, SideButtonLabel::Close);
    pbClose->setText(comp->title().toUpper());
    pbClose->setAlignment(Qt::AlignCenter);
    font = pbClose->font();
    font.setPointSizeF(40);
    font.setBold(true);
    pbClose->setFont(font);
    pbClose->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");
    connect (pbClose, &SideButtonLabel::buttonClicked, this, &MenuScreen::closeClicked);

    layout->addWidget(pbClose);
    layout->addWidget(m_lbParam);

    auto actions = comp->getActions();
    auto actionKeys = actions.keys();
    std::sort(actionKeys.begin(), actionKeys.end(), [actions](QString a, QString b) { return actions[a].order < actions[b].order; });

    for (auto i : actionKeys)
    {
        QPushButton * curButton = new QPushButton(widget);
        curButton->setText (actions[i].label.toUpper());
        curButton->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = curButton->font();
        font.setPointSizeF(23);
        font.setBold(true);
        curButton->setFont(font);
        curButton->setProperty("componentAction", i);
        connect(curButton, &QPushButton::clicked, this, &MenuScreen::actionClicked);
        layout->addWidget(curButton);
    }

    layout->insertStretch(layout->count());
    setWidget(widget);
    setupScroller(this);
}

void MenuScreen::setupScroller(QScrollArea *area)
{
    setWidgetResizable(true);
    QScroller::grabGesture(area->viewport(), QScroller::LeftMouseButtonGesture);
    QVariant OvershootPolicy = QVariant::fromValue<QScrollerProperties::OvershootPolicy>(QScrollerProperties::OvershootAlwaysOff);
    QScrollerProperties ScrollerProperties = QScroller::scroller(area->viewport())->scrollerProperties();
    ScrollerProperties.setScrollMetric(QScrollerProperties::VerticalOvershootPolicy, OvershootPolicy);
    ScrollerProperties.setScrollMetric(QScrollerProperties::HorizontalOvershootPolicy, OvershootPolicy);
    QScroller::scroller(area->viewport())->setScrollerProperties(ScrollerProperties);
}

void MenuScreen::updateParams()
{
    m_lbParam->setText ("Parameters:\n");
    auto boolLabels = m_component->getBooleanParameters();
    for (auto i : boolLabels)
    {
        m_lbParam->setText (m_lbParam->text() + i.name() + ": " + (i() ? "ON" : "OFF") + "\n");
    }

    auto strLabels = m_component->getStringParameters();
    for (auto i : strLabels)
    {
        m_lbParam->setText (m_lbParam->text() + i.name() + ": " + i() + "\n");
    }

    auto fltLabels = m_component->getFloatParameters();
    for (auto i : fltLabels)
    {
        m_lbParam->setText (m_lbParam->text() + i.name() + ": " + QString::number(i()) + "\n");
    }
}

void MenuScreen::actionClicked()
{
    QString action = sender()->property("componentAction").toString();
    DBG_MSG << "Action clicked:" << action;
    m_component->callAction(action);
    updateParams();
}

void MenuScreen::exitClicked()
{
    DBG_MSG << "Exit";
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


void MenuScreen::closeClicked()
{
    DBG_MSG << "Close";
    DBG_MSG << this->size() << this->widget()->size();
    deleteLater();
}

void MenuScreen::resetClicked()
{
    DBG_MSG << "Reset data";
    MainWidget * main = dynamic_cast<MainWidget*> (this->parent());
    main->startDash();
    deleteLater();
}

void MenuScreen::saveBestClicked()
{
    DBG_MSG << "Save lap";
    m_state->saveComparisonLap("best", "ref-a");
    m_state->loadComparisonLap("ref-a", "ref-a");
    //QFileDialog::getOpenFileName();
    deleteLater();
}

void MenuScreen::clearRefAClicked()
{
    if (m_state->comparisonLaps.contains("ref-a"))
    {
        m_state->comparisonLaps.remove("ref-a");
    }
    deleteLater();
}

void MenuScreen::importRefAClicked()
{
    auto filePath = QFileDialog::getOpenFileName(this, "Load lap", QString(), "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Load" << filePath << "as ref-a";
        m_state->loadComparisonLap("ref-a", filePath, true);
        m_state->saveComparisonLap("ref-a", "ref-a");
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}

void MenuScreen::exportRefAClicked()
{
    auto filePath = QFileDialog::getSaveFileName(this, "Save lap", QDate::currentDate().toString("yyyy-MM-dd") + " Reference Lap.gt7lap", "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save" << filePath << "from ref-a";
        m_state->saveComparisonLap("ref-a", filePath, true);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}
