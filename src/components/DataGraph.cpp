#include "src/components/DataGraph.h"

#include "src/components/ComponentFactory.h"
#include "src/system/Configuration.h"

DataGraph::DataGraph () : Component(),
    m_target (new ComponentParameter<QString>("target","carSpeed", true)),
    m_target2 (new ComponentParameter<QString>("target2","rpm", true)),
    m_target3 (new ComponentParameter<QString>("target3","", true)),
    m_target4 (new ComponentParameter<QString>("target4","", true)),
    m_target5 (new ComponentParameter<QString>("target5","", true)),
    m_scale (new ComponentParameter<float>("scale", 1.0, true)),
    m_scale2 (new ComponentParameter<float>("scale2", 1.0, true)),
    m_scale3 (new ComponentParameter<float>("scale3", 1.0, true)),
    m_scale4 (new ComponentParameter<float>("scale4", 1.0, true)),
    m_scale5 (new ComponentParameter<float>("scale5", 1.0, true)),
    m_offset (new ComponentParameter<float>("offset", 0.0, true)),
    m_offset2 (new ComponentParameter<float>("offset2", 0.0, true)),
    m_offset3 (new ComponentParameter<float>("offset3", 0.0, true)),
    m_offset4 (new ComponentParameter<float>("offset4", 0.0, true)),
    m_offset5 (new ComponentParameter<float>("offset5", 0.0, true)),
    m_useMinMax (new ComponentParameter<bool>("fixed range", false, true)),
    m_minValue (new ComponentParameter<float>("minimum value", 0.0, true)),
    m_maxValue (new ComponentParameter<float>("maximum value", 100.0, true)),
    m_type(typeid(void)),
    m_type2(typeid(void)),
    m_type3(typeid(void)),
    m_type4(typeid(void)),
    m_type5(typeid(void))

{
    addComponentParameter(m_target);
    addComponentParameter(m_target2);
    addComponentParameter(m_target3);
    addComponentParameter(m_target4);
    addComponentParameter(m_target5);
    addComponentParameter(m_scale);
    addComponentParameter(m_scale2);
    addComponentParameter(m_scale3);
    addComponentParameter(m_scale4);
    addComponentParameter(m_scale5);
    addComponentParameter(m_offset);
    addComponentParameter(m_offset2);
    addComponentParameter(m_offset3);
    addComponentParameter(m_offset4);
    addComponentParameter(m_offset5);
    addComponentParameter(m_useMinMax);
    addComponentParameter(m_minValue);
    addComponentParameter(m_maxValue);

    m_widget = new Graph(nullptr);
    m_widget->setWidth(400);
    //m_widget->setYRange(0, 100);

    m_widget->setColor (0, QColor(255, 0, 0));
    m_widget->setColor (1, QColor(0, 255, 0));
    m_widget->setColor (2, QColor(0, 255, 255));
    m_widget->setColor (3, QColor(255, 255, 0));
    m_widget->setColor (4, QColor(255, 255, 255, 127));

    m_counter = 0;
}

void DataGraph::parameterChanged(const PComponentParameterBoolean &)
{
    m_idx = -1;
    m_idx2 = -1;
    m_idx3 = -1;
    m_idx4 = -1;
    m_idx5 = -1;

    if (m_useMinMax())
    {
        DBG_MSG << "Graph range:" << m_minValue << m_maxValue;
        m_widget->setYRange(m_minValue(), m_maxValue());
    }
}

void DataGraph::loaded()
{
    parameterChanged(nullptr);
}

QWidget * DataGraph::getWidget() const
{
    return m_widget;
}

QString DataGraph::defaultTitle () const
{
    return "Data";
}

void DataGraph::addDataPoint(int graphIdx, std::type_index & type, int & keyIdx, int & field, PComponentParameterString & target, PComponentParameterFloat & scale, PComponentParameterFloat & offset, PTelemetryPoint & p)
{
    if (keyIdx < 0)
    {
        auto keys = p->getFloatKeys();
        if (keys.contains(target()))
        {
            keyIdx = keys[target()];
            type = typeid(float);
            DBG_MSG << "Index:" << keyIdx << type.name();
        }
        else
        {
            keys = p->getIntKeys();
            if (keys.contains(target()))
            {
                keyIdx = keys[target()];
                type = typeid(int);
                DBG_MSG << "Index:" << keyIdx << type.name();
            }
            else
            {
                keys = p->getBoolKeys();
                if (keys.contains(target()))
                {
                    keyIdx = keys[target()];
                    type = typeid(bool);
                    DBG_MSG << "Index:" << keyIdx << type.name();
                }
                else
                {
                    keys = p->getVector3DKeys();
                    auto targetParts = target().split(":");
                    if (keys.contains(targetParts[0]))
                    {
                        keyIdx = keys[targetParts[0]];
                        type = typeid(Vector3D<float>);
                        field = 0;
                        if (targetParts[1] == "X")
                        {
                            field = 0;
                        }
                        else if (targetParts[1] == "Y")
                        {
                            field = 1;
                        }
                        else if (targetParts[1] == "Z")
                        {
                            field = 2;
                        }
                        DBG_MSG << "Index:" << keyIdx << type.name() << field;
                    }
                    else
                    {
                        keys = p->getWheelDataKeys();
                        auto targetParts = target().split(":");
                        if (keys.contains(targetParts[0]))
                        {
                            keyIdx = keys[targetParts[0]];
                            type = typeid(WheelData<float>);
                            if (targetParts[1] == "FL")
                            {
                                field = 0;
                            }
                            else if (targetParts[1] == "FR")
                            {
                                field = 1;
                            }
                            else if (targetParts[1] == "RL")
                            {
                                field = 2;
                            }
                            else if (targetParts[1] == "RR")
                            {
                                field = 3;
                            }
                            DBG_MSG << "Index:" << keyIdx << type.name() << field;
                        }
                    }
                }
            }
        }
    }

    if (keyIdx >= 0)
    {
        if (type == typeid(float))
        {
            m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getFloat(keyIdx) * scale() + offset())));
        }
        else if (type == typeid(int))
        {
            m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getInt(keyIdx) * scale() + offset())));
        }
        else if (type == typeid(bool))
        {
            m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), (p->getBool(keyIdx) ? 1 : 0) * scale() + offset())));
        }
        else if (type == typeid(Vector3D<float>))
        {
            switch (field)
            {
            case 0:
                m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getVector3D(keyIdx).x() * scale() + offset())));
                break;
            case 1:
                m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getVector3D(keyIdx).y() * scale() + offset())));
                break;
            case 2:
                m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getVector3D(keyIdx).z() * scale() + offset())));
                break;

            }
        }
        else if (type == typeid(WheelData<float>))
        {
            switch (field)
            {
            case 0:
                m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getWheelData(keyIdx).fl() * scale() + offset())));
                break;
            case 1:
                m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getWheelData(keyIdx).fr() * scale() + offset())));
                break;
            case 2:
                m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getWheelData(keyIdx).rl() * scale() + offset())));
                break;
            case 3:
                m_widget->addValue(graphIdx, m_counter, std::min(m_maxValue(), std::max(m_minValue(), p->getWheelData(keyIdx).rr() * scale() + offset())));
                break;
            }
        }
    }
}

void DataGraph::newPoint(PTelemetryPoint p)
{
    addDataPoint(0, m_type, m_idx, m_field, m_target, m_scale, m_offset, p);
    addDataPoint(1, m_type2, m_idx2, m_field2, m_target2, m_scale2, m_offset2, p);
    addDataPoint(2, m_type3, m_idx3, m_field3, m_target3, m_scale3, m_offset3, p);
    addDataPoint(3, m_type4, m_idx4, m_field4, m_target4, m_scale4, m_offset4, p);
    addDataPoint(4, m_type5, m_idx5, m_field5, m_target5, m_scale5, m_offset5, p);

    m_counter++;
    m_previous = p;
}



QString DataGraph::description ()
{
    return "Show telemetry data in a graph";
}

QMap<QString, Action> DataGraph::actions ()
{
    return QMap<QString, Action>();
}

QString DataGraph::componentId ()
{
    return "DataGraph";
}

static ComponentFactory::RegisterComponent<DataGraph> reg(true);
