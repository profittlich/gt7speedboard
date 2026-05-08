#pragma once

#include "DashTree.h"
#include <QJsonDocument>

class DashWidget;

class Page
{
public:
    QJsonValue toJson()
    {
        QJsonObject result = dashNode->toJson().toObject();
        result.insert("title", title);
        QJsonArray scArray;
        for (auto i : shortcuts)
        {
            scArray.append(i);
        }
        result.insert("shortcuts", scArray);
        return QJsonValue(result);
    }

    bool replaceComponent(PComponent oldComponent, PComponent newComponent, QWidget * target)
    {
        return dashNode->replaceComponent(oldComponent, newComponent, target);
    }

    PDashNode dashNode;
    QString title;
    QList<QString> shortcuts;
};


class Dash : public QObject
{
    Q_OBJECT

public:
    QJsonDocument toJson()
    {
        QJsonObject out;
        out.insert("version", 2);
        QJsonArray pagesArray;
        for (auto i : pages)
        {
            //qDebug("===PAGE===");

            //qDebug(i.toJson().toJson());
            pagesArray.append(i.toJson());
        }
        out.insert("pages", pagesArray);
        return QJsonDocument(out);
    }

    void replaceComponent(PComponent oldComponent, PComponent newComponent, QWidget * target)
    {
        bool success = false;
        for (auto i : pages)
        {
            success |= i.replaceComponent(oldComponent, newComponent, target);
        }
        if (success)
        {
            components.removeAll(oldComponent);
            components.append(newComponent);
        }
        else
        {
            DBG_MSG << "Could not replace component";
        }
    }

    QJsonDocument json;
    QList<Page> pages;
    QList <PComponent> components;
    DashWidget * widget;
    QMap<unsigned, QPair<PComponent, QString>> actions;
    QMap<unsigned, unsigned> pageShortcuts;
};


typedef QSharedPointer<Dash> PDash;
