#pragma once

#include<QSharedPointer>

template<typename T>
class WheelData
{
public:
    WheelData () = default;
    WheelData(const T & fl, const T & fr, const T & rl, const T & rr)
    {
        setFL(fl);
        setFR(fr);
        setRL(rl);
        setRR(rr);
    }

    void setFL(const T & v) { m_fl = v; }
    void setFR(const T & v) { m_fr = v; }
    void setRL(const T & v) { m_rl = v; }
    void setRR(const T & v) { m_rr = v; }

    const T & fl () const { return m_fl; }
    const T & fr () const { return m_fr; }
    const T & rl () const { return m_rl; }
    const T & rr () const { return m_rr; }

private:
    T m_fl;
    T m_fr;
    T m_rl;
    T m_rr;
};

template<typename T>
WheelData<T> operator*(float c, WheelData<T> w)
{
    return WheelData<T> (c * w.fl(), c * w.fr(), c * w.rl(), c * w.rr());
}

template<typename T>
WheelData<T> operator+(WheelData<T> w1, WheelData<T> w2)
{
    return WheelData<T> (w1.fl() + w2.fl(), w1.fr() + w2.fr(), w1.rl() + w2.rl(), w1.rr() + w2.rr());
}
