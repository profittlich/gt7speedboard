QT       += core gui network opengl openglwidgets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

anroid {
QT += androidextras core-private
}


CONFIG += c++17

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    MainWidget.cpp \
    main.cpp \
    sb/cardata/TelemetryPoint.cpp \
    sb/cardata/TelemetryPointGT7.cpp \
    sb/components/Brake.cpp \
    sb/components/CPULoad.cpp \
    sb/components/CarName.cpp \
    sb/components/ComparisonLapManager.cpp \
    sb/components/ComparisonLapView.cpp \
    sb/components/ComponentFactory.cpp \
    sb/components/Empty.cpp \
    sb/components/FPS.cpp \
    sb/components/FuelAnalyzer.cpp \
    sb/components/FuelLevel.cpp \
    sb/components/FuelPerLap.cpp \
    sb/components/FuelRange.cpp \
    sb/components/Gear.cpp \
    sb/components/LapChangeDetector.cpp \
    sb/components/LapComparison.cpp \
    sb/components/LapDisplay.cpp \
    sb/components/LapTimes.cpp \
    sb/components/Map.cpp \
    sb/components/Message.cpp \
    sb/components/PresetSelector.cpp \
    sb/components/RPM.cpp \
    sb/components/SessionChangeDetector.cpp \
    sb/components/Speed.cpp \
    sb/components/Throttle.cpp \
    sb/components/TyreTemps.cpp \
    sb/receiver/GT7TelemetryReceiver.cpp \
    sb/system/Configuration.cpp \
    sb/system/Controller.cpp \
    sb/system/DashBuilder.cpp \
    sb/system/DashTree.cpp \
    sb/system/Helpers.cpp \
    sb/system/KeyStrings.cpp \
    sb/system/Laps.cpp \
    sb/system/RawRecorder.cpp \
    sb/system/State.cpp \
    sb/widgets/ButtonLabel.cpp \
    sb/widgets/ColorLabel.cpp \
    sb/widgets/ComponentMenuScrreen.cpp \
    sb/widgets/DashWidget.cpp \
    sb/widgets/ErrorScreen.cpp \
    sb/widgets/GaugeLabel.cpp \
    sb/widgets/ImageLabel.cpp \
    sb/widgets/MainMenuScreen.cpp \
    sb/widgets/MenuScreen.cpp \
    sb/widgets/SideButtonLabel.cpp \
    sb/widgets/StartScreen.cpp

HEADERS += \
    MainWidget.h \
    contrib/Salsa20-master/Source/Salsa20.h \
    contrib/Salsa20-master/Source/Salsa20.inl \
    sb/cardata/Point.h \
    sb/cardata/TelemetryPoint.h \
    sb/cardata/TelemetryPointGT7.h \
    sb/cardata/Vector3D.h \
    sb/cardata/WheelData.h \
    sb/components/Brake.h \
    sb/components/CPULoad.h \
    sb/components/CarName.h \
    sb/components/ComparisonLapManager.h \
    sb/components/ComparisonLapView.h \
    sb/components/Component.h \
    sb/components/ComponentFactory.h \
    sb/components/Empty.h \
    sb/components/FPS.h \
    sb/components/FuelAnalyzer.h \
    sb/components/FuelLevel.h \
    sb/components/FuelPerLap.h \
    sb/components/FuelRange.h \
    sb/components/Gear.h \
    sb/components/LapChangeDetector.h \
    sb/components/LapComparison.h \
    sb/components/LapDisplay.h \
    sb/components/LapTimes.h \
    sb/components/Map.h \
    sb/components/Message.h \
    sb/components/PresetSelector.h \
    sb/components/RPM.h \
    sb/components/SessionChangeDetector.h \
    sb/components/Speed.h \
    sb/components/Throttle.h \
    sb/components/TyreTemps.h \
    sb/receiver/GT7TelemetryReceiver.h \
    sb/receiver/TelemetryReceiver.h \
    sb/system/Action.h \
    sb/system/CarDatabase.h \
    sb/system/Configuration.h \
    sb/system/Controller.h \
    sb/system/Dash.h \
    sb/system/DashBuilder.h \
    sb/system/DashTree.h \
    sb/system/Helpers.h \
    sb/system/KeyStrings.h \
    sb/system/Laps.h \
    sb/system/RawRecorder.h \
    sb/system/State.h \
    sb/trackdata/Track.h \
    sb/trackdata/TrackDetector.h \
    sb/widgets/ButtonLabel.h \
    sb/widgets/ColorLabel.h \
    sb/widgets/ComponentMenuScreen.h \
    sb/widgets/ComponentWidget.h \
    sb/widgets/DashWidget.h \
    sb/widgets/DialogWidget.h \
    sb/widgets/ErrorScreen.h \
    sb/widgets/GaugeLabel.h \
    sb/widgets/ImageLabel.hpp \
    sb/widgets/InteractiveWidget.h \
    sb/widgets/MainMenuScreen.h \
    sb/widgets/MenuScreen.h \
    sb/widgets/SideButtonLabel.h \
    sb/widgets/StartScreen.h

TRANSLATIONS += \
    SpeedBoard_for_GT7_Next_de_DE.ts
CONFIG += lrelease
CONFIG += embed_translations

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

ios {
    QMAKE_INFO_PLIST = platform/ios/Info.plist
    app_launch_screen.files = $$PWD/platform/ios/SBLaunchScreen.storyboard $$files($$PWD/platform/ios/LoadingScreenLogo.png)
    QMAKE_BUNDLE_DATA += app_launch_screen
}

DISTFILES += \
    android/AndroidManifest.xml \
    android/build.gradle \
    android/res/values/libs.xml \
    android/res/xml/qtprovider_paths.xml \
    assets/3_Columns.sblayout \
    assets/SpeedBoard_Logo_black.png \
    assets/SpeedBoard_Logo_black_trans.png \
    assets/SpeedBoard_Logo_trans.png \
    assets/SpeedBoard_Logo_white.png \
    platform/ios/LoadingScreenLogo.png \
    platform/ios/SBLaunchScreen.storyboard \
    platform/ios/Info.plist

RESOURCES += \
    speedboard.qrc

contains(ANDROID_TARGET_ARCH,arm64-v8a) {
    ANDROID_PACKAGE_SOURCE_DIR = \
        $$PWD/android
}
