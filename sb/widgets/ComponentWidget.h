#pragma once

#include <QWidget>
#include <QGridLayout>
#include <QLabel>
#include <QElapsedTimer>
#include "sb/system/Dash.h"
#include "sb/widgets/DashWidget.h"
#include "sb/components/Component.h"
#include "sb/widgets/SideButtonLabel.h"

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
            //cmp->getWidget()->installEventFilter(this);
        }

        setContentsMargins(0,0,0,0);
        m_layout->setContentsMargins(0,0,0,0);
        //setStyleSheet("background-color:red;");
    }

    PComponent component() { return m_component; }

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

signals:
    void longClick();

protected:
    bool eventFilter(QObject *obj, QEvent *event) override
    {
        QMouseEvent * mev = dynamic_cast<QMouseEvent*>(event);
        if (event->type() == QEvent::MouseButtonPress && mev->button() == Qt::LeftButton  )
        {
            DBG_MSG << "Mouse press";
            m_longClickTimer.start();
            return true;
        }
        else if (event->type() == QEvent::MouseButtonRelease && mev->button() == Qt::LeftButton)
        {
            DBG_MSG << m_longClickTimer.elapsed();
            if (m_longClickTimer.elapsed() > g_globalConfiguration.longClickTimeout())
            {
                DBG_MSG << "Long click";
                emit longClick();
                return true;
            }

            return false;
        }
        else if (event->type() == QEvent::MouseButtonPress && mev->button() == Qt::RightButton)
        {
            emit longClick();
            return true;
        }
        else if (event->type() == QEvent::MouseButtonRelease && mev->button() == Qt::RightButton)
        {
            return true;
        }
        return false;
    }

    void addEventFiltersRecursively(QObject * o)
    {
        if(o && o->isWidgetType())
        {
            o->installEventFilter(this);
            const QObjectList& children = o->children();
            for(QObjectList::const_iterator it = children.begin(); it != children.end(); ++it)
            {
                addEventFiltersRecursively(*it);
            }
        }
    }

    void removeEventFiltersRecursively(QObject * o)
    {
        if(o && o->isWidgetType())
        {
            o->removeEventFilter(this);
            const QObjectList& children = o->children();
            for(QObjectList::const_iterator it = children.begin(); it != children.end(); ++it)
            {
                removeEventFiltersRecursively(*it);
            }
        }
    }

    void childEvent(QChildEvent*ev) override
    {
        if (ev->child()->isWidgetType())
        {
            if (ev->type() == QEvent::ChildAdded)
            {
                addEventFiltersRecursively(ev->child());
            }
            else if (ev->type() == QEvent::ChildRemoved)
            {
                removeEventFiltersRecursively(ev->child());
            }
        }
    }

    QLabel * makeHead(PComponent cmp, DashWidget * dashWidget, bool backButton = false, QString title="")
    {
        QLabel * head;
        if (backButton)
        {
            SideButtonLabel * sbhead = new SideButtonLabel(dashWidget);
            SideButtonLabel::connect(sbhead, &SideButtonLabel::buttonClicked, dashWidget, &DashWidget::showMenu);
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
    QElapsedTimer m_longClickTimer;
};
