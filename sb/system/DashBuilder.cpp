#include "DashBuilder.h"



DashWidget::DashWidget (QWidget * parent, PDash dash) : QStackedWidget(parent)
{
    DialogWidget * dialog = new DialogWidget(this, dash);
    addWidget(dialog);
    m_color = g_globalConfiguration.dimColor();
}

void DashWidget::paintEvent(QPaintEvent * ev)
{
    m_painter.begin(this);
    m_painter.setPen(m_color);
    m_painter.setBrush(m_color);
    m_painter.drawRect(0, 0, width(), height());
    m_painter.end();

    QStackedWidget::paintEvent(ev);
}

void DashWidget::setColor (const QColor & color)
{
    m_color = color;
}

QJsonValue DashBuilder::jVal(QJsonObject obj, QString key, QJsonValue def)
{
    if (!obj.contains(key))
    {
        return def;
    }
    return obj[key];
}

QWidget * DashBuilder::makeDashTree (PDash dash, QBoxLayout * curLayout, QJsonValue cur, bool vertical, bool & firstComp, PDashNode & dashNode, QStackedWidget * stacker)
{
    //DBG_MSG << ("Make dash tree");
    if (!cur.isObject())
    {
        DBG_MSG << ("Not an object");
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
            makeDashTree(dash, newLayout, comp, !vertical, firstComp, curNode);
            cmpList.append(curNode);
        }

        if (curLayout != nullptr)
        {
            curLayout->addWidget(widget);
            curLayout->setStretch(curLayout->count()-1,jVal(curObj, "stretch", 1).toInt(1));
        }

        dashNode = PDashNode(new DashList(cmpList));

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
            widget->addWidget(makeDashTree(dash, nullptr, comp, !vertical, firstComp, curNode, widget));
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

        PComponent cmp = ComponentFactory::createComponent(curObj["component"].toString(), cur);
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
                    ComponentParameter<QString> param (i, config[i].toString());
                    cmp->setStringParameter(param);
                }
                else if (config[i].isDouble())
                {
                    DBG_MSG << "Param" << i << config[i];
                    ComponentParameter<float> param (i, config[i].toDouble());
                    cmp->setFloatParameter(param);
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
            QJsonObject actList = curObj["actions"].toObject();
            for (const auto & a : actList.keys())
            {
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

        if (cmp->getWidget() != nullptr)
        {
            ComponentWidget * cw = new ComponentWidget(dash, cmp, firstComp, showHeader, title);

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
            dash->components.append(cmp);
            dashNode = PDashNode(new DashComponent(cmp, cur));

            return cw;
        }
        else
        {
            dash->components.append(cmp);
            dashNode = PDashNode(new DashComponent(cmp, cur));
            return nullptr;
        }
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
        makeDashTree(result, layout, page, true, firstComp, curPage.dashNode);
        result->pages.append(curPage);

        pageIndex++;
    }

    //qDebug(pages.toJson());

    result->widget->setCurrentIndex(1);
    //result->widget->setContentsMargins(14,14,14,14);

    return result;
}
