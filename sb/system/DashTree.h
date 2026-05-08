#pragma once

#include <QJsonValue>
#include <QJsonObject>
#include <QJsonArray>
#include "sb/components/Component.h"


class DashNode
{
public:
    virtual QJsonValue toJson() = 0;

    virtual bool replaceComponent(PComponent oldComponent, PComponent newComponent, QWidget * target) = 0;

    void addField(QString key, QVariant value) {
        DBG_MSG << key << value;
        m_additionalFields[key] = value;
    }

    QMap<QString, QJsonValue> getFields() {
        QMap<QString, QJsonValue> result;
        for (auto i : m_additionalFields.keys())
        {
            DBG_MSG << i << m_additionalFields[i];
            result[i] = m_additionalFields[i].toJsonValue();
        }
        return result;
    }


private:
    QMap<QString, QVariant> m_additionalFields;
};

typedef QSharedPointer<DashNode> PDashNode;

class ComponentWidget;

class DashComponent : public DashNode
{
public:
    DashComponent(const PComponent & cmp, ComponentWidget * widget) : m_component(cmp), m_widget(widget) {}

    QJsonValue toJson() override;
    bool replaceComponent(PComponent oldComponent, PComponent newComponent, QWidget * target) override;


private:
    PComponent m_component;
    ComponentWidget * m_widget;
};

class DashList : public DashNode
{
public:
    DashList(const QList<PDashNode> & lst) : m_list(lst) {}

    bool replaceComponent(PComponent oldComponent, PComponent newComponent, QWidget * target) override
    {
        bool result = false;
        for (auto i : m_list)
        {
            result |= i->replaceComponent(oldComponent, newComponent, target);
        }
        return result;
    }

    QJsonValue toJson()
    {
        QJsonObject result;

        QJsonArray list;

        for (auto i : m_list)
        {
            list.append(i->toJson());
        }

        auto additionalFields = getFields();
        DBG_MSG << additionalFields.size() << "additional fields";
        for (auto i : additionalFields.keys()) {
            result.insert(i, additionalFields[i]);
        }

        result.insert("list", list);

        return QJsonValue(result);
    }

private:
    QList<PDashNode> m_list;

};

class DashStack : public DashNode
{
public:
    DashStack(const QList<PDashNode> & stck) : m_stack(stck) {}

    bool replaceComponent(PComponent oldComponent, PComponent newComponent, QWidget * target) override
    {
        bool result = false;
        for (auto i : m_stack)
        {
            result |= i->replaceComponent(oldComponent, newComponent, target);
        }
        return result;
    }

    QJsonValue toJson()
    {
        QJsonObject result;

        QJsonArray list;

        for (auto i : m_stack)
        {
            list.append(i->toJson());
        }

        result.insert("stack", list);

        return QJsonValue(result);
    }


private:
    QList<PDashNode> m_stack;

};
