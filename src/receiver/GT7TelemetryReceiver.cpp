#include <QtLogging>
#include <QUdpSocket>
#include <QNetworkDatagram>
#include <QSharedPointer>
#include <src/receiver/GT7TelemetryReceiver.h>
#include <src/cardata/TelemetryPointGT7.h>
#include <src/system/Configuration.h>
#include <contrib/Salsa20-master/Source/Salsa20.h>

#include "src/system/Helpers.h"

GT7TelemetryReceiver::GT7TelemetryReceiver() : TelemetryReceiver ()
{
    DBG_MSG << ("Construct GT7TelemetryReceiver");
}

void GT7TelemetryReceiver::start()
{
    m_heartBeatTimer = new QTimer(this);
    connect(m_heartBeatTimer, &QTimer::timeout, this, &GT7TelemetryReceiver::sendHeartBeat);
    DBG_MSG << ("Start receiving");
    m_socket = new QUdpSocket(this);

    connect(m_socket, &QUdpSocket::readyRead, this, &GT7TelemetryReceiver::readPendingDatagrams);

    if (!m_socket->bind(33740))
    {
        qCritical("Could not bind UDP receiver");
    }

    m_isRunning = true;

    sendHeartBeat();
    m_heartBeatTimer->setInterval(3000);
    m_heartBeatTimer->start();

    m_lastSequenceNumbers.clear();
    m_lastSequenceNumbers.push_back(0);
}

void GT7TelemetryReceiver::stop()
{
    m_isRunning = false;
}

bool GT7TelemetryReceiver::magicValid(const QByteArray & data)
{
    if (data[0] == 0x30 && data[1] == 0x53 && data[2] == 0x37 && data[3] == 0x47)
    {
        return true;
    }
    return false;
}

QByteArray GT7TelemetryReceiver::decrypt(const QByteArray & data)
{
    const uint8_t * key = reinterpret_cast<const uint8_t *> ("Simulator Interface Packet GT7 v");//er 0.0";
    ucstk::Salsa20 salsa20(key);

    uint8_t oiv[4];
    oiv[0] = data.at(0x40);
    oiv[1] = data.at(0x41);
    oiv[2] = data.at(0x42);
    oiv[3] = data.at(0x43);
    uint32_t iv1 = oiv[0] + 0x100 * oiv[1] + 0x10000 * oiv[2] + 0x1000000 * oiv[3];
    uint32_t iv2 = iv1 ^ 0xDEADBEAF;
    switch (data.size())
    {
    case 296:
        iv2 = iv1 ^ 0xDEADBEAF;
        break;
    case 296 + 20:
        iv2 = iv1 ^ 0xDEADBEEF;
        break;
    case 296 + 20 + 28:
        iv2 = iv1 ^ 0x55FABB4F;
        break;
    case 296 + 20 + 28 + 20:
        iv2 = iv1 ^ 0xDEADBEEF;
        break;
    }

    uint8_t * piv1 = reinterpret_cast<uint8_t*> (&iv1);
    uint8_t * piv2 = reinterpret_cast<uint8_t*> (&iv2);

    uint8_t iv[8];

    iv[0] = piv2[0];
    iv[1] = piv2[1];
    iv[2] = piv2[2];
    iv[3] = piv2[3];

    iv[4] = piv1[0];
    iv[5] = piv1[1];
    iv[6] = piv1[2];
    iv[7] = piv1[3];

    salsa20.setIv(iv);
    QByteArray output (296, 0x00);
    salsa20.processBytes(reinterpret_cast<const uint8_t*>(data.data()), reinterpret_cast<uint8_t*>(output.data()), data.size());

    return output;
}

void GT7TelemetryReceiver::readPendingDatagrams()
{
    while (m_socket->hasPendingDatagrams())
    {
        QList <PTelemetryPoint> pendingPackages;
        m_lastTimeStamps.push_back(QTime::currentTime());
        QNetworkDatagram datagram = m_socket->receiveDatagram();
        if (!datagram.isValid())
        {
            DBG_MSG << "Invalid datagram received, expected " << (m_lastSequenceNumbers.back() + 1);
        }

        PTelemetryPointGT7 p;
        if (magicValid(datagram.data()))
        {
            DBG_MSG << ("Unencrypted datagram received.");
            p = PTelemetryPointGT7 (new TelemetryPointGT7(datagram.data()));
        }
        else
        {
            QByteArray unencrypted = decrypt(datagram.data());
            p = PTelemetryPointGT7 (new TelemetryPointGT7(unencrypted));
        }

        if (p->sequenceNumber() != m_lastSequenceNumbers.back() + 1)
        {
            if (m_lastSequenceNumbers.contains(p->sequenceNumber()))
            {
                DBG_MSG << "Double receive of telemetry package, sequence " << p->sequenceNumber();
                continue;
            }
            if ((p->sequenceNumber() - m_lastSequenceNumbers.back()) < 60 && !m_previousPackage.isNull())
            {
                DBG_MSG << "Lost" << (p->sequenceNumber() - m_lastSequenceNumbers.back()) << "packages. Using interpolator.";
                pendingPackages.append(m_interpolator.interpolate(m_previousPackage,p));
            }
            else
            {
                DBG_MSG << ("Receiver: Start of new telemetry sequence, d=" + QString::number (int(p->sequenceNumber()) - int(m_lastSequenceNumbers.back())).toLatin1()) << p->sequenceNumber() << m_lastSequenceNumbers.back();
                if (m_lastTimeStamps.size () >= 2)
                {
                    DBG_MSG << m_lastTimeStamps[m_lastTimeStamps.size()-2].toString("ss.zzz") << m_lastTimeStamps.back().toString("ss.zzz");
                }
                //DBG_MSG << (datagram.data() == s_prevDatagram.data());
            }
        }

        pendingPackages.append(p);
        m_previousPackage = p;

        m_lastSequenceNumbers.push_back (p->sequenceNumber());
        while(m_lastSequenceNumbers.size() > 5)
        {
            m_lastSequenceNumbers.pop_front();
            m_lastTimeStamps.pop_front();
        }

        for (auto curp : pendingPackages)
        {
            emit newTelemetryPoint(QSharedPointer<TelemetryPoint>(curp));
        }
    }
}

void GT7TelemetryReceiver::sendHeartBeat()
{
    //qInfo("Send heart beat");
    m_socket->writeDatagram("A", 1, QHostAddress(g_globalConfiguration.hostAddress()), 33739);
}
