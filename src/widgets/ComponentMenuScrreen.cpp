#include "ComponentMenuScreen.h"
#include "src/components/ComponentFactory.h"
#include "src/widgets/TextInput.h"

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
    m_boolParameters.clear();
    m_stringParameters.clear();
    m_intParameters.clear();
    m_floatParameters.clear();

    // remove spacer temporarily
    layout()->removeItem(layout()->itemAt(layout()->count()-1));

    auto boolLabels = m_component->getBooleanParameters();
    for (auto i : std::as_const(boolLabels))
    {
        m_boolParameters.insert(i.name(),i);
        QPushButton * curButton = addButton (i.name() + ": " + (i() ? "ON" : "OFF"), this, &ComponentContextMenuScreen::paramClicked);
        curButton->setProperty("paramKey", i.name());
        m_paramItems.push_back(curButton);
    }

    auto strLabels = m_component->getStringParameters();
    for (auto i : std::as_const(strLabels))
    {
        m_stringParameters.insert(i.name(),i);
        QPushButton * curButton = addButton (i.name() + ": " + i(), this, &ComponentContextMenuScreen::paramClicked);
        curButton->setProperty("paramKey", i.name());
        m_paramItems.push_back(curButton);
    }

    auto fltLabels = m_component->getFloatParameters();
    for (auto i : std::as_const(fltLabels))
    {
        m_floatParameters.insert(i.name(),i);
        QPushButton * curButton = addButton (i.name() + ": " + QString::number(i()), this, &ComponentContextMenuScreen::paramClicked);
        curButton->setProperty("paramKey", i.name());
        m_paramItems.push_back(curButton);
    }

    auto intLabels = m_component->getIntParameters();
    for (auto i : std::as_const(intLabels))
    {
        m_intParameters.insert(i.name(),i);
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
    QString paramKey = sender()->property("paramKey").toString();

    if (m_boolParameters.contains(paramKey))
    {
        DBG_MSG << "BOOL Param clicked:" << paramKey;
        ComponentParameter<bool> p = *m_boolParameters.find(paramKey);
        p() = !p();
        m_component->setBooleanParameter(p);
        updateParams();
    }
    else if (m_stringParameters.contains(paramKey))
    {
        DBG_MSG << "STRING Param clicked:" << paramKey;
        ComponentParameter<QString> p = *m_stringParameters.find(paramKey);
        MainWidget * mw = dynamic_cast<MainWidget*> (parent());
        TextInput * inp = new TextInput(mw, p.name(), p());
        connect(inp, &TextInput::ok, this, &ComponentContextMenuScreen::textInputOk);
        connect(inp, &TextInput::cancelled, this, &ComponentContextMenuScreen::textInputCancelled);

        mw->m_layout->insertWidget(0,inp);
        mw->m_layout->setCurrentIndex(0);
    }
    else if (m_floatParameters.contains(paramKey))
    {
        DBG_MSG << "FLOAT Param clicked:" << paramKey;
        ComponentParameter<float> p = *m_floatParameters.find(paramKey);
        MainWidget * mw = dynamic_cast<MainWidget*> (parent());
        TextInput * inp = new TextInput(mw, p.name(), QString::number(p()), new QDoubleValidator(this));
        connect(inp, &TextInput::ok, this, &ComponentContextMenuScreen::textInputOk);
        connect(inp, &TextInput::cancelled, this, &ComponentContextMenuScreen::textInputCancelled);

        mw->m_layout->insertWidget(0,inp);
        mw->m_layout->setCurrentIndex(0);
    }
    else if (m_intParameters.contains(paramKey))
    {
        DBG_MSG << "INT Param clicked:" << paramKey;
        ComponentParameter<int> p = *m_intParameters.find(paramKey);
        MainWidget * mw = dynamic_cast<MainWidget*> (parent());
        TextInput * inp = new TextInput(mw, p.name(), QString::number(p()), new QIntValidator(this));
        connect(inp, &TextInput::ok, this, &ComponentContextMenuScreen::textInputOk);
        connect(inp, &TextInput::cancelled, this, &ComponentContextMenuScreen::textInputCancelled);

        mw->m_layout->insertWidget(0,inp);
        mw->m_layout->setCurrentIndex(0);
    }
}

void ComponentContextMenuScreen::textInputOk()
{
    TextInput *inp = dynamic_cast<TextInput*> (sender());
    DBG_MSG << "Result:" << inp->getTitle() << inp->getResult();
    if (m_stringParameters.contains(inp->getTitle()))
    {
        ComponentParameter<QString> p = *m_stringParameters.find(inp->getTitle());
        p() = inp->getResult();
        m_component->setStringParameter(p);
    }
    else if (m_floatParameters.contains(inp->getTitle()))
    {
        ComponentParameter<float> p = *m_floatParameters.find(inp->getTitle());
        p() = inp->getResult().toFloat();
        m_component->setFloatParameter(p);
    }
    else if (m_intParameters.contains(inp->getTitle()))
    {
        ComponentParameter<int> p = *m_intParameters.find(inp->getTitle());
        p() = inp->getResult().toInt();
        m_component->setIntParameter(p);
    }
    updateParams();
    inp->deleteLater();
}

void ComponentContextMenuScreen::textInputCancelled()
{
    TextInput *inp = dynamic_cast<TextInput*> (sender());
    inp->deleteLater();
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
