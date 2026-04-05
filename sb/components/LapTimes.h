#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

#include <QScrollArea>

class LapTimes : public Component
{
public:
    LapTimes (const QJsonValue config);

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:
    void setupScroller(QScrollArea *area);


private:
    QScrollArea * m_scroller;
    QLabel * m_widget;
};
