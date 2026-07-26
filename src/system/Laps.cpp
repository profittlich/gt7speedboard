#include "Laps.h"
#include "src/cardata/TelemetryPointGT7.h"
#include <contrib/Salsa20-master/Source/Salsa20.h>
#include "src/receiver/GT7TelemetryReceiver.h"

bool Lap::saveLap(QString filename)
{
    DBG_MSG << "Save to " << filename;
    QFile f(filename);

    if (f.open(QFile::WriteOnly))
    {
        DBG_MSG << "write data";
        if (!preceedingPoint().isNull())
        {
            DBG_MSG << "write preceeding";
            f.write(preceedingPoint()->getData());
        }
        DBG_MSG << "write points";
        for (auto i : points())
        {
            f.write(i->getData());
        }
        if (!succeedingPoint().isNull())
        {
            DBG_MSG << "write succeeding";
            f.write(succeedingPoint()->getData());
        }

        f.close();
        return true;
    }
    return false;
}

PLap Lap::loadLap(QString filename, bool detectTrack, size_t index)
{
    auto all = Lap::loadLaps(filename, detectTrack);
    if (all.size() < qsizetype(index)+1)
    {
        return PLap();
    }
    return all[index];
}

QList<PLap> Lap::loadLaps(QString filename, bool detectTrack)
{
    QList<PLap> result;

    QFile f(filename);

    if (f.open(QFile::ReadOnly))
    {
        PLap loader;

        QByteArray data;
        while((data = f.read(296)).size() == 296)
        {
            auto curData = data;
            auto magic = curData.mid(0, 4);
            if (magic[0] == 0x30 && magic[1] == 0x53 && magic[2] == 0x37 && magic[3] == 0x47)
            {
                //DBG_MSG << "unencrypted telemetry package";
            }
            else
            {
                //DBG_MSG << "encrypted telemetry package";
                curData = GT7TelemetryReceiver::decrypt(curData);
            }

            magic = curData.mid(0, 4);
            if (!(magic[0] == 0x30 && magic[1] == 0x53 && magic[2] == 0x37 && magic[3] == 0x47))
            {
                DBG_MSG << "bad data";
                return result;
            }

            PTelemetryPointGT7 p (new TelemetryPointGT7(curData));

            if (loader.isNull() || loader->points()[0]->currentLap() != p->currentLap())
            {
                DBG_MSG << "new lap" << p->currentLap();
                if (!loader.isNull())
                {
                    DBG_MSG << "append lap" << loader->trackName();
                    result.append(loader);
                }
                loader = PLap(new Lap());
                if (detectTrack)
                {
                    loader->setTrackDetector(PTrackDetector(new TrackDetector()));
                }
                DBG_MSG << "new lap done";
            }

            loader->appendTelemetryPoint(p);
        }

        DBG_MSG << "loaded points";

        if (!loader.isNull())
        {
            DBG_MSG << "append final lap" << loader->trackName();
            result.append(loader);
        }

        f.close();

        DBG_MSG << "set special points";
        for (qsizetype i = 1; i < result.size()-1; ++i)
        {
            result[i]->m_preceedingPoint = result[i-1]->points()[result[i-1]->points().size()-1];
            result[i]->m_succeedingPoint = result[i+1]->points()[0];
        }

        DBG_MSG << result.size() << "laps loaded";
        DBG_MSG << result[0].isNull();
        if (result[0]->points().size() <= 1)
        {
            DBG_MSG << "remove preceeding point";
            result.pop_front();
        }
        if (result[result.size()-1]->points().size() <= 1)
        {
            DBG_MSG << "remove succeeding point";
            result.pop_back();
        }

        DBG_MSG << result.size() << " laps to be returned";

    }

    return result;
}

void Lap::updateValidity()
{
    bool valid = true;
    if (m_points.size() > 0)
    {
        for (int i = 0 ; i < int(m_points.size())-1; ++i)
        {
            valid &= m_points[i]->position().distanceTo(m_points[i+1]->position()) < 5.0; // todo: constant
        }
        if (!valid)
        {
            DBG_MSG << "Invalidate lap due to jumps";
        }
        valid &= m_points.front()->position().distanceTo(m_points.back()->position()) < 20.0; // todo: constant
        if (!valid)
        {
            DBG_MSG << "Invalidate lap due to jumps or endpoint distance" << m_points.size() << m_points.front()->position().distanceTo(m_points.back()->position());
            DBG_MSG << reinterpret_cast <size_t> (m_points.data());
        }
    }
    else
    {
        DBG_MSG << "no points, lap invalid";
        valid = false;
    }

    m_valid &= valid;
}

QPair<size_t, float> Lap::findClosestPoint(PPoint p, size_t start, float cancelRange) const
{
    int result = 0;
    float resultDist = 1000000;
    bool inRange = false;
    //DBG_MSG << "start search";
    if (start > 60)
    {
        start -= 60; // todo: this seems sketchy
    }
    for (size_t i = start; i < start + m_points.size(); ++i)
    {
        float newDist = p->position().distanceTo(m_points[i % m_points.size()]->position());
        if (!inRange && newDist < cancelRange)
        {
            inRange = true;
        }
        else if (inRange && newDist > cancelRange * 1.1)
        {
            break;
        }
        if (newDist < resultDist)
        {
            resultDist = newDist;
            result = i % m_points.size();
            while (result < 0)
            {
                DBG_MSG << "adjust index";
                result += m_points.size();
            }
        }

    }

    return QPair<size_t, float> (result, resultDist);
}

void Lap::appendTelemetryPoint(PTelemetryPoint p)
{
    if (!m_trackDetector.isNull())
    {
        m_trackDetector->addPoint(p);
    }
    /*if (!m_points.empty() && p->position().distanceTo(m_points.back()->position()) > 5.0)
    {
        invalidate();
    }*/

    m_points.append(p);
    /*int xQuad = p->position().x()/c_quadSize;
    int yQuad = p->position().y()/c_quadSize;
    int qIdx = 100000 * xQuad + yQuad;
    if (!m_quadPoints.contains(qIdx))
    {
        m_quadPoints[qIdx] = QSet<size_t>();
    }
    m_quadPoints[qIdx].insert(m_points.size()-1);*/
    //DBG_MSG << "Add" << xQuad << yQuad << m_quadPoints.size() << m_quadPoints[qIdx].size();
}
