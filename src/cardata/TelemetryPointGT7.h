#pragma once

#include <cstdint>
#include <src/cardata/TelemetryPoint.h>

class TelemetryPointGT7 : public TelemetryPoint
{
public:
    TelemetryPointGT7(const QByteArray & data);

    virtual QByteArray getData() override;
    virtual PTelemetryPoint copy() override;

    virtual int getInt(size_t key) override;

    virtual QMap<QString, size_t> getIntKeys() override;

    QByteArray makeGT7Package(size_t targetSize = 296);
    void reconstructData();

    /* SETTERS */
    void setCarID(const int32_t & v) { m_carID = v; }
    void setCarCategory (QString val) { m_carCategory = val; } // C

    void setUnknown28(const uint32_t & v) { m_unknown28 = v; }
    void setUnknown40(const uint32_t & v) { m_unknown40 = v; }
    void setUnknown93(const uint32_t & v) { m_unknown93 = v; }
    void setUnknownA0(const uint32_t & v) { m_unknownA0 = v; }
    void setUnknownD4(const uint32_t & v) { m_unknownD4 = v; }
    void setUnknownD8(const uint32_t & v) { m_unknownD8 = v; }
    void setUnknownDC(const uint32_t & v) { m_unknownDC = v; }
    void setUnknownE0(const uint32_t & v) { m_unknownE0 = v; }
    void setUnknownE4(const uint32_t & v) { m_unknownE4 = v; }
    void setUnknownE8(const uint32_t & v) { m_unknownE8 = v; }
    void setUnknownEC(const uint32_t & v) { m_unknownEC = v; }
    void setUnknownF0(const uint32_t & v) { m_unknownF0 = v; }
    void setUnknown100(const uint32_t & v) { m_unknown100 = v; }
    void setUnknown144(const uint32_t & v) { m_unknown144 = v; }
    void setUnknown148(const uint32_t & v) { m_unknown148 = v; }
    void setUnknown154(const uint32_t & v) { m_unknown154 = v; }

    /* GETTERS */
    const int32_t & carID() const { return m_carID; }
    const QString & carCategory() const { return m_carCategory; } // C

    const uint32_t & unknown28() const { return m_unknown28; }
    const uint32_t & unknown40() const { return m_unknown40; }
    const uint32_t & unknown93() const { return m_unknown93; }
    const uint32_t & unknownA0() const { return m_unknownA0; }
    const uint32_t & unknownD4() const { return m_unknownD4; }
    const uint32_t & unknownD8() const { return m_unknownD8; }
    const uint32_t & unknownDC() const { return m_unknownDC; }
    const uint32_t & unknownE0() const { return m_unknownE0; }
    const uint32_t & unknownE4() const { return m_unknownE4; }
    const uint32_t & unknownE8() const { return m_unknownE8; }
    const uint32_t & unknownEC() const { return m_unknownEC; }
    const uint32_t & unknownF0() const { return m_unknownF0; }
    const uint32_t & unknown100() const { return m_unknown100; }
    const uint32_t & unknown144() const { return m_unknown144; }
    const uint32_t & unknown148() const { return m_unknown148; }
    const uint32_t & unknown154() const { return m_unknown154; }

private:
    QByteArray m_data;

    /* PROPERTIES */
    int32_t m_carID;
    QString m_carCategory; // C

    uint32_t m_unknown28;
    uint32_t m_unknown40;
    uint32_t m_unknown93;
    uint32_t m_unknownA0;
    uint32_t m_unknownD4;
    uint32_t m_unknownD8;
    uint32_t m_unknownDC;
    uint32_t m_unknownE0;
    uint32_t m_unknownE4;
    uint32_t m_unknownE8;
    uint32_t m_unknownEC;
    uint32_t m_unknownF0;
    uint32_t m_unknown100;
    uint32_t m_unknown144;
    uint32_t m_unknown148;
    uint32_t m_unknown154;
};

typedef QSharedPointer<TelemetryPointGT7> PTelemetryPointGT7;
