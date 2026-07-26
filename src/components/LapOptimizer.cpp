#include "src/components/LapOptimizer.h"

#include "src/components/ComponentFactory.h"



LapOptimizer::LapOptimizer () : Component()
{
    m_optimizingLap = PLap(new Lap());
    m_optimizingLap->setTrackDetector(PTrackDetector (new TrackDetector()));
}

QWidget * LapOptimizer::getWidget() const
{
    return nullptr;
}

QString LapOptimizer::defaultTitle () const
{
    return "Lap Optimizer";
}

void LapOptimizer::newPoint(PTelemetryPoint p)
{
    PComparisonLap optimized;
    if (!state()->comparisonLaps.contains("opt"))
    {
        if (m_preparingOptimized.isNull())
        {
            m_preparingOptimized = PComparisonLap(new ComparisonLap());
            m_preparingOptimized->lap = PLap(new Lap());
            m_preparingOptimized->lap->setTrackDetector(PTrackDetector (new TrackDetector()));
            PComparisonLap init;
            //if (!state()->comparisonLaps.contains("best"))
            //{
            //init = state()->comparisonLaps["best"];
            //}

            if (!init.isNull())
            {
                for (auto i : init->lap->points())
                {
                    m_preparingOptimized->lap->appendTelemetryPoint(i->copy()); // Copy the points, because we'll manipulate the sequence numbers
                }

            }
        }
        optimized = m_preparingOptimized;

    }
    else
    {
        optimized = state()->comparisonLaps["opt"];
    }

    if (optimized->lap->points().empty())
    {
        if (m_optimizingLap->points().size() != state()->currentLap->points().size())
        {
            for (auto i : state()->currentLap->points())
            {
                m_optimizingLap->appendTelemetryPoint(i->copy()); // Copy the points, because we'll manipulate the sequence numbers
            }
            DBG_MSG << "now in opt:" << m_optimizingLap->points().size();
        }
        else
        {
            m_optimizingLap->appendTelemetryPoint(p->copy());
        }
        m_curIndex = optimized->closestPoint;;
        m_curLiveIndex = state()->currentLap->points().size();
    }
    else
    {
        bool nowBraking = p->brake() > 2 || (optimized->hasClosestPoint && optimized->lap->points()[optimized->closestPoint]->brake() > 2); // todo global constant
        if (nowBraking != m_curBrake)
        {
            m_curBrake = nowBraking;
            if (nowBraking)
            {
                auto lenOpt = optimized->closestPoint - m_curIndex;
                auto lenLive = state()->currentLap->points().size() - m_curLiveIndex;

                if (lenOpt > lenLive || lenOpt == 0)
                {
                    // insert new segment
                    for (size_t i = m_curLiveIndex; i < m_curLiveIndex + lenLive; ++i)
                    {
                        m_optimizingLap->appendTelemetryPoint(state()->currentLap->points()[i]->copy());
                    }
                    DBG_MSG << "now in opt w/ new:" << m_optimizingLap->points().size() << lenOpt << lenLive;
                }
                else
                {
                    // insert old segment
                    for (size_t i = m_curIndex; i < m_curIndex + lenOpt; ++i)
                    {
                        m_optimizingLap->appendTelemetryPoint(optimized->lap->points()[i]->copy());
                    }
                    DBG_MSG << "now in opt w/ old:" << m_optimizingLap->points().size() << lenOpt << lenLive;
                }
                m_curLiveIndex = state()->currentLap->points().size() - 1;
                m_curIndex = optimized->closestPoint-1;

            }
        }
    }

    //DBG_MSG << "Points:" << m_optimizingLap->points().size() << optimized->lap->points().size();
/*
  //      if len(self.data.optimizedLap.points) == 0:
  //          self.data.curOptimizingLap.points.append(copy.deepcopy(curPoint))
  //          if len(self.data.curOptimizingLap.points) != len(self.data.curLap.points):
  //              self.data.curOptimizingLap.points = copy.deepcopy(self.data.curLap.points)
  //          self.curOptimizingLiveIndex = len(self.data.curLap.points)
  //          self.curOptimizingIndex = self.data.closestIOptimized
  //      else:
  //          nowBraking = curPoint.brake > 50 or self.data.optimizedLap.points[self.data.closestIOptimized].brake > 50
  ///          if nowBraking != self.curOptimizingBrake:
  //              self.curOptimizingBrake = nowBraking
  //              if nowBraking:
  //                  lenOpt = self.data.closestIOptimized - self.curOptimizingIndex
  //                  lenLive = len(self.data.curLap.points) - self.curOptimizingLiveIndex
  //                  if lenOpt > lenLive or lenOpt == 0:
  //                      logPrint("Current segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex, len(self.data.curOptimizingLap.points), len(self.data.curLap.points))
                        self.data.curOptimizingLap.points += copy.deepcopy(self.data.curLap.points[self.curOptimizingLiveIndex:-1])
                        self.data.improvedOptimization = True
                    else:
                        logPrint("Previous segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex)
                        self.data.curOptimizingLap.points += self.data.optimizedLap.points[self.curOptimizingIndex:self.data.closestIOptimized-1]
  //                  self.curOptimizingLiveIndex = len(self.data.curLap.points)-1
  //                  self.curOptimizingIndex = self.data.closestIOptimized-1
*/
}

void LapOptimizer::completedLap(PLap, bool)
{
    PComparisonLap optimized;

    if (!state()->comparisonLaps.contains("opt"))
    {
        optimized = m_preparingOptimized;
    }
    else
    {
        optimized = state()->comparisonLaps["opt"];
    }

    auto lenOpt = optimized->closestPoint - m_curIndex;
    auto lenLive = state()->currentLap->points().size() - m_curLiveIndex;

    if (lenOpt > lenLive || lenOpt == 0)
    {
        // insert new segment
        for (size_t i = m_curLiveIndex; i < m_curLiveIndex + lenLive; ++i)
        {
            m_optimizingLap->appendTelemetryPoint(state()->currentLap->points()[i]->copy());
        }
        DBG_MSG << "now in opt w/ new at end:" << m_optimizingLap->points().size() << lenOpt << lenLive;
    }
    else
    {
        // insert old segment
        for (size_t i = m_curIndex; i < m_curIndex + lenOpt; ++i)
        {
            m_optimizingLap->appendTelemetryPoint(optimized->lap->points()[i]->copy());
        }
        DBG_MSG << "now in opt w/ old at end:" << m_optimizingLap->points().size() << lenOpt << lenLive;
    }

    m_optimizingLap->updateValidity();
    DBG_MSG << "OptTrck:" << m_optimizingLap->trackName(true);

    if (m_optimizingLap->valid())
    {
        DBG_MSG << "Update optimized lap:" << m_optimizingLap->points().front()->position().distanceTo(m_optimizingLap->points().back()->position());
        auto newCL = PComparisonLap(new ComparisonLap());
        newCL->lap = m_optimizingLap;
        state()->comparisonLaps["opt"] = newCL;
    }
    else
    {
        DBG_MSG << "Invalid optimizing lap";
    }

    PTrackDetector trk = m_optimizingLap->trackDetector();
    m_optimizingLap = PLap(new Lap());
    m_optimizingLap->setTrackDetector(trk);
    m_curIndex = 0;
    m_curLiveIndex = 0;
    m_curBrake = false;

    publishOptimizingLap();
/*
        //lenOpt = self.data.closestIOptimized - self.curOptimizingIndex
        //lenLive = len(self.data.curLap.points) - self.curOptimizingLiveIndex
        //if lenOpt > lenLive or lenOpt == 0:
            //logPrint("Current final segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex)
            self.data.curOptimizingLap.points += copy.deepcopy(self.data.curLap.points[self.curOptimizingLiveIndex:])
        //else:
            logPrint("Previous final segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex)
            self.data.curOptimizingLap.points += copy.deepcopy(self.data.optimizedLap.points[self.curOptimizingIndex:])
        if len(self.data.curOptimizingLap.points) > 100 and self.data.curOptimizingLap.points[0].distance(self.data.curOptimizingLap.points[-1]) < 20.0 and not self.data.curLapInvalidated:
            self.data.optimizedLap = self.data.curOptimizingLap
            if self.cfg.developmentMode:
                saveThread = Worker(self.appendOptimizedLap, "Optimized lap saved.", 1.0, (self.data.optimizedLap, "optimized",))
                self.data.threadpool.start(saveThread)
            logPrint("Optimized lap:", len(self.data.optimizedLap.points), "points vs.", len(self.data.curLap.points))
        else:
            logPrint("Discard current lap for optimization: Not a complete lap, pts:", len(self.data.curOptimizingLap.points))
            if len(self.data.curOptimizingLap.points) > 0:
                logPrint("Discard current lap for optimization: Not a complete lap, dist:", self.data.curOptimizingLap.points[0].distance(self.data.curOptimizingLap.points[-1]))
        logPrint("new optimizing lap")
        self.data.curOptimizingLap = Lap()
        self.data.improvedOptimization = False
        self.curOptimizingLiveIndex = 0
        self.curOptimizingIndex = 0
        self.curOptimizingBrake = False
*/
}

void LapOptimizer::publishOptimizingLap()
{
    auto newCL = PComparisonLap(new ComparisonLap());
    newCL->lap = m_optimizingLap;
    state()->comparisonLaps["opting"] = newCL;
#ifndef QT_DEBUG
    state()->invisibleComparisonLaps.insert("opting");
#endif
}

QString LapOptimizer::description ()
{
    return "Creates a synthetic lap with optimal brake points from previous laps";
}

QMap<QString, Action> LapOptimizer::actions ()
{
    return QMap<QString, Action>();
}

QString LapOptimizer::componentId ()
{
    return "LapOptimizer";
}


static ComponentFactory::RegisterComponent<LapOptimizer> reg(false);
