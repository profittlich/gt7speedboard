#include "ComponentMenuScreen.h"
#include "src/components/ComponentFactory.h"

// Component context menu
ComponentContextMenuScreen::ComponentContextMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp) : MenuScreen(parent, dash, state)
{
    m_component = comp;

    setTitle(comp->title().toUpper());

    addButton("REPLACE", this, &ComponentContextMenuScreen::replaceClicked);

    auto lbActions = new QLabel(widget());
    auto font = lbActions->font();
    font.setPointSizeF(30);
    font.setBold(true);
    lbActions->setFont(font);
    lbActions->setStyleSheet ("height: 100px;     border-style: none;  color:white;");
    lbActions->setText("Actions:");
    layout()->addWidget(lbActions);

    auto actions = comp->getActions();
    auto actionKeys = actions.keys();
    std::sort(actionKeys.begin(), actionKeys.end(), [actions](QString a, QString b) { return actions[a].order < actions[b].order; });

    for (auto & i : std::as_const(actionKeys))
    {
        QPushButton * curButton = addButton (actions[i].label.toUpper(), this, &ComponentContextMenuScreen::actionClicked);
        curButton->setProperty("componentAction", i);
    }

    m_lbParam = new QLabel(widget());
    font = m_lbParam->font();
    font.setPointSizeF(30);
    font.setBold(true);
    m_lbParam->setFont(font);
    m_lbParam->setStyleSheet ("height: 100px;     border-style: none;  color:white;");
    m_lbParam->setText ("Parameters:");
    layout()->addWidget(m_lbParam);

    layout()->insertStretch(layout()->count());

    updateParams();
}

// Component replace/select menu
ComponentSelectionMenuScreen::ComponentSelectionMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp) : MenuScreen(parent, dash, state)
{
    m_component = comp;

    setTitle("REPLACE");

    auto comps = ComponentFactory::listComponents();
    for (auto & i : std::as_const(comps))
    {
        if (!ComponentFactory::componentHasWidget(i))
        {
            continue;
        }
        QPushButton * curButton = addButton(i, this, &ComponentSelectionMenuScreen::componentClicked);
        curButton->setProperty("componentKey", i);

    }
}


void ComponentContextMenuScreen::updateParams()
{
    for (auto i : std::as_const(m_paramItems))
    {
        delete i;
    }
    m_paramItems.clear();

    // remove spacer temporarily
    layout()->removeItem(layout()->itemAt(layout()->count()-1));

    auto boolLabels = m_component->getBooleanParameters();
    for (auto i : std::as_const(boolLabels))
    {
        QPushButton * curButton = addButton (i.name() + ": " + (i() ? "ON" : "OFF"), this, &ComponentContextMenuScreen::paramClicked);
        curButton->setProperty("paramKey", i.name());
        m_paramItems.push_back(curButton);
    }

    auto strLabels = m_component->getStringParameters();
    for (auto i : std::as_const(strLabels))
    {
        QPushButton * curButton = addButton (i.name() + ": " + i(), this, &ComponentContextMenuScreen::paramClicked);
        curButton->setProperty("paramKey", i.name());
        m_paramItems.push_back(curButton);
    }

    auto fltLabels = m_component->getFloatParameters();
    for (auto i : std::as_const(fltLabels))
    {
        QPushButton * curButton = addButton (i.name() + ": " + QString::number(i()), this, &ComponentContextMenuScreen::paramClicked);
        curButton->setProperty("paramKey", i.name());
        m_paramItems.push_back(curButton);
    }

    auto intLabels = m_component->getIntParameters();
    for (auto i : std::as_const(intLabels))
    {
        QPushButton * curButton = addButton (i.name() + ": " + QString::number(i()), this, &ComponentContextMenuScreen::paramClicked);
        curButton->setProperty("paramKey", i.name());
        m_paramItems.push_back(curButton);
    }

    // re-add spacer
    layout()->insertStretch(layout()->count());
}

void ComponentContextMenuScreen::actionClicked()
{
    QString action = sender()->property("componentAction").toString();
    DBG_MSG << "Action clicked:" << action;
    m_component->callAction(action);
    updateParams();
}

void ComponentContextMenuScreen::paramClicked()
{
    QString action = sender()->property("paramKey").toString();
    DBG_MSG << "Param clicked:" << action;
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
