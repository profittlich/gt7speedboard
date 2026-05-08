#pragma once

#include <QtLogging>
#include <QMap>

#include "sb/components/Component.h"




class ComponentFactory
{
public:
    class ComponentBaseConstructor
    {
        friend class ComponentFactory;

    public:
        virtual PComponent create() = 0;

        bool hasWidget()
        {
            return m_hasWidget;
        }

    private:
        bool m_hasWidget;
    };

    typedef QSharedPointer<ComponentBaseConstructor> PComponentBaseConstructor;

    template<typename T>
    class ComponentConstructor : public ComponentBaseConstructor
    {
    public:
        PComponent create()
        {
            auto cmp = PComponent(new T());
            cmp->setComponentId(T::componentId());
            cmp->setDescription(T::description());
            cmp->setActions(T::actions());
            return cmp;
        }
    };

    template <typename T>
    class RegisterComponent
    {
    public:
        RegisterComponent(bool hasWidget)
        {
            //qDebug("Register component %s", T::componentId().toStdString().c_str());
            ComponentFactory::addComponent(T::componentId(), PComponentBaseConstructor(new ComponentConstructor<T>()), hasWidget);
        }
    };

    static void addComponent(QString id, PComponentBaseConstructor c, bool hasWidget)
    {
        //qDebug("Add component %s", id.toStdString().c_str());
        c->m_hasWidget = hasWidget;
        s_constructors[id] = c;
        //qDebug("done.");
    }

    static PComponent createComponent(QString id);

    static QStringList listComponents()
    {
        return s_constructors.keys();
    }

    static bool componentHasWidget(QString key)
    {
        if (s_constructors.contains(key))
        {
            return s_constructors[key]->hasWidget();
        }
        return false;
    }

private:
    static QMap<QString, PComponentBaseConstructor> s_constructors;
};

