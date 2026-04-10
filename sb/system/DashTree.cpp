#include "DashTree.h"

#include "sb/widgets/ComponentWidget.h"
#include "MainWidget.h"

QJsonValue DashComponent::toJson()
{
    QJsonObject result;// = m_json.toObject();

    result.insert("component", m_component->getComponentId());

    auto additionalFields = getFields();
    DBG_MSG << additionalFields.size() << "additional fields";
    for (auto i : additionalFields.keys()) {
        result.insert(i, additionalFields[i]);
    }

    QJsonObject conf;
    QMap<QString, QJsonObject> presets;

    bool found = false;
    for (auto i : m_component->getBooleanParameters())
    {
        found = true;
        conf.insert(i.name(), i());
        QMap<QString, bool> all = i.getAll();
        for (auto j : all.keys())
        {
            if (!presets.contains(j))
            {
                presets[j] = QJsonObject();
            }
            presets[j].insert(i.name(), all[j]);
        }
    }
    for (auto i : m_component->getFloatParameters())
    {
        found = true;
        conf.insert(i.name(), i());
        QMap<QString, float> all = i.getAll();
        for (auto j : all.keys())
        {
            if (!presets.contains(j))
            {
                presets[j] = QJsonObject();
            }
            presets[j].insert(i.name(), all[j]);
        }
    }
    for (auto i : m_component->getStringParameters())
    {
        found = true;
        conf.insert(i.name(), i());
        QMap<QString, QString> all = i.getAll();
        for (auto j : all.keys())
        {
            if (!presets.contains(j))
            {
                presets[j] = QJsonObject();
            }
            presets[j].insert(i.name(), all[j]);
        }
    }

    if (found)
    {
        if (!presets.empty())
        {
            QJsonObject preVal;
            for (auto j : presets.keys())
            {
                preVal.insert(j, presets[j]);
            }
            conf.insert("presets", preVal);
        }
        result.insert("configuration", conf);
    }
    return QJsonValue(result);
}

bool DashComponent::replaceComponent(PComponent oldComponent, PComponent newComponent, QWidget * target)
{
    if (oldComponent != m_component)
    {
        return false;
    }

    MainWidget * mw = dynamic_cast<MainWidget*> (target);

    ComponentWidget * newWidget = new ComponentWidget(m_widget->dash(), newComponent, m_widget->backButton(), m_widget->showHeader(), m_widget->title());
    DBG_MSG << "Layout ptr = " << m_widget->layout();
    if (m_widget->layout() != nullptr)
    {
        newWidget->setLayout(m_widget->layout());
        m_widget->layout()->replaceWidget(m_widget, newWidget);
    }
    else if (m_widget->stack() != nullptr)
    {
        auto stack = m_widget->stack();
        auto curIdx = stack->indexOf (m_widget);

        newWidget->setStack(m_widget->stack());

        stack->removeWidget(m_widget);
        stack->insertWidget(curIdx, newWidget);
        stack->setCurrentIndex(curIdx);
    }
    else
    {
        DBG_MSG << "Widget neither in Layout nor Stack";
        newWidget->deleteLater();
        return false;
    }
    m_widget->deleteLater();

    m_component = newComponent;
    m_widget = newWidget;

    if (m_widget->stack() != nullptr)
    {
        m_component->setStacker(m_widget->stack(), m_widget->stack()->count());
    }

    if (mw)
    {
        DBG_MSG << "Connect component menu";
        Component::connect (m_widget, &ComponentWidget::longClick, mw, &MainWidget::showComponentMenu);
    }
    else
    {
        DBG_MSG << "Invalid target for component menu";
    }

    Component::connect(m_component.get(), &Component::setTitleSuffix, m_widget, &ComponentWidget::setSuffix);


    return true;
}