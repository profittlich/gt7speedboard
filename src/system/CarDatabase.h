#pragma once

#include <QString>
#include <QSharedPointer>

class CarDatabase
{
    void loadCarDatabase();
    QString identifyCar(unsigned carID) const;
};

typedef QSharedPointer<CarDatabase> PCarDatabase;
