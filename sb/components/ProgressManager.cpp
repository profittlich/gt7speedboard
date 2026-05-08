#include "ProgressManager.h"
#include "ComponentFactory.h"


ProgressManager::ProgressManager ()
{

}

QWidget * ProgressManager::getWidget() const
{
    return nullptr;
}

QString ProgressManager::defaultTitle () const
{
    return "Progress Manager";
}

void ProgressManager::newPoint(PTelemetryPoint p)
{
    PComparisonLap progress;

    if (state()->comparisonLaps.contains("progress"))
    {
        progress = state()->comparisonLaps["progress"];
    }
    else if (state()->comparisonLaps.contains("ref-a"))
    {
        progress = state()->comparisonLaps["progress"] = state()->comparisonLaps["ref-a"];
    }
    else if (state()->comparisonLaps.contains("ref-b"))
    {
        progress = state()->comparisonLaps["progress"] = state()->comparisonLaps["ref-b"];
    }
    else if (state()->comparisonLaps.contains("ref-c"))
    {
        progress = state()->comparisonLaps["progress"] = state()->comparisonLaps["ref-c"];
    }

    if (!progress.isNull() && progress->hasClosestPoint)
    {
        state()->lapProgress = float(progress->closestPoint) / float(progress->lap->points().size());
    }
    else
    {
        state()->lapProgress = -1.0;
    }
}

void ProgressManager::completedLap(PLap lastLap, bool isFullLap)
{
    if (state()->comparisonLaps.contains("best"))
    {
        state()->comparisonLaps["progress"] = state()->comparisonLaps["best"];
    }
}

QString ProgressManager::description ()
{
    return "Detect the current lap progress for other components";
}

QMap<QString, Action> ProgressManager::actions ()
{
    return QMap<QString, Action>();
}

QString ProgressManager::componentId ()
{
    return "ProgressManager";
}

static ComponentFactory::RegisterComponent<ProgressManager> reg(false);