#include "sb/system/Helpers.h"
#include <QString>
#include <QColor>
#include <QStandardPaths>

#ifdef Q_OS_WINDOWS
#include <windows.h>
#endif

#ifdef Q_OS_ANDROID
#include <QGuiApplication>
#include <QJniObject>
#endif

#ifdef Q_OS_APPLE
#include <IOKit/pwr_mgt/IOPMLib.h>
CFStringRef g_reasonForActivity= CFSTR("User Activity Type");
IOPMAssertionID g_assertionID;
#endif


void sbDebugMessageHandler(QtMsgType type, const QMessageLogContext & context, const QString & txt)
{
    std::cout << txt.toStdString() << std::endl;

    QDir storeLoc = getStorageLocation();
    QFile outFile (storeLoc.absolutePath() + "/Last Debug.txt");
    if (outFile.open(QIODevice::Append))
    {
        QTextStream stream( &outFile );
        stream << txt << "\n";
        outFile.close();
    }
}

QString indexToTime(size_t idx)
{
    size_t ms = (idx + 0.5) * c_FPS;
    return msToTime(ms);
}

QString msToTime(unsigned ms)
{
    if (ms < 0)
    {
        return "no time";
    }

    int tm = int((ms/1000) / 60);
    int ts = int((ms/1000) % 60);
    int tms = ms % 1000;

    QString tts = QString::number(ts);
    if (tts.size() < 2)
    {
        tts = "0" + tts;
    }
    QString ttms = QString::number(tms);
    while (ttms.size() < 3)
    {
        ttms = "0" + ttms;
    }

    return QString::number(tm) + ":" + tts + "." + ttms;
}

QString sToTime(unsigned s)
{
    if (s < 0)
    {
        return "no time";
    }

    int tm = int(s / 60);
    int ts = int(s % 60);

    QString tts = QString::number(ts);
    if (tts.size() < 2)
    {
        tts = "0" + tts;
    }

    return QString::number(tm) + ":" + tts;
}

QDir getStorageLocation()
{
#ifdef Q_OS_IOS
    QDir storeLoc (QStandardPaths::standardLocations(QStandardPaths::StandardLocation::DocumentsLocation)[0] + "/Documents");
#elif defined(Q_OS_ANDROID)
    QDir storeLoc (QStandardPaths::standardLocations(QStandardPaths::StandardLocation::DocumentsLocation)[0]);
#else
    QDir storeLoc (QStandardPaths::standardLocations(QStandardPaths::StandardLocation::AppDataLocation)[0]);
#endif

    if(!storeLoc.exists())
    {
        storeLoc.mkpath(storeLoc.absolutePath());
    }

    return storeLoc;
}

void setKeepScreenOn(bool enable)
{
#ifdef Q_OS_ANDROID
    QNativeInterface::QAndroidApplication::runOnAndroidMainThread([=]() {
        QJniObject activity = QNativeInterface::QAndroidApplication::context();
        if (activity.isValid()) {
            QJniObject window = activity.callObjectMethod("getWindow", "()Landroid/view/Window;");
            if (window.isValid()) {
                const int FLAG_KEEP_SCREEN_ON = 128; // 0x00000080
                if (enable) {
                    window.callMethod<void>("addFlags", "(I)V", FLAG_KEEP_SCREEN_ON);
                } else {
                    window.callMethod<void>("clearFlags", "(I)V", FLAG_KEEP_SCREEN_ON);
                }
            }
        }
    });
#endif

#ifdef Q_OS_APPLE
    int success;
    bool active;
    if (enable)
    {
        //success = IOPMAssertionDeclareUserActivity(g_reasonForActivity, kIOPMUserActiveLocal, &g_assertionID);
        success = IOPMAssertionCreateWithName(kIOPMAssertionTypeNoDisplaySleep, kIOPMAssertionLevelOn, g_reasonForActivity, &g_assertionID);
        active =(success == kIOReturnSuccess);
    } else {
        success = IOPMAssertionRelease(g_assertionID);
        active = !(success == kIOReturnSuccess);
    }
    DBG_MSG << "Awake mode: " << (enable ? "enable" : "disable") << " " << success << " " << (active ? "active" : "inactive");
#endif

#ifdef Q_OS_WINDOWS
    int result;
    if (enable)
    {
        result = SetThreadExecutionState(ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED | ES_CONTINUOUS);
    } else {
        result = SetThreadExecutionState(ES_CONTINUOUS);
    }
    DBG_MSG << "Awake mode: " << result;
#endif
}
