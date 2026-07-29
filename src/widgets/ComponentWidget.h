#pragma once

#include <QWidget>
#include <QGridLayout>
#include <QLabel>
#include <QElapsedTimer>
#include <QtCore/qtimer.h>
#include "src/system/Dash.h"
#include "src/widgets/DashWidget.h"
#include "src/components/Component.h"

class ComponentWidget : public QWidget
{
    Q_OBJECT

public:
    ComponentWidget (PDash parent, PComponent cmp, bool backButton = false, bool showHeader = true, QString title = "");

    PComponent component();
    PDash dash();
    QString title();
    bool backButton ();
    bool showHeader();

    void setLayout(QLayout * l);
    QLayout * layout();

    void setStack(QStackedWidget * s);
    QStackedWidget * stack();


public slots:
    void setSuffix(QString sf);
    void selectComponent();
    void replaceComponent(PComponent newCmp);


signals:
    void longClick();

protected:
    bool eventFilter(QObject *, QEvent *event) override;
    void addEventFiltersRecursively(QObject * o);
    void removeEventFiltersRecursively(QObject * o);
    void childEvent(QChildEvent*ev) override;
    QLabel * makeHead(PComponent cmp, DashWidget * dashWidget, bool backButton = false, QString title="");

private:
    PDash m_dash;
    QLabel * m_head = nullptr;
    PComponent m_component;
    QGridLayout * m_layout = nullptr;
    QString m_headText;
    QTimer m_longClickTimer;
    QLayout * m_ownLayout = nullptr;
    QStackedWidget * m_ownStack = nullptr;
    bool m_backButton = false;
    bool m_showHeader = true;
    QString m_title;
    int m_oldMaxHeight = 16777215;
    int m_oldMaxWidth = 16777215;
};
