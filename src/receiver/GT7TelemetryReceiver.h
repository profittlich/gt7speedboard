#pragma once

#include "src/cardata/TelemetryPointGT7.h"
#include <QTimer>
#include <QUdpSocket>
#include <QByteArray>
#include <src/receiver/TelemetryReceiver.h>
#include <src/cardata/LinearInterpolator.h>


class GT7TelemetryReceiver : public TelemetryReceiver
{

public:
    GT7TelemetryReceiver();

    bool isRunning() const { return m_isRunning; }
    float telemetryFps() const { return 59.94; }

    void startRecording() {}
    void stopRecording() {}

    static QByteArray decrypt(const QByteArray & data);

public slots:
    void start();
    void stop();

protected:
    bool magicValid(const QByteArray & data);

protected slots:
    void readPendingDatagrams();
    void sendHeartBeat();

private:
    QTimer * m_heartBeatTimer;
    QUdpSocket * m_socket = nullptr;
    bool m_isRunning = false;
    QList<uint32_t> m_lastSequenceNumbers;
    QList<QTime> m_lastTimeStamps;
    LinearInterpolator m_interpolator;
    PTelemetryPointGT7 m_previousPackage;
};

typedef QSharedPointer<GT7TelemetryReceiver> PGT7TelemetryReceiver;
