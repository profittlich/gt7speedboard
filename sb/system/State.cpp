#include "State.h"


void State::saveComparisonLap(QString key, QString fnKey)
{
    if (!comparisonLaps.contains(key))
    {
        addMessage("main", "Lap " + key + " not available");
        return;
    }

    QString fn = getStorageLocation().absolutePath() + "/" + fnKey + ".gt7lap";
    if (!comparisonLaps[key]->lap->saveLap(fn))
    {
        addMessage("main", "Could not save lap " + key);
    }
}

void State::loadComparisonLap(QString key, QString fnKey, bool absolutePath)
{
    PComparisonLap compLap (new ComparisonLap());
    PLap lap;
    if (absolutePath)
    {
        lap = Lap::loadLap(fnKey);
    }
    else
    {
        lap = Lap::loadLap(getStorageLocation().absolutePath() + "/" + fnKey + ".gt7lap");
    }
    if (!lap.isNull())
    {
        compLap->lap = lap;
        comparisonLaps[key] = compLap;
    }
    else
    {
        DBG_MSG << "Could not load file" << fnKey;
    }
}
