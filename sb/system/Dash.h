#pragma once

#include "DashTree.h"

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

    PDashNode dashNode;
    QString title;
    QList<QString> shortcuts;
};


class Dash : public QObject
{
    Q_OBJECT

public:
    QJsonValue toJson()
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
        return QJsonValue(out);
    }

    QJsonDocument json;
    QList<Page> pages;
    QList <PComponent> components;
    DashWidget * widget;
    QMap<unsigned, QPair<PComponent, QString>> actions;
    QMap<unsigned, unsigned> pageShortcuts;
};


typedef QSharedPointer<Dash> PDash;
