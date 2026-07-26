#pragma once

#include "TelemetryPoint.h"

class TelemetryInterpolator
{
public:
    virtual QList<PTelemetryPoint> interpolate (PTelemetryPoint p1, PTelemetryPoint p2) = 0;
};
