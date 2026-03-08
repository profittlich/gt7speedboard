#include "MainWidget.h"

#include "sb/system/Helpers.h"

#include <QApplication>
#include <QLocale>
#include <QTranslator>

int main(int argc, char *argv[])
{
    qInstallMessageHandler(sbDebugMessageHandler);

    QApplication a(argc, argv);
    a.setOrganizationName("pitstop.profittlich.com");
    a.setOrganizationDomain("pitstop.profittlich.com");
    a.setApplicationName("GT7 SpeedBoard");

    QDir storeLoc = getStorageLocation();
    QFile outFile (storeLoc.absolutePath() + "/Last Debug.txt");
    if (outFile.open(QIODevice::WriteOnly))
    {
        outFile.write("New log file\n");
        outFile.close();
    }

    DBG_MSG << "Application starting";
    DBG_MSG << qVersion();

    QPalette pal = a.palette();
    pal.setColor(QPalette::Window, "#222");
    a.setPalette(pal);

    QTranslator translator;
    const QStringList uiLanguages = QLocale::system().uiLanguages();
    for (const QString &locale : uiLanguages) {
        const QString baseName = "SpeedBoard_for_GT7_Next_" + QLocale(locale).name();
        if (translator.load(":/i18n/" + baseName)) {
            a.installTranslator(&translator);
            break;
        }
    }
    DBG_MSG << "Start up UI";
    g_globalConfiguration.init();
    MainWidget w;
    w.show();
    return a.exec();
}
