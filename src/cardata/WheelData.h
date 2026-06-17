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

