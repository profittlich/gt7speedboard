#pragma once

#include <QObject>
#include <QSharedPointer>
#include <sb/cardata/TelemetryPoint.h>

class TelemetryReceiver : public QObject
{
Q_OBJECT

public:
    virtual void start() = 0;
    virtual void stop() = 0;
    virtual bool isRunning() const = 0;
    virtual float telemetryFps() const = 0;

    virtual void startRecording() = 0;
    virtual void stopRecording() = 0;

signals:
    void newTelemetryPoint(PTelemetryPoint);
};

typedef QSharedPointer<TelemetryReceiver> PTelemetryReceiver;
