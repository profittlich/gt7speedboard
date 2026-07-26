#pragma once

#include "TelemetryInterpolator.h"

class LinearInterpolator : public TelemetryInterpolator
{
public:
    QList<PTelemetryPoint> interpolate (PTelemetryPoint p1, PTelemetryPoint p2) override;
};
