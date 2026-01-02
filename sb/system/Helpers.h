#pragma once

#include <QString>
#include <QColor>
#include <QSharedPointer>
#include <QtCore/qdebug.h>
#include <qlogging.h>

QString indexToTime(size_t idx);

QString msToTime(unsigned ms);

#define DBG_MSG qDebug () << __FILE__ << "::" << __LINE__ << ":"

const float c_FPS = 59.94;

class ColorMapper
{
public:
    ColorMapper(float center, float spread) : m_center(center), m_spread(spread)
    {

    }

    virtual QColor getColor(float value) = 0;

    const float center () { return m_center; }
    const float spread () { return m_spread; }

private:
    float m_center;
    float m_spread;
};

typedef QSharedPointer<ColorMapper> PColorMapper;

class ColorMapperBlueGreenRed : public ColorMapper
{
public:
    ColorMapperBlueGreenRed (float center, float spread) : ColorMapper(center, spread) {}

    virtual QColor getColor(float value) override
    {
        QColor col;
        float hue = (1.0/3.0) - (value - center())/(3*spread());

        if (hue < 0)
        {
            hue = 0;
        }
        else if (hue > (2.0/3.0))
        {
            hue = (2.0/3.0);
        }
        col.setHsvF (hue, 1, 1);

        return col;
    }
};

class ColorMapperGreenRed : public ColorMapper
{
public:
    ColorMapperGreenRed (float center, float spread) : ColorMapper(center, spread) {}

    virtual QColor getColor(float value) override
    {
        QColor col;
        float hue = (1.0/6.0) - (value - center())/(6*spread());

        if (hue < 0)
        {
            hue = 0;
        }
        else if (hue > (1.0/3.0))
        {
            hue = (1.0/3.0);
        }
        col.setHsvF (hue, 1, 1);

        return col;
    }
};
