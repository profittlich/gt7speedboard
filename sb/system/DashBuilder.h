#pragma once

#include <QtLogging>

#include <QWidget>
#include <QGridLayout>
#include <QLabel>
#include <QStackedWidget>
#include <QPushButton>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>

#include "sb/system/KeyStrings.h"
#include "sb/system/DashTree.h"
#include "sb/system/Dash.h"


class DashBuilder : public QObject
{
    Q_OBJECT

public:
    DashBuilder ()
    {
        m_qtKeys = initQtKeys();
    }

    PDash makeDash(QWidget * parent, QJsonDocument spec);

protected:
    QWidget * makeDashTree (PDash dash, QBoxLayout * curLayout, QJsonValue cur, bool vertical, bool & firstComp, PDashNode & dashNode, QStackedWidget * stacker = nullptr);
    unsigned qtKey(QString k) { if (m_qtKeys.contains(k)) return m_qtKeys[k]; return 0; }
    static QJsonValue jVal(QJsonObject obj, QString key, QJsonValue def);

private:
    PDash m_dash;
    QMap<QString, unsigned> m_qtKeys;
};

typedef QSharedPointer<DashBuilder> PDashBuilder;
