#include "src/components/DebugLog.h"

#include "src/components/ComponentFactory.h"
#include "src/system/Configuration.h"
#include <QtWidgets/qscroller.h>

DebugLog::DebugLog () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize()*3);
    m_widget->setAlignment(Qt::AlignLeft);
    m_widget->setFont(font);
    m_widget->setText(g_debugText);
    m_widget->setStyleSheet("color : white;");

    m_scroller = new QScrollArea();
    m_scroller->setWidgetResizable(true);
    m_scroller->setWidget(m_widget);

    setupScroller(m_scroller);
    m_scroller->ensureVisible(0, m_widget->height());
}

void DebugLog::setupScroller(QScrollArea *area)
{
    QScroller::grabGesture(area->viewport(), QScroller::LeftMouseButtonGesture);
    QVariant OvershootPolicy = QVariant::fromValue<QScrollerProperties::OvershootPolicy>(QScrollerProperties::OvershootAlwaysOff);
    QScrollerProperties ScrollerProperties = QScroller::scroller(area->viewport())->scrollerProperties();
    ScrollerProperties.setScrollMetric(QScrollerProperties::VerticalOvershootPolicy, OvershootPolicy);
    ScrollerProperties.setScrollMetric(QScrollerProperties::HorizontalOvershootPolicy, OvershootPolicy);
    QScroller::scroller(area->viewport())->setScrollerProperties(ScrollerProperties);
}

void DebugLog::newPoint(PTelemetryPoint p)
{
    m_widget->setText(g_debugText);
    m_scroller->ensureVisible(0, m_widget->height());
}

QWidget * DebugLog::getWidget() const
{
    return m_scroller;
}

QString DebugLog::defaultTitle () const
{
    return "Debug";
}

QString DebugLog::description ()
{
    return "Show debugging output";
}

QString DebugLog::componentId ()
{
    return "DebugLog";
}

QMap<QString, Action> DebugLog::actions ()
{
    return QMap<QString, Action>();
}

static ComponentFactory::RegisterComponent<DebugLog> reg(true);
