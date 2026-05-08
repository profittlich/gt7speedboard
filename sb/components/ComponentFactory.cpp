#include "sb/components/ComponentFactory.h"

QMap<QString, ComponentFactory::PComponentBaseConstructor> ComponentFactory::s_constructors;

PComponent ComponentFactory::createComponent(QString id)
{
    if (s_constructors.contains(id))
    {
        return s_constructors[id]->create();
    }

    return PComponent();
}
