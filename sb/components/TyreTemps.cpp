#include "sb/components/TyreTemps.h"

#include "sb/components/ComponentFactory.h"

#include<QGridLayout>
#include <QJsonObject>

TyreTemps::TyreTemps (const QJsonValue conf) : Component(conf), m_target(new ComponentParameter<float>("target", 70, true)), m_spread(new ComponentParameter<float>("spread", 20, true))
{
    addComponentParameter(m_target);
    addComponentParameter(m_spread);

    m_colorMapper = new ColorMapperBlueGreenRed((*m_target)(), (*m_spread)());

    m_widget = new QWidget();

    QGridLayout * layout = new QGridLayout(m_widget);
    layout->setContentsMargins(0,0,0,0);

    m_fl = new ColorLabel();
    m_fr = new ColorLabel();
    m_rl = new ColorLabel();
    m_rr = new ColorLabel();
    layout->addWidget(m_fl, 0, 0);
    layout->addWidget(m_fr, 0, 1);
    layout->addWidget(m_rl, 1, 0);
    layout->addWidget(m_rr, 1, 1);
    m_fl->installEventFilter(this);
    m_fr->installEventFilter(this);
    m_rl->installEventFilter(this);
    m_rr->installEventFilter(this);
    m_widget->installEventFilter(this);

    QFont font = m_fl->font();
    font.setPointSizeF(baseFontSize() * 8);

    m_fl->setAlignment(Qt::AlignCenter);
    m_fl->setFont(font);
    m_fl->setStyleSheet("color : #fff;");
    m_fl->setText("FL");

    m_fr->setAlignment(Qt::AlignCenter);
    m_fr->setFont(font);
    m_fr->setStyleSheet("color : #fff;");
    m_fr->setText("FR");

    m_rl->setAlignment(Qt::AlignCenter);
    m_rl->setFont(font);
    m_rl->setStyleSheet("color : #fff;");
    m_rl->setText("RL");

    m_rr->setAlignment(Qt::AlignCenter);
    m_rr->setFont(font);
    m_rr->setStyleSheet("color : #fff;");
    m_rr->setText("RR");
}

bool TyreTemps::eventFilter(QObject *obj, QEvent *event)
{
    if (event->type() == QEvent::MouseButtonPress || event->type() == QEvent::MouseButtonDblClick)
    {
        QMouseEvent * me = dynamic_cast<QMouseEvent*>(event);
        QWidget * w = dynamic_cast<QWidget*> (obj);

        int y = me->pos().y();

        if (obj != m_widget)
        {
            y += w->pos().y();
        }

        if (y < m_widget->height() / 2)
        {
            callAction("targetUp");
        }
        else
        {
            callAction("targetDown");
        }

        qDebug("Event filter: MouseButtonPress " + QString::number(y).toLatin1());
    }
    if (event->type() == QEvent::MouseButtonRelease)
    {
        qDebug("Event filter: MouseButtonRelease");
    }

    return QObject::eventFilter(obj, event);
}

QWidget * TyreTemps::getWidget() const
{
    return m_widget;
}

QString TyreTemps::defaultTitle () const
{
    return "Tyres";
}

void TyreTemps::newPoint(PTelemetryPoint p)
{
    const float fl = p->tyreTemperature().fl();
    const float fr = p->tyreTemperature().fr();
    const float rl = p->tyreTemperature().rl();
    const float rr = p->tyreTemperature().rr();

    m_fl->setText (QString::number(round(fl)) + " °C");
    m_fr->setText (QString::number(round(fr)) + " °C");
    m_rl->setText (QString::number(round(rl)) + " °C");
    m_rr->setText (QString::number(round(rr)) + " °C");

    m_fl->setColor(m_colorMapper->getColor(fl));
    m_fr->setColor(m_colorMapper->getColor(fr));
    m_rl->setColor(m_colorMapper->getColor(rl));
    m_rr->setColor(m_colorMapper->getColor(rr));

    emit setTitleSuffix("[" + QString::number((*m_target)()) + " °C]");
}


QString TyreTemps::description ()
{
    return "Color-coded tyre temperatures";
}

QList<QString> TyreTemps::actions ()
{
    QList<QString> result;

    result.append("targetUp");
    result.append("targetDown");

    return result;
}

QString TyreTemps::componentId ()
{
    return "TyreTemps";
}


void TyreTemps::callAction(QString a)
{
    if (a == "targetUp")
    {
        if ((*m_target)() < 150)
        {
            (*m_target)()++;
            m_colorMapper = new ColorMapperBlueGreenRed((*m_target)(), (*m_spread)());
            m_widget->update();
            emit setTitleSuffix("[" + QString::number((*m_target)()) + " °C]");
        }
    }
    else if (a == "targetDown")
    {
        if ((*m_target)() > 20)
        {
            (*m_target)()--;
            m_colorMapper = new ColorMapperBlueGreenRed((*m_target)(), (*m_spread)());
            m_widget->update();
            emit setTitleSuffix("[" + QString::number((*m_target)()) + " °C]");
        }
    }
}

void TyreTemps::presetSwitched()
{
    m_colorMapper = new ColorMapperBlueGreenRed((*m_target)(), (*m_spread)());
}


static ComponentFactory::RegisterComponent<TyreTemps> reg;
