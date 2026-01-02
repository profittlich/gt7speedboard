#pragma once

#include <QtLogging>

#include <QString>
#include <QSharedPointer>
#include <QSettings>
#include <QColor>

class Configuration
{
public:
    Configuration ()
    {
    }

    void init()
    {
        QSettings settings;

        setHostAddress(settings.value("ip", "127.0.0.1").toString());
        //setHostAddress("192.168.178.64");

        setBackgroundColor(QColor("#222"));
        setDimColor(QColor("#333"));
        setHeaderTextColor(QColor("white"));

        setFontScale(1);
        setFuelStatisticsLaps(5);

        m_maxPointDistanceForValidLap = 20.0;

        loadCars();
    }

    void loadCars();

    QString carName(const unsigned carId) const
    {
        if (m_cars.contains(carId))
        {
            return m_cars[carId];
        }
        return "Unknown car: " + QString::number(carId);
    }

    /* SETTERS */
    void setFontScale(const float & v) { m_fontScale = v; }
    //void setStorageLocation(const QString & v) { m_storageLocation = v; }
    void setHostAddress(const QString & v) { qInfo("%s", v.toStdString().c_str()); m_hostAddress = v; }
    void setSelectedLayout(const QString & v) { m_selectedLayout = v; }
    void setBackgroundColor(const QColor & c) { m_backgroundColor = c; }
    void setHeaderTextColor(const QColor & c) { m_headerTextColor = c; }
    void setDimColor(const QColor & c) { m_dimColor = c; }

    void setFuelStatisticsLaps(const size_t & v) { m_fuelStatisticsLaps = v; }

    /* GETTERS */
    const float & fontScale() const { return m_fontScale; }
    //const QString & storageLocation() const { return m_storageLocation; }
    const QString & hostAddress() const { return m_hostAddress; }
    const QString & selectedLayout() const { return m_selectedLayout; }

    const QColor & backgroundColor() const { return m_backgroundColor; }
    const QColor & headerTextColor() const { return m_headerTextColor;; }
    const QColor & dimColor() const { return m_dimColor; }

    const size_t & fuelStatisticsLaps() const { return m_fuelStatisticsLaps; }

    const float & maxPointDistanceForValidLap() const { return m_maxPointDistanceForValidLap; }

private:
    /* PROPERTIES */
    float m_fontScale;
    //QString m_storageLocation;
    QString m_hostAddress;
    QColor m_backgroundColor;
    QColor m_dimColor;
    QColor m_headerTextColor;
    size_t m_fuelStatisticsLaps;
    float m_maxPointDistanceForValidLap;
    QString m_selectedLayout;
    QMap<unsigned, QString> m_carMakers;
    QMap<unsigned, QString> m_cars;
};

typedef QSharedPointer<Configuration> PConfiguration;

extern Configuration g_globalConfiguration;

