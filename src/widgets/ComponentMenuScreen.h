#pragma once

#include "MenuScreen.h"

class ComponentContextMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    ComponentContextMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp);

public slots:
    void actionClicked();
    void paramClicked();
    void replaceClicked();

    void textInputOk();
    void textInputCancelled();

protected:
    void updateParams();

private:
    PState m_state;
    PComponent m_component;
    QLabel * m_lbParam = nullptr;
    QList<QWidget*> m_paramItems;
    QMap<QString, ComponentParameter<bool>> m_boolParameters;
    QMap<QString, ComponentParameter<QString>> m_stringParameters;
    QMap<QString, ComponentParameter<int>> m_intParameters;
    QMap<QString, ComponentParameter<float>> m_floatParameters;

};

class ComponentSelectionMenuScreen : public MenuScreen
{
    Q_OBJECT

public:
    ComponentSelectionMenuScreen (MainWidget * parent, PDash dash, PState state, PComponent comp);

public slots:
    void componentClicked();

private:
    PComponent m_component;
};
