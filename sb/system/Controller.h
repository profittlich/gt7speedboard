#pragma once

#include <QObject>
#include <QElapsedTimer>
#include "sb/system/DashBuilder.h"
#include "sb/cardata/TelemetryPoint.h"

class Controller : public QObject
{
    Q_OBJECT
public:
    Controller () : m_state(new State()) {}

    void setDash(PDash d);
    PDash dash();
    PState state();

public slots:
    void newTelemetryPoint(PTelemetryPoint);

private:
    PDash m_dash;
    PState m_state;
    unsigned m_previousSequenceNumber;
    QColor m_currentColor;
    QElapsedTimer m_timer;
    QElapsedTimer m_fpsTimer;
};

typedef QSharedPointer<Controller> PController;
