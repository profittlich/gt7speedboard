#include "DashBuilder.h"

#include "sb/widgets/DashWidget.h"
#include "sb/widgets/ComponentWidget.h"
#include "sb/components/ComponentFactory.h"
#include "MainWidget.h"


QJsonValue DashBuilder::jVal(QJsonObject obj, QString key, QJsonValue def)
{
    if (!obj.contains(key))
    {
        return def;
    }
    return obj[key];
}

QWidget * DashBuilder::makeDashTree (PDash dash, QBoxLayout * curLayout, QJsonValue cur, bool vertical, bool & firstComp, PDashNode & dashNode, QObject * menuTarget, QStackedWidget * stacker)
{
    //DBG_MSG << ("Make dash tree");
    if (!cur.isObject())
    {
        DBG_MSG << "Not an object" << cur.type();
        return nullptr;
    }

    QJsonObject curObj = cur.toObject();

    if (curObj.contains("list"))
    {
        //DBG_MSG << ("Component list");
        QWidget * widget = new QWidget(dash->widget);
        QBoxLayout * newLayout;
        if (vertical)
        {
            newLayout = new QVBoxLayout(widget);
        }
        else
        {
            newLayout = new QHBoxLayout(widget);
        }

        newLayout->setContentsMargins(0,0,0,0);
        newLayout->setSpacing(10);

        QList<PDashNode> cmpList;

        for (const QJsonValue & comp : curObj["list"].toArray())
        {
            PDashNode curNode;
            makeDashTree(dash, newLayout, comp, !vertical, firstComp, curNode, menuTarget);
            cmpList.append(curNode);
        }

        if (curLayout != nullptr)
        {
            curLayout->addWidget(widget);
            curLayout->setStretch(curLayout->count()-1,jVal(curObj, "stretch", 1).toInt(1));

        }

        dashNode = PDashNode(new DashList(cmpList));

        if (curObj.contains("stretch"))
        {
            DBG_MSG << "stretch found";
            dashNode->addField("stretch", jVal(curObj, "stretch", 1));
        }

        return widget;
    }
    else if (curObj.contains("stack"))
    {
        //DBG_MSG << ("Component stack");
        QStackedWidget * widget = new QStackedWidget(dash->widget);
        QList<PDashNode> cmpList;

        for (const QJsonValue & comp : curObj["stack"].toArray())
        {
            PDashNode curNode;
            widget->addWidget(makeDashTree(dash, nullptr, comp, !vertical, firstComp, curNode, menuTarget, widget));
            cmpList.append(curNode);
        }

        if (curLayout != nullptr)
        {
            curLayout->addWidget(widget);
            curLayout->setStretch(curLayout->count()-1,jVal(curObj, "stretch", 1).toInt(1));
        }

        dashNode = PDashNode(new DashStack(cmpList));

        return widget;
    }
    else if (curObj.contains("component"))
    {
        cur = curObj;
        DBG_MSG << (curObj["component"].toString().toLatin1());
        bool showHeader = true;
        QString title = "";
        QJsonObject config;

        if (curObj.contains("showHeader"))
        {
            showHeader = curObj["showHeader"].toBool(true);
        }
        if (curObj.contains("title"))
        {
            title = curObj["title"].toString("");
        }

        PComponent cmp = ComponentFactory::createComponent(curObj["component"].toString());
        if (cmp.isNull())
        {
            DBG_MSG << ("Unknown component " + curObj["component"].toString().toLatin1());
            return nullptr;
        }
        cmp->setPermissions(jVal(curObj, "raiseAllowed", false).toBool(), jVal(curObj, "gotoPageAllowed", false).toBool(), jVal(curObj, "fullScreenSignalAllowed", false).toBool());

        if (curObj.contains("configuration") && curObj["configuration"].isObject())
        {
            config = curObj["configuration"].toObject();

            for (const auto & i : config.keys())
            {
                if (config[i].isString())
                {
                    DBG_MSG << "Set string" << i << config[i].toString();
                    ComponentParameter<QString> param (i, config[i].toString());
                    cmp->setStringParameter(param);
                }
                else if (config[i].isDouble())
                {
                    DBG_MSG << "Set number" << i << QString::number (config[i].toDouble());
                    DBG_MSG << "Param" << i << config[i];
                    ComponentParameter<float> param (i, config[i].toDouble());
                    cmp->setFloatParameter(param);
                }
                else if (config[i].isBool())
                {
                    DBG_MSG << "Set boolean" << i << QString::number (config[i].toDouble());
                    DBG_MSG << "Param" << i << config[i];
                    ComponentParameter<bool> param (i, config[i].toBool());
                    cmp->setBooleanParameter(param);
                }
            }
            if (config.contains("presets"))
            {
                //DBG_MSG << ("Presets found");
                QJsonObject presets = config["presets"].toObject();
                for (auto & i : presets.keys())
                {
                    DBG_MSG << ("key " + i.toLatin1());
                    QJsonObject curPreset = presets[i].toObject();
                    for (const auto & j : curPreset.keys())
                    {
                        DBG_MSG << ("key2 " + j.toLatin1());
                        if (curPreset[j].isString())
                        {
                            ComponentParameter<QString> param = cmp->stringParameter(j);
                            DBG_MSG << ("Add preset " + i.toLatin1() + " " + j.toLatin1() + " " + curPreset[j].toString().toLatin1());
                            param.addPresetValue(i, curPreset[j].toString());
                            cmp->setStringParameter(param, true);
                        }
                        else if (curPreset[j].isDouble())
                        {
                            ComponentParameter<float> param = cmp->floatParameter(j);
                            DBG_MSG << ("Add preset " + i.toLatin1() + " " + j.toLatin1() + " " + QString::number(curPreset[j].toDouble()).toLatin1());
                            param.addPresetValue(i, curPreset[j].toDouble());
                            cmp->setFloatParameter(param, true);
                        }
                        else if (curPreset[j].isBool())
                        {
                            ComponentParameter<bool> param = cmp->booleanParameter(j);
                            DBG_MSG << ("Add preset " + i.toLatin1() + " " + j.toLatin1() + " " + QString::number(curPreset[j].toBool()).toLatin1());
                            param.addPresetValue(i, curPreset[j].toBool());
                            cmp->setBooleanParameter(param, true);
                        }
                    }
                }

            }
            cmp->presetSwitched();
        }

        if (curObj.contains("actions"))
        {
            if (!curObj["actions"].isObject())
            {
                DBG_MSG << ("Malformed action list: " + curObj["component"].toString().toLatin1());
                return nullptr;
            }
            auto defActions = cmp->getActions();

            QJsonObject actList = curObj["actions"].toObject();
            for (const auto & a : actList.keys())
            {
                if (!defActions.contains(actList[a].toString()))
                {
                    DBG_MSG << "Unknown action for" << cmp->getComponentId() << ":" << actList[a].toString();
                }
                unsigned keyCode = qtKey(a);
                if (dash->pageShortcuts.contains(keyCode) || dash->actions.contains(keyCode))
                {
                    DBG_MSG << ("Shortcut already taken: " + a.toLatin1());
                }
                else
                {
                    auto & x = dash->actions[keyCode];
                    x.first = cmp;
                    x.second = actList[a].toString();
                }
            }
        }

        ComponentWidget * cw = nullptr;
        if (cmp->getWidget() != nullptr)
        {
            DBG_MSG << "Build widget";
            cw = new ComponentWidget(dash, cmp, firstComp, showHeader, title);
            MainWidget * mw = dynamic_cast<MainWidget*> (menuTarget);
            if (mw)
            {
                DBG_MSG << "Connect component menu";
                connect (cw, &ComponentWidget::longClick, mw, &MainWidget::showComponentMenu);
            }
            else
            {
                DBG_MSG << "Invalid target for component menu";
            }

            connect(cmp.get(), &Component::setTitleSuffix, cw, &ComponentWidget::setSuffix);
            firstComp = false;

            if (curLayout != nullptr)
            {
                curLayout->addWidget(cw);
                curLayout->setStretch(curLayout->count()-1,jVal(curObj, "stretch", 1).toInt(1));
            }
            if (stacker != nullptr)
            {
                cmp->setStacker(stacker, stacker->count());
            }
        }

        dash->components.append(cmp);
        dashNode = PDashNode(new DashComponent(cmp));

        if (curObj.contains("title"))
        {
            DBG_MSG << "JSON title";
            dashNode->addField("title", jVal(curObj, "title", 1));
        }
        if (curObj.contains("stretch"))
        {
            DBG_MSG << "JSON stretch";
            dashNode->addField("stretch", jVal(curObj, "stretch", 1));
        }
        if (curObj.contains("showHeader"))
        {
            DBG_MSG << "JSON showHeader";
            dashNode->addField("showHeader", jVal(curObj, "showHeader", 1));
        }
        if (curObj.contains("raiseAllowed"))
        {
            DBG_MSG << "JSON raiseAllowed";
            dashNode->addField("raiseAllowed", jVal(curObj, "raiseAllowed", 1));
        }
        if (curObj.contains("fullScreenSignalAllowed"))
        {
            DBG_MSG << "JSON fullScreenSignalAllowed";
            dashNode->addField("fullScreenSignalAllowed", jVal(curObj, "fullScreenSignalAllowed", 1));
        }

        return cw;
    }
    else
    {
        DBG_MSG << ("Malformed JSON");
        return nullptr;
    }

}


PDash DashBuilder::makeDash(QWidget * parent, QJsonDocument spec)
{
    if (!spec.isObject()) return nullptr;

    PDash result = PDash(new Dash());

    QJsonObject root = spec.object();

    if (root["version"] != 2) return nullptr;

    result->widget = new DashWidget(parent, result);

    QJsonValue pages = root["pages"];

    if (!pages.isArray()) return nullptr;

    size_t pageIndex = 0;

    for (const QJsonValue & page : pages.toArray())
    {
        Page curPage;
        if (!page.isObject()) return nullptr;

        QJsonObject curObj = page.toObject();

        if (!curObj["list"].isArray()) return nullptr;

        if (curObj.contains("title"))
        {
            curPage.title = curObj["title"].toString();
        }

        if (curObj.contains("shortcuts") && curObj["shortcuts"].isArray())
        {
            for (auto i : curObj["shortcuts"].toArray())
            {
                curPage.shortcuts.append(i.toString());
                unsigned keyCode = qtKey(i.toString());
                if (result->pageShortcuts.contains(keyCode) || result->actions.contains(keyCode))
                {
                    qDebug("Shortcut already taken: " + i.toString().toLatin1());
                }
                else
                {
                    result->pageShortcuts[keyCode] = pageIndex;
                }
            }
        }

        QWidget * pageWidget = new QWidget();

        pageWidget->setContentsMargins(20,20,20,20);
        result->widget->addWidget (pageWidget);

        QHBoxLayout * layout = new QHBoxLayout(result->widget->widget(result->widget->count()-1));
        layout->setContentsMargins(0,0,0,0);
        bool firstComp = true;
        makeDashTree(result, layout, page, true, firstComp, curPage.dashNode, parent);
        result->pages.append(curPage);

        pageIndex++;
    }

    result->widget->setCurrentIndex(1);

    return result;
}
