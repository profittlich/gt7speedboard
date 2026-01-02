#pragma once

#include "sb/cardata/TelemetryPoint.h"
#include "sb/trackdata/Track.h"
#include "sb/system/State.h"
#include <QObject>
#include <QColor>
#include <QWidget>
#include <QStackedWidget>
#include <QJsonValue>
#include <QJsonObject>

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

class Component : public QObject
{
    Q_OBJECT

public:
    Component (const QJsonValue json) : m_permissionsSet(false), m_json(json), m_stacker(nullptr) {}

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
        for (auto i : m_floatParameters)
        {
            result.append(*i);
        }

        return result;
    }

    void setFloatParameter (ComponentParameter<float> & p, bool overwritePresets = false) {
        if (m_floatParameters.contains(p.name()))
        {
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

    QList<ComponentParameter<QString>> getStringParameters()
    {
        QList<ComponentParameter<QString>> result = QList<ComponentParameter<QString>>();
        for (auto i : m_stringParameters)
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

    const QJsonValue initialJson() { return m_json; }

    virtual QWidget * getWidget() const { return nullptr; }

    virtual QString title () const { return defaultTitle(); }
    virtual QString defaultTitle () const = 0;

    // Derived classes MUST IMPLEMENT these static functions:
    //
    // static QString description ();
    // static QList<QString> actions ();
    // static QString componentId ();
    //

    virtual void newPoint(PTelemetryPoint curPoint) { Q_UNUSED(curPoint) };
    virtual void pointFinished(PTelemetryPoint curPoint) { Q_UNUSED(curPoint) };

    float baseFontSize () { return 10; }

    virtual void newSession() {};
    virtual void completedLap(PLap lastLap, bool isFullLap) { Q_UNUSED(lastLap) Q_UNUSED(isFullLap) }
    virtual void pitStop() {};

    virtual void newTrack(PTrack track) { Q_UNUSED(track) }
    virtual void maybeNewTrack(PTrack track) { Q_UNUSED(track) }
    virtual void leftTrack() {};

    virtual void callAction(QString a) { Q_UNUSED(a) };
    virtual void shutdown() {};

    virtual QColor signalColor() { return QColor(); }
    bool canFullScreenSignal () { return m_canFullScreenSignal; }
    virtual bool raise() { return false; }
    bool canRaise () { return m_canRaise; }
    virtual bool gotoPage() { return false; }
    bool canGotoPage () { return m_canGotoPage; }

    void setStacker (QStackedWidget * w, size_t idx) { m_stacker = w; m_stackIndex = idx; }
    QStackedWidget * stacker() { return m_stacker; }
    size_t stackIndex() { return m_stackIndex; }

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
        presetSwitched();
    }

    virtual void presetSwitched() {}
    virtual void parameterChanged(const PComponentParameterFloat &) {}
    virtual void parameterChanged(const PComponentParameterString &) {}

protected:
    void addComponentParameter (const PComponentParameterFloat & p)
    {
        m_floatParameters[p->name()] = p;
    }
    void addComponentParameter (const PComponentParameterString & p)
    {
        m_stringParameters[p->name()] = p;
    }

signals:
    void setTitleSuffix(QString);

private:
    bool m_permissionsSet;
    bool m_canRaise;
    bool m_canGotoPage;
    bool m_canFullScreenSignal;
    QJsonValue m_json;
    QStackedWidget * m_stacker;
    size_t m_stackIndex;
    PState m_state;
    QMap<QString, PComponentParameterFloat> m_floatParameters;
    QMap<QString, PComponentParameterString> m_stringParameters;
};

typedef QSharedPointer<Component> PComponent;
