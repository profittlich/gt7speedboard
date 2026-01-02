#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"
#include <QScrollArea>

class ComparisonLapView : public Component
{
public:
    ComparisonLapView (const QJsonValue config);

    virtual QWidget * getWidget() const override;
    virtual QString defaultTitle () const override;
    virtual void newPoint(PTelemetryPoint p) override;
    virtual void completedLap(PLap lastLap, bool isFullLap) override;
    virtual void newSession() override;

    virtual void pitStop() override;

    virtual void newTrack(PTrack track) override;
    virtual void maybeNewTrack(PTrack track) override;
    virtual void leftTrack() override;

    static QString description ();
    static QList<QString> actions ();
    static QString componentId ();

private:
    ColorLabel * m_widget;
    QScrollArea * m_scrollWidget;
};
