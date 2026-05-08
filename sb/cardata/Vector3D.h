#pragma once

#include <QSharedPointer>
#include <cfloat>
#include <cmath>

template<typename T>
class Vector3D
{
public:
    Vector3D() = default;

    Vector3D(const T &px, const T &py, const T &pz)
    {
        m_x = px;
        m_y = py;
        m_z = pz;
    }

    T distanceTo (const Vector3D<T> & p2) const
    {
        const float dx = p2.x() - x();
        const float dy = p2.y() - y();
        const float dz = p2.z() - z();
        return std::sqrt(dx*dx + dy*dy + dz*dz);
    }

    T flatDistanceTo (const Vector3D<T> & p2) const
    {
        const float dx = p2.x() - x();
        const float dz = p2.z() - z();
        return std::sqrt(dx*dx + dz*dz);
    }

    T angle(const Vector3D<T> & p2) const
    {
        T s = std::sqrt(
                      std::pow(x(), 2) +
                      std::pow(y(), 2) +
                      std::pow(z(), 2))
                  * std::sqrt(
                      std::pow(p2.x(),2) +
                      std::pow(p2.y(), 2) +
                      std::pow(p2.z(), 2));

        if (s <= std::numeric_limits<T>::epsilon())
        {
            return 0;
        }

        T a = x() * p2.x() + y() * p2.y() + z() * p2.z() / s;
        if (a > 1)
        {
            a = 1;
        }
        T r = std::acos(a);
        return r;
    }


    void setX (const T &x) { m_x = x; }
    void setY (const T &y) { m_y = y; }
    void setZ (const T &z) { m_z = z; }

    const T& x() const { return m_x; }
    const T& y() const { return m_y; }
    const T& z() const { return m_z; }

private:
    T m_x;
    T m_y;
    T m_z;
};

