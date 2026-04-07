#pragma once

#include "sb/cardata/TelemetryPoint.h"
#include "sb/system/Configuration.h"
#include "sb/trackdata/Track.h"
#include "sb/system/State.h"
#include "sb/system/Action.h"
#include <QObject>
#include <QColor>
#include <QWidget>
#include <QStackedWidget>

template <typename T>
class ComponentParameter
{
public:
    ComponentParameter (QString name, const T & v, bool useConfigs = false) : m_name(name), m_useConfigs(useConfigs), m_currentValue(v)
    {
    }

    void setUseConfigs(bool on)
    {
        m_useConfigs = on;
    }

    T & operator()()
    {
        return m_currentValue;
    }

    const QString & name() const { return m_name; }

    QMap<QString, T> getAll()
    {
        if (!m_currentConfig.isNull())
        {
            m_otherConfigs[m_currentConfig] = m_currentValue;
        }
        return m_otherConfigs;
    }

    void addPresetValue(QString preset, T value)
    {
        m_otherConfigs[preset] = value;
    }

    void overwritePresets(const QMap<QString, T> & src)
    {
        m_otherConfigs = src;
    }

    void switchToPreset(QString c)
    {
        if (!m_useConfigs)
        {
            qDebug("Ignore switch");
            return;
        }

        qDebug("Perform switch");

        if (!m_currentConfig.isNull())
        {
            m_otherConfigs[m_currentConfig] = m_currentValue;
        }

        if (!m_otherConfigs.contains(c))
        {
            m_otherConfigs[c] = m_currentValue;
        }

        m_currentConfig = c;
        m_currentValue = m_otherConfigs[c];
    }

private:
    QString m_name;
    bool m_useConfigs;
    T m_currentValue;
    QString m_currentConfig;
    QMap<QString, T> m_otherConfigs;
};

typedef QSharedPointer<ComponentParameter<float>> PComponentParameterFloat;
typedef QSharedPointer<ComponentParameter<QString>> PComponentParameterString;
typedef QSharedPointer<ComponentParameter<bool>> PComponentParameterBoolean;

class Component : public QObject
{
    Q_OBJECT

    friend class ComponentFactory;

public:
    Component () : m_permissionsSet(false), m_stacker(nullptr) {}

    virtual ~Component()
    {

    }

    void setPermissions (bool raiseAllowed, bool gotoPageAllowed, bool fullScreenSignalAllowed)
    {
        if (m_permissionsSet) throw std::runtime_error("Permissions for component " + this->title().toStdString() + " already set");
        m_canRaise = raiseAllowed;
        m_canGotoPage = gotoPageAllowed;
        m_canFullScreenSignal = fullScreenSignalAllowed;
        m_permissionsSet = true;
    }

    void setState(PState s) { m_state = s; }
    PState state() { return m_state; }

    QList<ComponentParameter<float>> getFloatParameters()
    {
        QList<ComponentParameter<float>> result = QList<ComponentParameter<float>>();
        for (auto i : m_floatParametersOrdered)
        {
            result.append(*i);
        }

        return result;
    }

    void setFloatParameter (ComponentParameter<float> & p, bool overwritePresets = false) {
        if (m_floatParameters.contains(p.name()))
        {
            DBG_MSG << p.name();
            (*m_floatParameters[p.name()])() = p();
            if (overwritePresets)
            {
                (*m_floatParameters[p.name()]).overwritePresets(p.getAll());
            }
            parameterChanged(m_floatParameters[p.name()]);
        }
    }

    ComponentParameter<float> floatParameter(const QString & key)
    {
        if (m_floatParameters.contains(key))
        {
            return *m_floatParameters[key];
        }
        return ComponentParameter<float>("", 0, false);
    }


    QList<ComponentParameter<bool>> getBooleanParameters()
    {
        QList<ComponentParameter<bool>> result = QList<ComponentParameter<bool>>();
        for (auto i : m_booleanParametersOrdered)
        {
            result.append(*i);
        }

        return result;
    }

    void setBooleanParameter (ComponentParameter<bool> & p, bool overwritePresets = false) {
        if (m_booleanParameters.contains(p.name()))
        {
            DBG_MSG << p.name();
            (*m_booleanParameters[p.name()])() = p();
            if (overwritePresets)
            {
                (*m_booleanParameters[p.name()]).overwritePresets(p.getAll());
            }
            parameterChanged(m_booleanParameters[p.name()]);
        }
    }

    ComponentParameter<bool> booleanParameter(const QString & key)
    {
        if (m_booleanParameters.contains(key))
        {
            return *m_booleanParameters[key];
        }
        return ComponentParameter<bool>("", false, false);
    }

    QList<ComponentParameter<QString>> getStringParameters()
    {
        QList<ComponentParameter<QString>> result = QList<ComponentParameter<QString>>();
        for (auto i : m_stringParametersOrdered)
        {
            result.append(*i);
        }

        return result;
    }

    void setStringParameter (ComponentParameter<QString> & p, bool overwritePresets = false)
    {
        if (m_stringParameters.contains(p.name()))
        {
            (*m_stringParameters[p.name()])() = p();
            if (overwritePresets)
            {
                (*m_stringParameters[p.name()]).overwritePresets(p.getAll());
            }
            parameterChanged(m_stringParameters[p.name()]);
        }
    }

    ComponentParameter<QString> stringParameter(const QString & key)
    {
        if (m_stringParameters.contains(key))
        {
            return *m_stringParameters[key];
        }
        return ComponentParameter<QString>("", "", false);
    }

    virtual QWidget * getWidget() const { return nullptr; }

    virtual QString title () const { return defaultTitle(); }
    virtual QString defaultTitle () const = 0;

    // Derived classes MUST IMPLEMENT these static functions:
    //
    // static QString description ();
    // static QMap<QString, Action> actions ();
    // static QString componentId ();
    //

    virtual void loaded() {};

    virtual void newPoint(PTelemetryPoint curPoint) { Q_UNUSED(curPoint) };
    virtual void pointFinished(PTelemetryPoint curPoint) { Q_UNUSED(curPoint) };

    float baseFontSize () { return 10 * g_globalConfiguration.fontScale(); }

    virtual void newSession() {};
    virtual void completedLap(PLap lastLap, bool isFullLap) { Q_UNUSED(lastLap) Q_UNUSED(isFullLap) }
    virtual void pitStop() {};

    virtual void newCircuit() {}
    virtual void newTrack(PTrack track) { Q_UNUSED(track) }
    virtual void maybeNewTrack(PTrack track) { Q_UNUSED(track) }
    virtual void leftTrack() {};
    virtual void leftCircuit() {};

    virtual void callAction(QString a) { Q_UNUSED(a) };
    virtual void shutdown() {};

    virtual QColor signalColor() const { return QColor(); }
    bool canFullScreenSignal () const { return m_canFullScreenSignal; }
    virtual bool raise() { return false; }
    bool canRaise () const { return m_canRaise; }
    virtual bool gotoPage() { return false; }
    bool canGotoPage () const { return m_canGotoPage; }

    void setStacker (QStackedWidget * w, size_t idx) { m_stacker = w; m_stackIndex = idx; }
    QStackedWidget * stacker() { return m_stacker; }
    size_t stackIndex() const { return m_stackIndex; }

    void switchToPreset(QString preset)
    {
        for (auto i : m_floatParameters)
        {
            i->switchToPreset(preset);
            parameterChanged(i);
        }
        for (auto i : m_stringParameters)
        {
            i->switchToPreset(preset);
            parameterChanged(i);
        }
        for (auto i : m_booleanParameters)
        {
            i->switchToPreset(preset);
            parameterChanged(i);
        }
        presetSwitched();
    }

    virtual void presetSwitched() {}
    virtual void parameterChanged(const PComponentParameterFloat &) {}
    virtual void parameterChanged(const PComponentParameterBoolean &) {}
    virtual void parameterChanged(const PComponentParameterString &) {}

    const QMap<QString, Action> & getActions () const { return m_actions; }
    const QString & getDescription () const { return m_description; }
    const QString & getComponentId () const { return m_componentId; }

protected:
    void addComponentParameter (const PComponentParameterFloat & p)
    {
        m_floatParameters[p->name()] = p;
        m_floatParametersOrdered.append(p);
    }
    void addComponentParameter (const PComponentParameterBoolean & p)
    {
        m_booleanParameters[p->name()] = p;
        m_booleanParametersOrdered.append(p);
    }
    void addComponentParameter (const PComponentParameterString & p)
    {
        m_stringParameters[p->name()] = p;
        m_stringParametersOrdered.append(p);
    }

signals:
    void setTitleSuffix(QString);

private:
    void setActions (QMap<QString, Action> a) { m_actions = a; }
    void setDescription (QString a) { m_description = a; }
    void setComponentId (QString a) { m_componentId = a; }

    bool m_permissionsSet;
    bool m_canRaise;
    bool m_canGotoPage;
    bool m_canFullScreenSignal;

    QStackedWidget * m_stacker;
    size_t m_stackIndex;
    PState m_state;
    QMap<QString, PComponentParameterFloat> m_floatParameters;
    QList<PComponentParameterFloat> m_floatParametersOrdered;
    QMap<QString, PComponentParameterBoolean> m_booleanParameters;
    QList<PComponentParameterBoolean> m_booleanParametersOrdered;
    QMap<QString, PComponentParameterString> m_stringParameters;
    QList<PComponentParameterString> m_stringParametersOrdered;

    QString m_componentId;
    QString m_description;
    QMap<QString, Action> m_actions;

};

typedef QSharedPointer<Component> PComponent;
