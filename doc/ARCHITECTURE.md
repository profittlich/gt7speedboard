# SpeedBoard architecture

The SpeedBoard consists of multiple parts:

![SpeedBoard architecture](images/architecture.png)

## UI

MainWidget is the center point of the UI, from which all other parts are launched. It contains a StackedLayout that contains the StartScreen, DashWidget and all Dialogs.

When the dash is started, the UI will create a new Dash, Controller and Receiver for the session.

## Receiver

The Receiver handles the network connection for receiving the telemetry data, fills in gaps and sends the packages to the Controller.

## Dash

The Dash manages the layout and contents of the dash board. It contains a number of Components, arranges them in a widget and handles im- and export of dash data.
It includes UI and non-UI components, defines keyboard shortcuts and parameter values.

Dashes are defined in layout files (*.sblayout). 

### Component

A Component handles one task within a Dash. It may, for example, display the current speed, show tyre temperatures or act in the background, like detect the current progress in a lap for other Components to use.

Components have public access to the State.

#### Widget

A Component may or may not have a widget. If it has a widget, it will be added to the Dash's DashWidget according to the layout defined in the layout file.

#### Parameters

A Component may have a number of parameters. ComponentParameters may be of the types

- Int
- Float
- String
- Boolean

Their values can be defined in the layout file. If the parameters are changed during operation, the updated values can be exported into a new layout file.

Changes to parameters can happen through actions, context menus or by the Component itself.

#### Actions

A Component may provide a number of actions to change its behavior during operation. Actions can be executed via keyboard shortcuts (as defined in the layout file), taps/clicks on the Component's widget or through a context menu (by long-pressing the widget).

### DashWidget

The DashWidget holds all the widgets of Components as defined in the layout file. It is held itself by the stacked layout of the MainWidget.

## Controller

The Controller receives telemetry data, does some general global processing and delivers the telemetry data to all Components in the current Dash. It decides which Component methods need to be called. For each telemetry packet, it will first serve non-UI Components and then UI Components.

It has private access to the State.

### State

The State contains all persistent information about the current session. This includes values that may be important to multiple Components or the Controller, like:

- The current progress in the lap
- Information about fuel consumption
- CPU load/processing time data

The State is owned by the Controller and created and destroyed with it.

#### Telemetry storage

The State stores all telemetry data that was received during the session. The data is structured in Laps.

#### Comparison laps

Some laps are referenced as ComparisonLaps. For example

- The lap with the fastest lap time
- The previous lap
- The lap with the median lap time
- A synthetic lap with optimizes brake points
- Laps loaded from files (previously exported comparison laps/telemetry data)

Components can use the comparison laps to provide information to the driver, for example about brake points or current lap time gains/losses.

Comparison laps can be exported for later use or sharing with other drivers.