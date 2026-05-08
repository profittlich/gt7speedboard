#pragma once

#include <QObject>
#include <QFile>
#include "sb/cardata/TelemetryPoint.h"

class RawRecorder : public QObject
{
    Q_OBJECT
public:
    RawRecorder (QString filename) : m_filename(filename), m_recording(false) {}

public slots:
    void setFilename(QString filename);
    void start();
    void stop();
    void newTelemetryPoint(PTelemetryPoint);

private:
    QString m_filename;
    bool m_recording;
    QFile m_file;
};

typedef QSharedPointer<RawRecorder> PRawRecorder;
