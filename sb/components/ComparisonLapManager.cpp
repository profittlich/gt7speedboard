#include "sb/components/ComparisonLapManager.h"
#include "sb/system/Laps.h"

#include "sb/components/ComponentFactory.h"
#include "sb/system/Configuration.h"



ComparisonLapManager::ComparisonLapManager () : Component(), m_maxClosenessDistance(new ComponentParameter<float>("maxClosenessDistance", 20, false))
{
    addComponentParameter(m_maxClosenessDistance);
}

QWidget * ComparisonLapManager::getWidget() const
{
    return nullptr;
}

QString ComparisonLapManager::defaultTitle () const
{
    return "Comparison Lap Manager";
}

void ComparisonLapManager::newPoint(PTelemetryPoint p)
{
    if (!state()->currentLap->points().isEmpty() && p->position().distanceTo(state()->currentLap->points().back()->position()) > g_globalConfiguration.maxPointDistanceForValidLap())
    {
        DBG_MSG << "Current lap invalid";
        state()->currentLap->invalidate();
    }
    updateClosestPoints(p);
    updateNextCriticalPoints();
    m_cachedPt = p;
}

void ComparisonLapManager::updateClosestPoints (PTelemetryPoint p)
{
    for (auto curLap : state()->comparisonLaps.keys())
    {
        if (!state()->comparisonLaps[curLap]->lap->points().empty())
        {
            auto compLap = state()->comparisonLaps[curLap];
            auto closest = compLap->lap->findClosestPoint(p, compLap->closestPoint);
            if (closest.second <= (*m_maxClosenessDistance)())
            {
                compLap->hasClosestPoint = true;
                compLap->closestPoint = closest.first;
                //DBG_MSG << "closest: " <<  curLap << closest.first << closest.second;
            }
            else
            {
                compLap->hasClosestPoint = false;
                //qDebug() << "closest: " << compLap->name << "none";
            }
        }
    }
}

void ComparisonLapManager::updateNextCriticalPoints()
{
    for (auto curLap : state()->comparisonLaps.keys())
    {
        auto compLap = state()->comparisonLaps[curLap];
        if (compLap->hasClosestPoint)
        {
            size_t end = compLap->closestPoint + 5 * 60; // TODO: make configurable
            if (end > compLap->lap->points().size())
            {
                end = compLap->lap->points().size();
            }
            if (compLap->lap->points()[compLap->closestPoint]->brake() < 2) // TODO: make configurable
            {
                size_t i;
                for (i = compLap->closestPoint + 1; i < end; ++i)
                {
                    if (compLap->lap->points()[i]->brake() >= 2) // TODO: make configurable
                    {
                        compLap->nextBrake  = i;
                        break;
                    }
                }
                if (i == end)
                {
                    compLap->nextBrake = INT_MAX;
                }
                else
                {
                    //qDebug() << "next brake" << (compLap->nextBrake - compLap->closestPoint);
                }
            }
            else
            {
                compLap->nextBrake = INT_MAX;
            }
        }
    }
}

void ComparisonLapManager::completedLap(PLap lastLap, bool isFullLap)
{
    // CHECKS FOR COMPLETED LAP
    if (lastLap->lapTime() == -1)
    {
        DBG_MSG << "no lap time set";
        return;
    }
    auto loopEndDistance = lastLap->points().front()->position().distanceTo(lastLap->points().back()->position());
    if (loopEndDistance > g_globalConfiguration.maxPointDistanceForValidLap())
    {
        DBG_MSG << "Completed lap is not a closed loop:" << loopEndDistance << "m";
        lastLap->invalidate();
    }

    // LAST
    if (lastLap->points().size() > 1) // Ignore succeeding points of recordings
    {
        if (!state()->comparisonLaps.contains(("last")))
        {
            state()->comparisonLaps["last"] = PComparisonLap(new ComparisonLap());
        }
        auto lastCompLap = state()->comparisonLaps["last"];
        lastCompLap->lap = lastLap;
        //lastCompLap->lapTime = lastLap->lapTime();

        DBG_MSG << "Last lap: " << lastCompLap->lap->lapTime() << "ms";
    }

    // BEST
    if (lastLap->valid())
    {
        if (!state()->comparisonLaps.contains(("best")))
        {
            DBG_MSG << "Create best lap data structure";
            state()->comparisonLaps["best"] = PComparisonLap(new ComparisonLap());
        }
        auto bestCompLap = state()->comparisonLaps["best"];
        if (bestCompLap->lap.isNull() || bestCompLap->lap->lapTime() > lastLap->lapTime())
        {
            bestCompLap->lap = lastLap;
            //bestCompLap->lapTime = lastLap->lapTime();
        }
        DBG_MSG << "Best lap: " << bestCompLap->lap->lapTime() << "ms";
    }

    // PROGRESS
    if (state()->comparisonLaps.contains(("best")))
    {
        state()->comparisonLaps["progress"] = state()->comparisonLaps["best"];
    }

    // TODO update points again for new lap
    updateClosestPoints(m_cachedPt);
}

QString ComparisonLapManager::description ()
{
    return "Provide comparison laps for other components";
}

QMap<QString, Action> ComparisonLapManager::actions ()
{
    return QMap<QString, Action>();
}

QString ComparisonLapManager::componentId ()
{
    return "ComparisonLapManager";
}


static ComponentFactory::RegisterComponent<ComparisonLapManager> reg(false);
