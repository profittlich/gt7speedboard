#include "src/components/TrackName.h"

#include "src/cardata/TelemetryPointGT7.h"
#include "src/components/ComponentFactory.h"
#include "src/system/Configuration.h"



TrackName::TrackName () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 3);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setWordWrap(true);
}

QWidget * TrackName::getWidget() const
{
    return m_widget;
}

QString TrackName::defaultTitle () const
{
    return "Track";
}

void TrackName::newPoint(PTelemetryPoint p)
{
    QString trc = state()->currentLap->trackName(true);
    if (!trc.isNull())
    {
        m_widget->setText (trc);
    }
    else
    {
        m_widget->setText ("unknown track");
    }
}


QString TrackName::description ()
{
    return "Show the name of the current track";
}

QMap<QString, Action> TrackName::actions ()
{
    return QMap<QString, Action>();
}

QString TrackName::componentId ()
{
    return "TrackName";
}


static ComponentFactory::RegisterComponent<TrackName> reg(true);
