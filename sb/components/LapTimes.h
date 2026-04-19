#pragma once

#include "sb/components/Component.h"
#include "sb/widgets/ColorLabel.h"

#include <QScrollArea>

class LapTimes : public Component
{
public:
    LapTimes ();

    virtual QWidget * getWidget() const override;

    virtual QString defaultTitle () const override;

    virtual void completedLap(PLap lastLap, bool isFullLap) override;

    virtual void callAction(QString a) override;

    static QString description ();
    static QMap<QString, Action> actions ();
    static QString componentId ();

protected:
    void setupScroller(QScrollArea *area);
    void exportCSV();


private:
    QScrollArea * m_scroller;
    QLabel * m_widget;
};
