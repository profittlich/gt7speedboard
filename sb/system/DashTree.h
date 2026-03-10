#pragma once

#include <QJsonValue>
#include <QJsonObject>
#include <QJsonArray>
#include "sb/components/Component.h"

class DashNode
{
public:
    virtual QJsonValue toJson() = 0;

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

class DashComponent : public DashNode
{
public:
    DashComponent(const PComponent & cmp, const QJsonValue json) : m_component(cmp), m_json(json) {}

    QJsonValue toJson()
    {
        QJsonObject result = m_json.toObject();
        QJsonObject conf;
        QMap<QString, QJsonObject> presets;

        bool found = false;
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

private:
    PComponent m_component;
    QJsonValue m_json;

};

class DashList : public DashNode
{
public:
    DashList(const QList<PDashNode> & lst) : m_list(lst) {}

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
