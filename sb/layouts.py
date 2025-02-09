
defaultLayout = [
                    [ # Screen 1
                        [ # Page 1
                            {
                                "component": "SaveLaps",
                                "actions": { 
                                    "Key_B":"saveBest",
                                    "Key_M":"saveMedian",
                                    "Key_L":"saveLast",
                                    "Key_O":"saveOptimized",
                                    "Key_A":"saveAll",
                                }
                            },
                            {
                                "component": "RecordingController",
                                "actions": { 
                                    "Key_R":"toggleRecording",
                                }
                            },
                            { "component" : "LapHeader", "stretch" : 1},
                            { "list" :
                                [
                                    { "list" :
                                        [
                                            { "component" : "Speed", "stretch" : 2, "actions" : { "Key_Tab" : "cycleFocusReference", "Key_Up" : "brakeOffsetUp", "Key_Down" : "brakeOffsetDown", "Key_0" : "resetBrakeOffset", }},
                                            { "component" : "TyreTemps", "stretch" : 1},
                                        ], "stretch" : 1
                                    },
                                    { "component" : "FuelAndMessages", "stretch" : 1, "actions" : { "Key_Space" : "setCautionMarker", "Key_W" : "saveMessages" }},
                                ], "stretch" : 100
                            }
                        ],
                        # Pages 2..
                        { "component" : "Stats", "stretch" : 1, "shortcut":"Key_S", "actions" : { "Key_T" : "saveRuns", "Key_D" : "setRunDescription" }},
                        { "component" : "Help", "title":"Keyboard shortcuts", "shortcut":"Key_Question", "stretch" : 1},
                        { "component" : "Map", "shortcut":"Key_V", "stretch" : 1},
                    ],
                ]

multiScreenLayout = [
                    [ # Screen 1
                        [ # Page 1
                            {
                                "component": "SaveLaps",
                                "actions": { 
                                    "Key_B":"saveBest",
                                    "Key_M":"saveMedian",
                                    "Key_L":"saveLast",
                                    "Key_O":"saveOptimized",
                                    "Key_A":"saveAll",
                                }
                            },
                            {
                                "component": "RecordingController",
                                "actions": { 
                                    "Key_R":"toggleRecording",
                                }
                            },
                            { "component" : "LapHeader", "stretch" : 1},
                            { "list" :
                                [
                                    { "list" :
                                        [
                                            { "component" : "Speed", "stretch" : 2, "actions" : { "Key_Tab" : "cycleFocusReference", "Key_Up" : "brakeOffsetUp", "Key_Down" : "brakeOffsetDown", "Key_0" : "resetBrakeOffset", }},
                                            { "component" : "TyreTemps", "stretch" : 1},
                                        ], "stretch" : 1
                                    },
                                    { "component" : "FuelAndMessages", "stretch" : 1, "actions" : { "Key_Space" : "setCautionMarker", "Key_W" : "saveMessages" }},
                                ], "stretch" : 100
                            }
                        ],
                        # Pages 2..
                        { "title":"Keyboard shortcuts", "component" : "Help", "shortcut":"Key_Question", "stretch" : 1},
                    ],
                    [ # Screen 2
                        { "component" : "Map", "stretch" : 1},
                    ],
                    [ # Screen 2
                        { "component" : "Stats", "stretch" : 1, "actions" : { "Key_T" : "saveRuns", "Key_D" : "setRunDescription" }},
                    ]
                ]

#j = json.dumps(defaultLayout, indent = 4)
#with open("defaultLayout.json", "w") as jf:
    #jf.write(j)

bigLayout = [
    [
        [
            {
                "component": "SaveLaps",
                "actions": { 
                    "Key_B":"saveBest",
                    "Key_M":"saveMedian",
                    "Key_L":"saveLast",
                    "Key_O":"saveOptimized",
                    "Key_A":"saveAll",
                }
            },
            {
                "component": "RecordingController",
                "actions": { 
                    "Key_R":"toggleRecording",
                }
            },
            {
                "component": "LapHeader",
                "stretch": 1
            },
            {
                "list": [
                    {
                        "list": [
                            { "component" : "Speed", "stretch" : 2, "actions" : { "Key_Tab" : "cycleFocusReference", "Key_Up" : "brakeOffsetUp", "Key_Down" : "brakeOffsetDown", "Key_0" : "resetBrakeOffset", }},
                            {
                                "list": [
                                    {
                                        "component": "Map",
                                        "stretch": 1
                                    },
                                    {
                                        "component": "TyreTemps",
                                        "stretch": 1
                                    }
                                ],
                                "stretch": 1
                            }
                        ],
                        "stretch": 1
                    },
                    {
                        "list": [
                            {
                                "component": "Pedals",
                                "stretch": 1
                            },
                            { "component" : "FuelAndMessages", "stretch" : 4, "actions" : { "Key_Space" : "setCautionMarker", "Key_W" : "saveMessages" }},
                        ],
                        "stretch": 1
                    }
                ],
                "stretch": 100
            }
        ],
        { "component" : "Stats", "stretch" : 1, "shortcut":"Key_S", "actions" : { "Key_T" : "saveRuns", "Key_D" : "setRunDescription" }},
        {
            "component": "Help",
            "shortcut":"Key_Question", 
            "stretch": 1
        },
        {
            "component": "Map",
            "shortcut":"Key_V", 
            "stretch": 1
        },
    ]
]

circuitExperienceLayout = [
                    [ # Screen 1
                        [ # Page 1
                            {
                                "component": "SaveLaps",
                                "actions": { 
                                    "Key_B":"saveBest",
                                    "Key_M":"saveMedian",
                                    "Key_L":"saveLast",
                                    "Key_O":"saveOptimized",
                                    "Key_A":"saveAll",
                                }
                            },
                            {
                                "component": "RecordingController",
                                "actions": { 
                                    "Key_R":"toggleRecording",
                                }
                            },
                            { "component" : "LapHeader", "stretch" : 1},
                            { "list" :
                                [
                                    { "list" :
                                        [
                                            { "component" : "Speed", "stretch" : 2, "actions" : { "Key_Tab" : "cycleFocusReference", "Key_Up" : "brakeOffsetUp", "Key_Down" : "brakeOffsetDown", "Key_0" : "resetBrakeOffset", }},
                                            { "component" : "TyreTemps", "stretch" : 1},
                                        ], "stretch" : 1
                                    },
                                    { "component" : "Map", "stretch" : 1},
                                ], "stretch" : 100
                            }
                        ],
                        # Pages 2..
                        { "component" : "Stats", "stretch" : 1, "shortcut":"Key_S", "actions" : { "Key_T" : "saveRuns", "Key_D" : "setRunDescription" }},
                        { "component" : "Help", "shortcut":"Key_Question", "stretch" : 1},
                    ],
                ]

brakeBoardLayout = [
                    [ # Screen 1
                        {
                            "component": "RecordingController",
                            "actions": { 
                                "Key_R":"toggleRecording",
                            }
                        },
                        { "component" : "BrakeBoard", "stretch" : 1, "actions" : { "Key_Tab" : "cycleModes", "Key_D" : "cycleDifficulty" }},
                        { "component" : "Help", "shortcut":"Key_Question", "stretch" : 1},
                    ],
                ]
