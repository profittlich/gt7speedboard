#pragma once

#include "src/components/Component.h"
#include "src/widgets/Graph.h"

#include <typeindex>

class DataGraph : public Component
{
public:
    DataGraph ();

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;

    virtual void parameterChanged(const PComponentParameterBoolean &) override;
    virtual void loaded() override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:
    void addDataPoint(int idx, std::type_index & type, int & keyIdx, int & field, PComponentParameterString & target, PComponentParameterFloat & scale, PComponentParameterFloat & offset, PTelemetryPoint & p);


private:
    Graph * m_widget = nullptr;
    int m_counter = 0;
    PTelemetryPoint m_previous;
    PComponentParameterString m_target;
    PComponentParameterString m_target2;
    PComponentParameterString m_target3;
    PComponentParameterString m_target4;
    PComponentParameterString m_target5;
    PComponentParameterFloat m_scale;
    PComponentParameterFloat m_scale2;
    PComponentParameterFloat m_scale3;
    PComponentParameterFloat m_scale4;
    PComponentParameterFloat m_scale5;
    PComponentParameterFloat m_offset;
    PComponentParameterFloat m_offset2;
    PComponentParameterFloat m_offset3;
    PComponentParameterFloat m_offset4;
    PComponentParameterFloat m_offset5;
    PComponentParameterBoolean m_useMinMax;
    PComponentParameterFloat m_minValue;
    PComponentParameterFloat m_maxValue;
    int m_idx = -1;
    std::type_index m_type;
    int m_field;
    int m_idx2 = -1;
    std::type_index m_type2;
    int m_field2;
    int m_idx3 = -1;
    std::type_index m_type3;
    int m_field3;
    int m_idx4 = -1;
    std::type_index m_type4;
    int m_field4;
    int m_idx5 = -1;
    std::type_index m_type5;
    int m_field5;
};
