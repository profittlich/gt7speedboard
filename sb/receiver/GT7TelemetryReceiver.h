#pragma once

#include <QTimer>
#include <QUdpSocket>
#include <QByteArray>
#include <sb/receiver/TelemetryReceiver.h>


class GT7TelemetryReceiver : public TelemetryReceiver
{

public:
    GT7TelemetryReceiver();

    void start();
    void stop();
    bool isRunning() const { return m_isRunning; }
    float telemetryFps() const { return 59.94; }

    void startRecording() {}
    void stopRecording() {}

    static QByteArray decrypt(const QByteArray & data);
protected:
    bool magicValid(const QByteArray & data);

protected slots:
    void readPendingDatagrams();
    void sendHeartBeat();

private:
    QTimer m_heartBeatTimer;
    QUdpSocket * m_socket;
    bool m_isRunning;
    QList<uint32_t> m_lastSequenceNumbers;
};

typedef QSharedPointer<GT7TelemetryReceiver> PGT7TelemetryReceiver;
