#include "Laps.h"
#include "sb/cardata/TelemetryPointGT7.h"

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

PLap Lap::loadLap(QString filename, size_t index)
{
    auto all = Lap::loadLaps(filename);
    if (all.size() < index+1)
    {
        return PLap();
    }
    return all[index];
}

QList<PLap> Lap::loadLaps(QString filename)
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
            DBG_MSG << "At:" << (curIndex / 296);
            auto curData = data;//.mid (curIndex, curIndex + 296);
            auto magic = curData.mid(0, 4);
            if (magic[0] == 0x30 && magic[1] == 0x53 && magic[2] == 0x37 && magic[3] == 0x47)
            {
                //DBG_MSG << "unencrypted telemetry package";
            }
            else
            {
                //DBG_MSG << "encrypted telemetry package";
                //TODO decrypt
            }

            PTelemetryPointGT7 p (new TelemetryPointGT7(curData));

            if (loader.isNull() || loader->points()[0]->currentLap() != p->currentLap())
            {
                DBG_MSG << "new lap";
                if (!loader.isNull())
                {
                    DBG_MSG << "append lap";
                    result.append(loader);
                }
                loader = PLap(new Lap());
                DBG_MSG << "new lap done";
            }

            loader->appendTelemetryPoint(p);

            curIndex += 296;
        }

        DBG_MSG << "loaded points";

        if (!loader.isNull())
        {
            DBG_MSG << "append final lap";
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
