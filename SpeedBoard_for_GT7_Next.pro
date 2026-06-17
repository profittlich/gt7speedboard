QT       += core gui network opengl openglwidgets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

anroid {
QT += androidextras core-private
QT_ANDROID_APP_ICON = @mipmap/ic_launcher
}


CONFIG += c++17

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    MainWidget.cpp \
    main.cpp \
    src/cardata/TelemetryPoint.cpp \
    src/cardata/TelemetryPointGT7.cpp \
    src/components/Brake.cpp \
    src/components/CPULoad.cpp \
    src/components/CarName.cpp \
    src/components/ComparisonLapManager.cpp \
    src/components/ComparisonLapView.cpp \
    src/components/ComponentFactory.cpp \
    src/components/Empty.cpp \
    src/components/FPS.cpp \
    src/components/FuelAnalyzer.cpp \
    src/components/FuelLevel.cpp \
    src/components/FuelPerLap.cpp \
    src/components/FuelRange.cpp \
    src/components/Gear.cpp \
    src/components/LapChangeDetector.cpp \
    src/components/LapComparison.cpp \
    src/components/LapDisplay.cpp \
    src/components/LapProgress.cpp \
    src/components/LapTimes.cpp \
    src/components/Map.cpp \
    src/components/MapRenderers/SBGLMapWidgetLines.cpp \
    src/components/MapRenderers/SBGLMapWidgetZoomedLines.cpp \
    src/components/Message.cpp \
    src/components/PedalGraph.cpp \
    src/components/PresetSelector.cpp \
    src/components/ProgressManager.cpp \
    src/components/RPM.cpp \
    src/components/RaceTime.cpp \
    src/components/SessionChangeDetector.cpp \
    src/components/Speed.cpp \
    src/components/Throttle.cpp \
    src/components/TrackDetectDebug.cpp \
    src/components/TrackName.cpp \
    src/components/TyreTemps.cpp \
    src/receiver/GT7TelemetryReceiver.cpp \
    src/system/Configuration.cpp \
    src/system/Controller.cpp \
    src/system/DashBuilder.cpp \
    src/system/DashTree.cpp \
    src/system/Helpers.cpp \
    src/system/KeyStrings.cpp \
    src/system/Laps.cpp \
    src/system/RawRecorder.cpp \
    src/system/State.cpp \
    src/trackdata/Track.cpp \
    src/trackdata/TrackDetector.cpp \
    src/widgets/ButtonLabel.cpp \
    src/widgets/ColorLabel.cpp \
    src/widgets/ComponentMenuScrreen.cpp \
    src/widgets/DashWidget.cpp \
    src/widgets/ErrorScreen.cpp \
    src/widgets/GaugeLabel.cpp \
    src/widgets/Graph.cpp \
    src/widgets/ImageLabel.cpp \
    src/widgets/LapMenuScreen.cpp \
    src/widgets/LapsMenuScreen.cpp \
    src/widgets/MainMenuScreen.cpp \
    src/widgets/MenuScreen.cpp \
    src/widgets/SideButtonLabel.cpp \
    src/widgets/StartScreen.cpp \
    src/widgets/TextInput.cpp

HEADERS += \
    MainWidget.h \
    contrib/Salsa20-master/Source/Salsa20.h \
    contrib/Salsa20-master/Source/Salsa20.inl \
    src/cardata/Point.h \
    src/cardata/TelemetryPoint.h \
    src/cardata/TelemetryPointGT7.h \
    src/cardata/Vector3D.h \
    src/cardata/WheelData.h \
    src/components/Brake.h \
    src/components/CPULoad.h \
    src/components/CarName.h \
    src/components/ComparisonLapManager.h \
    src/components/ComparisonLapView.h \
    src/components/Component.h \
    src/components/ComponentFactory.h \
    src/components/Empty.h \
    src/components/FPS.h \
    src/components/FuelAnalyzer.h \
    src/components/FuelLevel.h \
    src/components/FuelPerLap.h \
    src/components/FuelRange.h \
    src/components/Gear.h \
    src/components/LapChangeDetector.h \
    src/components/LapComparison.h \
    src/components/LapDisplay.h \
    src/components/LapProgress.h \
    src/components/LapTimes.h \
    src/components/Map.h \
    src/components/MapRenderers/SBGLMapWidget.h \
    src/components/MapRenderers/SBGLMapWidgetLines.h \
    src/components/MapRenderers/SBGLMapWidgetZoomedLines.h \
    src/components/Message.h \
    src/components/PedalGraph.h \
    src/components/PresetSelector.h \
    src/components/ProgressManager.h \
    src/components/RPM.h \
    src/components/RaceTime.h \
    src/components/SessionChangeDetector.h \
    src/components/Speed.h \
    src/components/Throttle.h \
    src/components/TrackDetectDebug.h \
    src/components/TrackName.h \
    src/components/TyreTemps.h \
    src/receiver/GT7TelemetryReceiver.h \
    src/receiver/TelemetryReceiver.h \
    src/system/Action.h \
    src/system/CarDatabase.h \
    src/system/Configuration.h \
    src/system/Controller.h \
    src/system/Dash.h \
    src/system/DashBuilder.h \
    src/system/DashTree.h \
    src/system/Helpers.h \
    src/system/KeyStrings.h \
    src/system/Laps.h \
    src/system/RawRecorder.h \
    src/system/State.h \
    src/trackdata/Track.h \
    src/trackdata/TrackDetector.h \
    src/widgets/ButtonLabel.h \
    src/widgets/ColorLabel.h \
    src/widgets/ComponentMenuScreen.h \
    src/widgets/ComponentWidget.h \
    src/widgets/DashWidget.h \
    src/widgets/DialogWidget.h \
    src/widgets/ErrorScreen.h \
    src/widgets/GaugeLabel.h \
    src/widgets/Graph.h \
    src/widgets/ImageLabel.hpp \
    src/widgets/InteractiveWidget.h \
    src/widgets/LapMenuScreen.h \
    src/widgets/LapsMenuScreen.h \
    src/widgets/MainMenuScreen.h \
    src/widgets/MenuScreen.h \
    src/widgets/SideButtonLabel.h \
    src/widgets/StartScreen.h \
    src/widgets/TextInput.h

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

    app_icon.files = $$PWD/platform/ios/IOS_Assests.xcassets
    QMAKE_BUNDLE_DATA += app_icon


    #QMAKE_ASSET_CATALOGS += $$PWD/platform/ios/IOS_Assests.xcassets
    QMAKE_ASSET_CATALOG_APP_ICON = AppIcon
}

windows {
    RC_ICONS = doc/SpeedBoard_Icon_512.ico
}

macx {
    QMAKE_APPLE_DEVICE_ARCHS = x86_64 arm64
    ICON = doc/SpeedBoard_Icon.icns
    QMAKE_MACOSX_DEPLOYMENT_TARGET = 12.0
    MACOSX_DEPLOYMENT_TARGET=12.0
}
#QMAKE_APPLE_DEVICE_ARCHS = arm64

DISTFILES += \
    android/AndroidManifest.xml \
    android/build.gradle \
    android/res/values/libs.xml \
    android/res/xml/qtprovider_paths.xml \
    assets/Default.sblayout \
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
