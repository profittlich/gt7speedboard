#pragma once

#include <QObject>
#include "sb/system/DashBuilder.h"
#include "sb/cardata/TelemetryPoint.h"

class Controller : public QObject
{
    Q_OBJECT
public:
    Controller () : m_state(new State()), m_currentStyle("") {}

    void setDash(PDash d);
    PDash dash();
    PState state();

public slots:
    void newTelemetryPoint(PTelemetryPoint);

private:
    PDash m_dash;
    PState m_state;
    unsigned m_previousSequenceNumber;
    QString m_currentStyle;
    QElapsedTimer m_timer;
};

typedef QSharedPointer<Controller> PController;
