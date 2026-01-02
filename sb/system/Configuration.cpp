#include "Configuration.h"
#include "sb/system/Helpers.h"

#include <QFile>

Configuration g_globalConfiguration;



void Configuration::loadCars()
{
    m_cars.clear();
    m_carMakers.clear();

    DBG_MSG << "loadCars";
    {
        QFile f (":/assets/assets/makers.csv");
        if (f.exists())
        {
            f.open(QIODeviceBase::ReadOnly);
            auto all = f.readLine();
            while (!all.isNull())
            {
                //DBG_MSG << "Maker: " << all;
                all = f.readLine();
                auto curCar = all.split(',');
                DBG_MSG << curCar;
                if (curCar.size() == 2)
                {
                    m_carMakers[curCar[0].toLong()] = curCar[1].trimmed();
                }
            }
            f.close();
        }
    }

    {
        QFile f (":/assets/assets/cars.csv");
        if (f.exists())
        {
            f.open(QIODeviceBase::ReadOnly);
            auto all = f.readLine();
            while (!all.isNull())
            {
                //DBG_MSG << "Car: " << all;
                all = f.readLine();
                auto curCar = all.split(',');
                if (curCar.size() == 3)
                {
                    m_cars[curCar[0].toLong()] = m_carMakers[curCar[2].toLong()] + " - " + curCar[1].trimmed();
                }
            }
            f.close();
        }
    }

    for (auto i : m_cars)
    {
        DBG_MSG << i;
    }
}
