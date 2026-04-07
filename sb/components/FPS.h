#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include <QtCore/qdatetime.h>
#include <QElapsedTimer>

class FPS : public Component
{
public:
    FPS ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();


private:
    ColorLabel * m_widget;
    QElapsedTimer m_timer;
    unsigned m_counter;
};
