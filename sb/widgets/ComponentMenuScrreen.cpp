#include "ComponentMenuScreen.h"
#include "sb/components/ComponentFactory.h"

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
