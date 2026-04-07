#include "sb/components/RPM.h"

#include "sb/components/ComponentFactory.h"



RPM::RPM () : Component()
{
    m_widget = new ColorLabel();

    m_widget->setAlignment(Qt::AlignCenter);
    QFont font = m_widget->font();
    font.setPointSizeF(baseFontSize() * 15);
    m_widget->setFont(font);
    m_widget->setStyleSheet("color : #fff;");

    m_widget->setText("0 RPM");
}

QWidget * RPM::getWidget() const
{
    return m_widget;
}

QString RPM::defaultTitle () const
{
    return "RPM";
}

void RPM::newPoint(PTelemetryPoint p)
{
    m_widget->setText (QString::number(100*round(p->rpm()/100)) + " RPM");
}


QString RPM::description ()
{
    return "Simple RPM meter";
}

QMap<QString, Action> RPM::actions ()
{
    return QMap<QString, Action>();
}

QString RPM::componentId ()
{
    return "RPM";
}


static ComponentFactory::RegisterComponent<RPM> reg;
