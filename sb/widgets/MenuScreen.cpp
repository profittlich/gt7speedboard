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
#include "sb/widgets/ComponentWidget.h"
#include "sb/components/ComponentFactory.h"

// Abstract menu
MenuScreen::MenuScreen (MainWidget * parent, PDash dash, PState state) : QScrollArea(parent), m_dash(dash), m_state(state)
{
    setContentsMargins(5,5,5,5);
    setStyleSheet("background-color: " + g_globalConfiguration.backgroundColor().name() + ";");

    QWidget * widget = new QWidget();
    widget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

    m_layout = new QVBoxLayout(widget);

    m_pbClose = new SideButtonLabel(widget, SideButtonLabel::Close);
    m_pbClose->setText("MENU");
    m_pbClose->setAlignment(Qt::AlignCenter);
    auto font = m_pbClose->font();
    font.setPointSizeF(60);
    font.setBold(true);
    m_pbClose->setFont(font);
    m_pbClose->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");
    connect (m_pbClose, &SideButtonLabel::buttonClicked, this, &MenuScreen::closeClicked);

    layout()->addWidget(m_pbClose);

    setWidget(widget);
    setupScroller(this);
}

// Main menu
MainMenuScreen::MainMenuScreen (MainWidget * parent, PDash dash, PState pstate) : MenuScreen(parent, dash, pstate)
{
    QPushButton * pbExit = new QPushButton(widget());
    pbExit->setText("EXIT DASH");
    pbExit->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    auto font = pbExit->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbExit->setFont(font);
    connect (pbExit, &QPushButton::clicked, this, &MainMenuScreen::exitClicked);

    QPushButton * pbReset = new QPushButton(widget());
    pbReset->setText("RESET DATA");
    pbReset->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbReset->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbReset->setFont(font);
    connect (pbReset, &QPushButton::clicked, this, &MainMenuScreen::resetClicked);


    QPushButton * pbClearRefA = nullptr;
    if (state()->comparisonLaps.contains("ref-a"))
    {
        pbClearRefA = new QPushButton(widget());
        pbClearRefA->setText("CLEAR REF-A");
        pbClearRefA->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbClearRefA->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbClearRefA->setFont(font);
        connect (pbClearRefA, &QPushButton::clicked, this, &MainMenuScreen::clearRefAClicked);
    }

    QPushButton * pbSave = nullptr;
    if (state()->comparisonLaps.contains("best"))
    {
        pbSave = new QPushButton(widget());
        pbSave->setText("SAVE BEST AS REF-A");
        pbSave->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbSave->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbSave->setFont(font);
        connect (pbSave, &QPushButton::clicked, this, &MainMenuScreen::saveBestClicked);
    }

    QPushButton * pbImport = new QPushButton(widget());
    pbImport->setText("IMPORT REF-A");
    pbImport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = pbImport->font();
    font.setPointSizeF(23);
    font.setBold(true);
    pbImport->setFont(font);
    connect (pbImport, &QPushButton::clicked, this, &MainMenuScreen::importRefAClicked);

    QPushButton * pbExport = nullptr;
    if (state()->comparisonLaps.contains("ref-a"))
    {
        pbExport = new QPushButton(widget());
        pbExport->setText("EXPORT REF-A");
        pbExport->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = pbExport->font();
        font.setPointSizeF(23);
        font.setBold(true);
        pbExport->setFont(font);
        connect (pbExport, &QPushButton::clicked, this, &MainMenuScreen::exportRefAClicked);
    }

    layout()->addWidget(pbReset);
    if (pbClearRefA != nullptr)
    {
        layout()->addWidget(pbClearRefA);
    }
    if (pbSave != nullptr)
    {
        layout()->addWidget(pbSave);
    }
    layout()->addWidget(pbImport);
    if (pbExport != nullptr)
    {
        layout()->addWidget(pbExport);
    }

    layout()->addWidget(pbExit);
    layout()->insertStretch(layout()->count()-1);
}

// Component context menu
ComponentContextMenuScreen::ComponentContextMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp) : MenuScreen(parent, dash, state)
{
    m_component = comp;

    setTitle(comp->title());

    m_lbParam = new QLabel(widget());
    auto font = m_lbParam->font();
    font.setPointSizeF(30);
    font.setBold(true);
    m_lbParam->setFont(font);
    updateParams();

    QPushButton * replaceButton = new QPushButton(widget());
    replaceButton->setText ("REPLACE");
    replaceButton->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
    font = replaceButton->font();
    font.setPointSizeF(23);
    font.setBold(true);
    replaceButton->setFont(font);
    connect(replaceButton, &QPushButton::clicked, this, &ComponentContextMenuScreen::replaceClicked);

    layout()->addWidget(replaceButton);
    layout()->addWidget(m_lbParam);

    auto actions = comp->getActions();
    auto actionKeys = actions.keys();
    std::sort(actionKeys.begin(), actionKeys.end(), [actions](QString a, QString b) { return actions[a].order < actions[b].order; });

    for (auto i : actionKeys)
    {
        QPushButton * curButton = new QPushButton(widget());
        curButton->setText (actions[i].label.toUpper());
        curButton->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        font = curButton->font();
        font.setPointSizeF(23);
        font.setBold(true);
        curButton->setFont(font);
        curButton->setProperty("componentAction", i);
        connect(curButton, &QPushButton::clicked, this, &ComponentContextMenuScreen::actionClicked);
        layout()->addWidget(curButton);
    }

    layout()->insertStretch(layout()->count());
}

// Component replace/select menu
ComponentSelectionMenuScreen::ComponentSelectionMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp) : MenuScreen(parent, dash, state)
{
    m_component = comp;

    setTitle("REPLACE");

    auto comps = ComponentFactory::listComponents();
    for (auto i : comps)
    {
        if (!ComponentFactory::componentHasWidget(i))
        {
            continue;
        }
        QPushButton * curButton = new QPushButton(widget());
        curButton->setText (i);
        curButton->setStyleSheet ("height: 100px; background-color: #555;     border-style: none;  color:white;");
        auto font = curButton->font();
        font.setPointSizeF(23);
        font.setBold(true);
        curButton->setFont(font);
        curButton->setProperty("componentKey", i);
        connect(curButton, &QPushButton::clicked, this, &ComponentSelectionMenuScreen::componentClicked);
        layout()->addWidget(curButton);
    }
}

void MenuScreen::setTitle (QString t)
{
    m_pbClose->setText(t);
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

void ComponentContextMenuScreen::updateParams()
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

void ComponentContextMenuScreen::actionClicked()
{
    QString action = sender()->property("componentAction").toString();
    DBG_MSG << "Action clicked:" << action;
    m_component->callAction(action);
    updateParams();
}

void ComponentContextMenuScreen::replaceClicked()
{
    DBG_MSG << "Replace component";
    MainWidget * mw = dynamic_cast<MainWidget*> (parent());
    MenuScreen * men = new ComponentSelectionMenuScreen (mw, dash(), state(), m_component);
    mw->m_layout->insertWidget(0,men);
    mw->m_layout->setCurrentIndex(0);

    deleteLater();
}

void ComponentSelectionMenuScreen::componentClicked()
{
    MainWidget * mw = dynamic_cast<MainWidget*> (parent());
    QString key = sender()->property("componentKey").toString();
    PComponent newComponent = ComponentFactory::createComponent(key);
    if (newComponent.isNull())
    {
        DBG_MSG << "Unknown component";
    }
    else
    {
        dash()->replaceComponent(m_component, newComponent, mw);
        newComponent->setState(state());
    }
    deleteLater();
}

void MainMenuScreen::exitClicked()
{
    DBG_MSG << "Exit";
    if (!dash().isNull())
    {
        dash()->widget->exitDash();
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
    //DBG_MSG << this->size() << this->widget()->size();
    deleteLater();
}

void MainMenuScreen::resetClicked()
{
    DBG_MSG << "Reset data";
    MainWidget * main = dynamic_cast<MainWidget*> (this->parent());
    main->startDash();
    deleteLater();
}

void MainMenuScreen::saveBestClicked()
{
    DBG_MSG << "Save lap";
    state()->saveComparisonLap("best", "ref-a");
    state()->loadComparisonLap("ref-a", "ref-a");
    //QFileDialog::getOpenFileName();
    deleteLater();
}

void MainMenuScreen::clearRefAClicked()
{
    if (state()->comparisonLaps.contains("ref-a"))
    {
        state()->comparisonLaps.remove("ref-a");
    }
    deleteLater();
}

void MainMenuScreen::importRefAClicked()
{
    auto filePath = QFileDialog::getOpenFileName(this, "Load lap", QString(), "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Load" << filePath << "as ref-a";
        state()->loadComparisonLap("ref-a", filePath, true);
        state()->saveComparisonLap("ref-a", "ref-a");
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}

void MainMenuScreen::exportRefAClicked()
{
    auto filePath = QFileDialog::getSaveFileName(this, "Save lap", QDate::currentDate().toString("yyyy-MM-dd") + " Reference Lap.gt7lap", "Laps (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save" << filePath << "from ref-a";
        state()->saveComparisonLap("ref-a", filePath, true);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}
