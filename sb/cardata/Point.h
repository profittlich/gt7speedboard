#pragma once

#include <sb/cardata/Vector3D.h>
#include <QSharedPointer>

class Point
{
public:
    Point(const Vector3D<float> & p = Vector3D<float>(0,0,0), const Vector3D<float> & n = Vector3D<float>(0,1,0))
    {
        setPosition(p);
        setNormal(n);
    }

    void setPosition(const Vector3D<float> & v) { m_position = v; }
    const Vector3D<float> & position() const { return m_position; }

    void setNormal(const Vector3D<float> & v) { m_normal = v; }
    const Vector3D<float> & normal() const { return m_normal; }


private:
    Vector3D<float> m_position;
    Vector3D<float> m_normal;
};

typedef QSharedPointer<Point> PPoint;
