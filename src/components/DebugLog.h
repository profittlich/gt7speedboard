#pragma once

#include "src/components/Component.h"
#include "src/widgets/ColorLabel.h"
#include <QtCore/qdatetime.h>
#include <QtWidgets/qscrollarea.h>

class DebugLog : public Component
{
public:
    DebugLog ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void newPoint(PTelemetryPoint p) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:
    void setupScroller(QScrollArea *area);

private:
    QScrollArea * m_scroller = nullptr;
    ColorLabel * m_widget = nullptr;
};
