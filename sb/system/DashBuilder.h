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
#include "sb/widgets/SideButtonLabel.h"
#include "sb/widgets/ButtonLabel.h"
#include "sb/system/Configuration.h"

#include "sb/components/Component.h"
#include "sb/components/ComponentFactory.h"
#include "sb/system/DashTree.h"

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

class DashWidget : public QStackedWidget
{
    Q_OBJECT

public:
    DashWidget (QWidget * parent, PDash dash);
    void setColor (const QColor & color);

protected:
    void paintEvent(QPaintEvent * ev);

signals:
    void exitDash();

private:
    QPainter m_painter;
    QColor m_color;
};

class DialogWidget : public QWidget
{
    Q_OBJECT

public:
    DialogWidget (QWidget * parent, PDash dash) : QWidget(parent)
    {
        m_dash = dash;
        QLayout * layout = new QVBoxLayout(this);
        QPushButton * btn = new QPushButton(this);
        btn->setText("Dismiss");
        connect(btn, &QPushButton::clicked, this, &DialogWidget::returnToDash);
        layout->addWidget(btn);
    }

public slots:
    void returnToDash()
    {
        m_dash->widget->setCurrentIndex(1);
    }

private:
    PDash m_dash;
};

class ComponentWidget : public QWidget
{
    Q_OBJECT

public:
    ComponentWidget (PDash parent, PComponent cmp, bool backButton = false, bool showHeader = true, QString title = "") : QWidget(parent->widget)
    {
        m_dash = parent;
        m_component = cmp;

        m_layout = new QGridLayout(this);
        m_layout->setRowStretch(0, 1);
        m_layout->setSpacing(10);

        m_head = makeHead(cmp, parent->widget, backButton, title);
        if (!showHeader && !backButton)
        {
            m_head->setVisible(false);
        }
        if (!showHeader && backButton)
        {
            m_head->setText("");
        }


        if (showHeader)
        {
            m_layout->addWidget(m_head, 0, 0);
            if (cmp->getWidget()->isEnabled())
            {
                DBG_MSG << "Add visible widget" << cmp->defaultTitle();
                m_layout->setRowStretch(1, 100);
                m_layout->addWidget(cmp->getWidget(), 1, 0);
            }
            else
            {
                DBG_MSG << "Do not add invisible widget" << cmp->defaultTitle();
            }
        }
        else
        {
            m_layout->addWidget(cmp->getWidget(), 0, 0);
        }

        setContentsMargins(0,0,0,0);
        m_layout->setContentsMargins(0,0,0,0);
        //setStyleSheet("background-color:red;");
    }

public slots:
    void setSuffix(QString sf)
    {
        m_head->setText(m_headText + " " + sf);
    }

    void selectComponent()
    {
        DBG_MSG << ("replaceComponent");
        m_dash->widget->setCurrentIndex(1);
    }

    void replaceComponent(PComponent newCmp)
    {
        m_head->setText("");

        QFont font = m_head->font();
        font.setPointSizeF(newCmp->baseFontSize() * 6);
        m_head->setFont(font);

        QWidget * oldWidget = m_component->getWidget();
        m_layout->replaceWidget(oldWidget, newCmp->getWidget());
        oldWidget->hide();

        m_dash->components.removeAll(m_component);
        m_dash->components.append(newCmp);
        m_component = newCmp;

        delete oldWidget;

        m_head->setText(newCmp->title().toUpper());
    }

protected:
    QLabel * makeHead(PComponent cmp, DashWidget * dashWidget, bool backButton = false, QString title="")
    {
        QLabel * head;
        if (backButton)
        {
            SideButtonLabel * sbhead = new SideButtonLabel(dashWidget);
            SideButtonLabel::connect(sbhead, &SideButtonLabel::buttonClicked, dashWidget, &DashWidget::exitDash);
            SideButtonLabel::connect(sbhead, &SideButtonLabel::labelClicked, this, &ComponentWidget::selectComponent);
            head = sbhead;
        }
        else
        {
            ButtonLabel * bhead = new ButtonLabel(dashWidget);
            ButtonLabel::connect(bhead, &ButtonLabel::labelClicked, this, &ComponentWidget::selectComponent);
            head = bhead;
        }
        if (title == "")
        {
            m_headText = cmp->title().toUpper();
        }
        else
        {
            m_headText = title;
        }
        head->setText(m_headText);
        head->setAlignment(Qt::AlignCenter);
        QFont font = head->font();
        font.setPointSizeF(cmp->baseFontSize() * 6);
        font.setBold(true);
        head->setFont(font);
        head->setStyleSheet("color:" + g_globalConfiguration.headerTextColor().name() + ";");

        return head;
    }

private:
    PDash m_dash;
    QLabel * m_head;
    PComponent m_component;
    QGridLayout * m_layout;
    QString m_headText;
};

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
