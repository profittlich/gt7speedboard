#include "Laps.h"
#include "sb/cardata/TelemetryPointGT7.h"
#include <contrib/Salsa20-master/Source/Salsa20.h>
#include "sb/receiver/GT7TelemetryReceiver.h"

static const float c_quadSize = 10.0;

bool Lap::saveLap(QString filename)
{
    DBG_MSG << "Save to " << filename;
    QFile f(filename);
    f.open(QFile::WriteOnly);
    if (f.isOpen())
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
    if (all.size() < index+1)
    {
        return PLap();
    }
    return all[index];
}

QList<PLap> Lap::loadLaps(QString filename, bool detectTrack)
{
    QList<PLap> result;

    QFile f(filename);
    f.open(QFile::ReadOnly);
    if (f.isOpen())
    {
        //auto data = f.readAll();
        qsizetype curIndex = 0;
        size_t curLap = -10; // TODO why -10?
        PLap loader;
        //DBG_MSG << "Loaded file:" << data.size() << (data.size() / 296);
        //while (curIndex < data.size())
        QByteArray data;
        while((data = f.read(296)).size() == 296)
        {
            //DBG_MSG << "At:" << (curIndex / 296);
            auto curData = data;//.mid (curIndex, curIndex + 296);
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

            curIndex += 296;
        }

        DBG_MSG << "loaded points";

        if (!loader.isNull())
        {
            DBG_MSG << "append final lap" << loader->trackName();
            result.append(loader);
        }

        f.close();

        DBG_MSG << "set special points";
        for (size_t i = 1; i < result.size()-1; ++i)
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

QPair<size_t, float> Lap::findClosestPoint(PPoint p, size_t start, float cancelRange) const
{
#if 0
    int resultNew = 0;
    int xQuad = p->position().x()/c_quadSize;
    int yQuad = p->position().y()/c_quadSize;
    //DBG_MSG << "Search" << xQuad << yQuad;

    int qIdx = 100000 * xQuad + yQuad;

    float resultNewDist = 1000000;

        if (m_quadPoints.contains(qIdx))
        {
            float resultNewDist = 1000000;

            for (auto i : m_quadPoints[qIdx])
            {
                float newDist = p->position().distanceTo(m_points[i % m_points.size()]->position());
                if (newDist < resultNewDist)
                {
                    resultNewDist = newDist;
                    resultNew = i % m_points.size();
                }
            }
            for (int i = -15; i < 15; ++i)
            {
                if ((resultNew+i) < 0) continue;
                float newDist = p->position().distanceTo(m_points[(resultNew + i) % m_points.size()]->position());
                if (newDist < resultNewDist)
                {
                    resultNewDist = newDist;
                    resultNew = (resultNew + i) % m_points.size();
                }

            }
        }
#endif




    int result = 0;
    float resultDist = 1000000;
    bool inRange = false;
    //DBG_MSG << "start search";
    if (start > 60)
    {
        start -= 60;
    }
    for (int i = start; i < start + m_points.size(); ++i)
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
#if 0
    if (resultNew != result)
    {
        DBG_MSG << "Not equal:" << resultNew << result << (result - resultNew);
    }
#endif
    return QPair<size_t, float> (result, resultDist);
}

void Lap::appendTelemetryPoint(PTelemetryPoint p)
{
    if (!m_trackDetector.isNull())
    {
        m_trackDetector->addPoint(p);
    }
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
