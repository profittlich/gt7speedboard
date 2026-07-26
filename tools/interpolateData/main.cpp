#include <iostream>

#include "src/system/Laps.h"
#include "src/cardata/LinearInterpolator.h"

void quietDebugMessageHandler(QtMsgType type, const QMessageLogContext & context, const QString & txt)
{
}

void simpleDebugMessageHandler(QtMsgType type, const QMessageLogContext & context, const QString & txt)
{
    std::cout << "Log: " << txt.toStdString() << std::endl;
}


int main(int argc, char *argv[])
{
    qInstallMessageHandler(quietDebugMessageHandler);
    std::cout << "Interpolate data" << std::endl;

    if (argc < 2)
    {
        std::cout << "usage: " << argv[0] << "<infile> [<outfile>]" << std::endl;
    }

    PLap lap = Lap::loadLap(argv[1], false);
    PLap filledLap (new Lap());

    qInstallMessageHandler(simpleDebugMessageHandler);

    LinearInterpolator inter;

    if (!lap.isNull())
    {
        auto prev = lap->points()[0];
        filledLap->appendTelemetryPoint(prev);

        int counter = 1;
        for (auto cur : lap->points())
        {
            std::cout << counter++ << ": " << cur->sequenceNumber() << std::endl;
            if (cur->sequenceNumber() - prev->sequenceNumber() == 1)
            {
                std::cout << "Identical number: " << cur->sequenceNumber();
            }
            if (cur->sequenceNumber() - prev->sequenceNumber() > 1)
            {
                std::cout << prev->sequenceNumber() << "->" << cur->sequenceNumber() << ": " << (cur->sequenceNumber() - prev->sequenceNumber()) << std::endl;
                auto newp = inter.interpolate(prev, cur);
                std::cout << "Generated " << newp.size() << std::endl;
                for (auto i : newp)
                {
                    filledLap->appendTelemetryPoint(i);
                    DBG_MSG << "X Positions: " << i->sequenceNumber() << cur->position().x() << i->position().x();
                }
            }
            filledLap->appendTelemetryPoint(cur);
            prev = cur;
        }
    }

    if (argc >= 3)
    {
        std::cout << "Save interpolated lap" << std::endl;
        filledLap->saveLap(argv[2]);
    }

    return 0;
}