#include "MainWidget.h"

#include <QLabel>
#include <QFile>
#include <QJsonDocument>
#include <QStandardPaths>
#include <QDir>
#include <QFileDialog>
#include "sb/widgets/ErrorScreen.h"
#include "sb/widgets/MenuScreen.h"
#include "sb/widgets/StartScreen.h"
#include "sb/receiver/GT7TelemetryReceiver.h"
#include "sb/system/DashBuilder.h"
#include "sb/system/Configuration.h"
#include "sb/system/KeyStrings.h"
#include "sb/widgets/DashWidget.h"

MainWidget::MainWidget(QWidget *parent)
    : QWidget(parent), m_inDash(false)
{
    DBG_MSG << "Construct MainWidget";
    m_widget = nullptr;

    this->setWindowTitle("SpeedBoard for GT7");
    m_layout = new QStackedLayout(this);
    setLayout(m_layout);
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + ";");
    showStartScreen();
    auto x = initQtKeys();
}

MainWidget::~MainWidget()
{
    if (!m_dash.isNull())
    {
        QDir storeLoc = getStorageLocation();
        QFile outFile (storeLoc.absolutePath() + "/Last Used.sblayout");
        DBG_MSG << "Out file: " << outFile.fileName();
        if (outFile.open(QIODevice::WriteOnly))
        {
            QTextStream stream( &outFile );
            stream << m_dash->toJson().toJson();
            outFile.close();
        }
    }
}

void MainWidget::showStartScreen()
{
    setKeepScreenOn(false);
    if (m_widget != nullptr)
    {
        m_receiver.clear();
        m_controller.clear();
        if (m_debugRecorder.get())
        {
            m_debugRecorder->stop();
            m_debugRecorder.clear();
        }
        m_widget->deleteLater();

        QDir storeLoc = getStorageLocation();
        QFile outFile (storeLoc.absolutePath() + "/Last Used.sblayout");
        DBG_MSG << "Out file: " << outFile.fileName();
        if (outFile.open(QIODevice::WriteOnly))
        {
            QTextStream stream( &outFile );
            stream << m_dash->toJson().toJson();
            outFile.close();
        }
    }

    m_widget = new StartScreen(this);
    //m_layout->setContentsMargins(0,0,0,0);

    m_layout->addWidget(m_widget);

    m_inDash = false;

    connect(dynamic_cast<StartScreen*> (m_widget), &StartScreen::startDash, this, &MainWidget::startDash);
    setStyleSheet("background-color: " + g_globalConfiguration.dimColor().name() + "; color:white;");
}

void MainWidget::startDash ()
{
    setKeepScreenOn(true);
    QByteArray jsonData;

    QFile f(g_globalConfiguration.selectedLayout());
    DBG_MSG << "Selected layout: " << f.fileName();
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

#ifdef QT_DEBUG
    QDir storeLoc = getStorageLocation();

    m_debugRecorder = PRawRecorder (new RawRecorder(storeLoc.absolutePath() + "/Last Recording.gt7"));
    connect(m_receiver.get(), &TelemetryReceiver::newTelemetryPoint, m_debugRecorder.get(), &RawRecorder::newTelemetryPoint);
    m_debugRecorder->start();
#endif

    PDashBuilder dashbuilder = PDashBuilder(new DashBuilder());
    m_dash = dashbuilder->makeDash(this, jDoc);

    if (m_dash == nullptr)
    {
        qInfo("No valid dash");
        ErrorScreen * err = new ErrorScreen (this, "Layout is broken", nullptr);
        m_layout->insertWidget(0,err);
        m_layout->setCurrentIndex(0);
        return;
    }

    if (m_widget != nullptr)
    {
        m_widget->deleteLater();
    }
    if (m_widget != nullptr)
    {
        m_layout->removeWidget(m_widget);
    }

    m_widget = m_dash->widget;
    m_controller->setDash(m_dash);

    DBG_MSG << "load reference laps";
    m_controller->state()->loadComparisonLap("ref-a", getStorageLocation().absolutePath() + "/ref-a.gt7lap", true);
    DBG_MSG << "step";
    m_controller->state()->loadComparisonLap("ref-b", getStorageLocation().absolutePath() + "/ref-b.gt7lap", true);
    DBG_MSG << "step";
    m_controller->state()->loadComparisonLap("ref-c", getStorageLocation().absolutePath() + "/ref-c.gt7lap", true);
    DBG_MSG << "loaded reference laps";

    connect(m_dash->widget, &DashWidget::exitDash, this, &MainWidget::showStartScreen);
    connect(m_dash->widget, &DashWidget::showMenu, this, &MainWidget::showMenuScreen);
    connect(m_receiver.get(), &TelemetryReceiver::newTelemetryPoint, m_controller.get(), &Controller::newTelemetryPoint);

    m_receiver->start();
    m_layout->addWidget(m_widget);
    m_layout->setContentsMargins(0,0,0,0);
    setStyleSheet("");//background-color: " + g_globalConfiguration.dimColor().name() + ";");

    for (auto i : m_dash->components)
    {
        i->setState (m_controller->state());
        i->loaded();
    }

    m_widget->update();

    m_inDash = true;
}

void MainWidget::showMenuScreen ()
{
    MenuScreen * men = new MenuScreen (this, m_dash, m_controller->state());
    m_layout->insertWidget(0,men);
    m_layout->setCurrentIndex(0);
    //m_dash->widget->exitDash();
}

void MainWidget::keyPressEvent(QKeyEvent *event)
{
    if (m_inDash)
    {
        if (event->key() == Qt::Key_Escape || event->key() == Qt::Key_Back)
        {
            m_dash->widget->exitDash();
        }
        else if (event->key() == Qt::Key_C)
        {
            startDash();
        }
        else if (event->key() == Qt::Key_Right)
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

void MainWidget::resizeEvent(QResizeEvent * ev)
{
    //DBG_MSG << ev->oldSize().width() << "x" << ev->oldSize().height() << " -> " << ev->size().width() << "x" << ev->size().height();
    //DBG_MSG << this->contentsMargins().top();
    this->setContentsMargins(0,0,0,0);
    //DBG_MSG << this->contentsMargins().top();
}
