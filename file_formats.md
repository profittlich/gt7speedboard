# File formats for GT7 telemetry and configuration

## Telemetry

All telemetry file formats consist of sequences of telemetry packages. One package is 296 bytes long and is stored exactly as it arrived from the PlayStation (i.e. encrypted). The differences between the formats lie in the assumptions about the content of the packages.

### .gt7 files

Raw telemetry streams as they arrive from the PlayStation. They can start and stop at any point in the stream and will also include paused or out-of-race packages.

### .gt7lap files

Telemetry data for exactly one lap. The first package is the last data point from the previous lap and the last package is the first data point from the following lap. This can be useful, because the finish line is crossed between the last and first telemetry points of two consecutive laps. The 'following' data point is especially useful, because it contains the official lap time of the stored lap. 'Preceeding' and 'following' packages can be identified by their current_lap entry. When working with multiple laps, be careful not to create duplicate packages by not considering 'preceeding' and 'following' entries correctly. Paused and out-of-race packages are not present in .gt7lap files. 

### .gt7laps files

Like .gt7lap files, but containing multiple laps. There are no duplicate packages in .gt7laps files. Extra 'preceeding' and 'following' packages (see above) exist only at the very start and end of the file.

### .gt7track files

Like .gt7lap files, but with fewer packages. Only packages that are significant to the shape of the racing line or track are stored. Two consecutive packages do not necessarily have consecutive package_ids (are rarely will). However, two consecutive packages are never further than 50m apart.

## Configuration

TBD
