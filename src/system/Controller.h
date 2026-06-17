#pragma once

#include <QObject>
#include <QElapsedTimer>
#include "src/system/DashBuilder.h"
#include "src/cardata/TelemetryPoint.h"

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
    unsigned m_previousSequenceNumber = 0;
    QColor m_currentColor;
    QElapsedTimer m_timer;
    QElapsedTimer m_fpsTimer;
};

typedef QSharedPointer<Controller> PController;
