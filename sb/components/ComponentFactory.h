#pragma once

#include <QtLogging>
#include <QMap>

#include "sb/components/Component.h"




class ComponentFactory
{
public:
    class ComponentBaseConstructor
    {
    public:
        virtual PComponent create() = 0;
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
        RegisterComponent()
        {
            //qDebug("Register component %s", T::componentId().toStdString().c_str());
            ComponentFactory::addComponent(T::componentId(), PComponentBaseConstructor(new ComponentConstructor<T>()));
        }
    };

    static void addComponent(QString id, PComponentBaseConstructor c)
    {
        //qDebug("Add component %s", id.toStdString().c_str());
        s_constructors[id] = c;
        //qDebug("done.");
    }

    static PComponent createComponent(QString id);

    static QStringList listComponents()
    {
        return s_constructors.keys();
    }

private:
    static QMap<QString, PComponentBaseConstructor> s_constructors;
};

