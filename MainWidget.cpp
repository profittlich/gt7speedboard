#include "MainWidget.h"

#include <QLabel>
#include <QFile>
#include <QJsonDocument>
#include <QStandardPaths>
#include <QDir>
#include <QFileDialog>
#include "sb/widgets/StartScreen.h"
#include "sb/receiver/GT7TelemetryReceiver.h"
#include "sb/system/DashBuilder.h"
#include "sb/system/Configuration.h"
#include "sb/system/KeyStrings.h"


MainWidget::MainWidget(QWidget *parent)
    : QWidget(parent), m_inDash(false)
{
    qDebug("Construct MainWidget");
    m_widget = nullptr;
    setStyleSheet("QLabel { background-color: " + g_globalConfiguration.dimColor().name() + "; color : white; }");

    this->setWindowTitle("SpeedBoard for GT7");
    m_layout = new QVBoxLayout(this);
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");
    showStartScreen();
    auto x = initQtKeys();
}

MainWidget::~MainWidget() {}

void MainWidget::showStartScreen()
{
    if (m_widget != nullptr)
    {
        m_receiver.clear();
        m_controller.clear();
        m_widget->deleteLater();

#ifdef Q_OS_IOS
        QDir storeLoc (QStandardPaths::standardLocations(QStandardPaths::StandardLocation::DocumentsLocation)[0] + "/Documents");
#else
        QDir storeLoc (QStandardPaths::standardLocations(QStandardPaths::StandardLocation::AppDataLocation)[0]);
#endif
        if(!storeLoc.exists())
        {
            qDebug("Create data path");
            storeLoc.mkpath(storeLoc.absolutePath());
        }
        QFile outFile (storeLoc.absolutePath() + "/Last Used.sblayout");
        qDebug() << "Out file: " << outFile.fileName();
        if (outFile.open(QIODevice::WriteOnly))
        {
            QTextStream stream( &outFile );
            stream << m_dash->toJson().toJson();
            outFile.close();
        }
    }
    m_widget = new StartScreen(this);
    m_layout->addWidget(m_widget);
    m_inDash = false;

    connect(dynamic_cast<StartScreen*> (m_widget), &StartScreen::startDash, this, &MainWidget::startDash);
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");
}

void MainWidget::startDash ()
{
    QByteArray jsonData;

    QFile f(g_globalConfiguration.selectedLayout());
    qDebug() << "Selected layout: " << f.fileName();
    if (!f.exists())
    {
        QFile f (":/assets/assets/Default.sblayout");
        f.open(QIODeviceBase::ReadOnly);
        jsonData = f.readAll();
        f.close();
    }
    else
    {
        f.open(QIODeviceBase::ReadOnly);
        jsonData = f.readAll();
        f.close();
    }

    QJsonDocument jDoc = QJsonDocument::fromJson(jsonData);

    m_receiver = QSharedPointer<TelemetryReceiver> (new GT7TelemetryReceiver());
    m_controller = QSharedPointer<Controller> (new Controller());

    PDashBuilder dashbuilder = PDashBuilder(new DashBuilder());
    m_dash = dashbuilder->makeDash(this, jDoc);

    if (m_dash == nullptr)
    {
        qInfo("No valid dash");
        return;
    }

    if (m_widget != nullptr)
    {
        m_widget->deleteLater();
    }
    m_widget = m_dash->widget;
    m_controller->setDash(m_dash);

    for (auto i : m_dash->components)
    {
        i->setState (m_controller->state());
    }

    connect(m_dash->widget, &DashWidget::exitDash, this, &MainWidget::showStartScreen);
    connect(m_receiver.get(), &TelemetryReceiver::newTelemetryPoint, m_controller.get(), &Controller::newTelemetryPoint);
    m_receiver->start();
    m_layout->addWidget(m_widget);
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");
    m_inDash = true;
}

void MainWidget::keyPressEvent(QKeyEvent *event)
{
    if (m_inDash)
    {
        if (event->key() == Qt::Key_Right)
        {
            size_t newIdx = m_controller->dash()->widget->currentIndex();
            size_t idxCount = m_controller->dash()->widget->count();
            newIdx++;
            if (newIdx >= idxCount)
            {
                newIdx = 1;
            }
            m_controller->dash()->widget->setCurrentIndex(newIdx);

        }
        else if (event->key() == Qt::Key_Left)
        {
            size_t newIdx = m_controller->dash()->widget->currentIndex();
            size_t idxCount = m_controller->dash()->widget->count();
            newIdx--;
            if (newIdx <= 0)
            {
                newIdx = idxCount-1;
            }
            m_controller->dash()->widget->setCurrentIndex(newIdx);
        }
        else if (m_dash->pageShortcuts.contains(event->key()))
        {
            m_controller->dash()->widget->setCurrentIndex(m_dash->pageShortcuts[event->key()]+1);
        }
        else if (m_dash->actions.contains(event->key()))
        {
            auto act = m_dash->actions[event->key()];
            act.first->callAction(act.second);
        }
    }
    else
    {
        QWidget::keyPressEvent(event);
    }
}
