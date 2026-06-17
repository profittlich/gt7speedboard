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
    else if (state()->comparisonLaps.contains("ref-a") && state()->currentLap->trackDetector()->detectedTrack().get() == state()->comparisonLaps["ref-a"]->lap->trackDetector()->detectedTrack().get()) //(!state()->currentLap->trackDetector()->trackFound() || state()->comparisonLaps["ref-a"]->lap->trackName() == state()->currentLap->trackName()))
    {
        progress = state()->comparisonLaps["progress"] = state()->comparisonLaps["ref-a"];
        state()->invisibleComparisonLaps.insert("progress");
    }
    else if (state()->comparisonLaps.contains("ref-b") && state()->currentLap->trackDetector()->detectedTrack().get() == state()->comparisonLaps["ref-b"]->lap->trackDetector()->detectedTrack().get()) // && (!state()->currentLap->trackDetector()->trackFound() || state()->comparisonLaps["ref-b"]->lap->trackName() == state()->currentLap->trackName()))
    {
        progress = state()->comparisonLaps["progress"] = state()->comparisonLaps["ref-b"];
        state()->invisibleComparisonLaps.insert("progress");
    }
    else if (state()->comparisonLaps.contains("ref-c") && state()->currentLap->trackDetector()->detectedTrack().get() == state()->comparisonLaps["ref-c"]->lap->trackDetector()->detectedTrack().get()) // && (!state()->currentLap->trackDetector()->trackFound() || state()->comparisonLaps["ref-c"]->lap->trackName() == state()->currentLap->trackName()))
    {
        progress = state()->comparisonLaps["progress"] = state()->comparisonLaps["ref-c"];
        state()->invisibleComparisonLaps.insert("progress");
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