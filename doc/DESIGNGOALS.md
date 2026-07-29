# Design goals of SpeedBoard

The SpeedBoard is primarily intended to be used while driving in the sim. Therefore, it needs to introduce as few obstacles as possible to the driver while concentrating on the road and operating the virtual vehicle. It is also supposed to run on different types of platforms, such as tablets, phones, laptops and desktop computers and needs to consider the UX approaches of these platforms.

## Glancability

The information on the dashboard must be taken in as quickly as possible, depening on the current situation:

- The car is standing for a long period:
  - The driver can make deep changes to the dashboard, like setting parameters or replacing individual components. 
  - No restrictions on UX, except to consider multi-platform support.
- The car is standing for a short time (like during a pit stop):
  - The driver can look at the dashboard for a couple of seconds.
  - Information should be quickly found and presented in a clear layout. Smaller fonts and lists of data are OK.
- The car is driving in a non-critical situation (like on a straight with no traffic):
  - The driver can only quickly glance at the dashboard.
  - Information must be immediately visible and understandable in less than a second.
  - Use strong color coding where applicable.
  - Use very short but large text.
  - Omit complicated graphics or metaphors (e.g. don't draw a drive train to show information about the tyres. Just display the relevant information).
- The car is driving in a critical situation (like approaching and driving through a corner or when the driver has to be notified of a problem like running low on fuel):
  - The driver cannot/does not look at the dashboard at all.
  - Information must be delivered to the peripheral vision of the driver.
  - Use large areas of strong colors to convey information.
  - Blinking frequency or timing can carry additional information.
  - Provide a way to turn off excessive blinking if the driver prefers not to be distracted at all.

## Shortcuts

Provide keyboard and touch/click shortcuts for the most important settings for use during driving. This depends on the component used. The goal should be to give the driver quick access to settings/adjustments without beint distracted from the track for too long.

## Touch and mouse interaction

Since some target platforms use primarily touch screens for interaction, always consider the limitations of such devices. Make touch targets/buttons large enough to be controlled with a finger. Omit user interactions that can only be comfortably executed with a mouse. This is also relevant for laptops and desktop computers, since mouse and touchpad interactions will also be less precise when the player is driving at the same time.