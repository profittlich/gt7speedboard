#include "LapsMenuScreen.h"
#include "LapMenuScreen.h"

LapsMenuScreen::LapsMenuScreen (MainWidget * parent, PDash dash, PState pstate) : MenuScreen(parent, dash, pstate)
{
    setTitle("LAPS");

    auto compLaps = state()->comparisonLaps.keys();

    if (!compLaps.contains("ref-a"))
    {
        compLaps.append("ref-a");
    }
    if (!compLaps.contains("ref-b"))
    {
        compLaps.append("ref-b");
    }
    if (!compLaps.contains("ref-c"))
    {
        compLaps.append("ref-c");
    }

    compLaps.sort();

    for (auto l : compLaps)
    {
        if (state()->invisibleComparisonLaps.contains(l))
        {
            continue;
        }
        auto btn = addButton(l.toUpper(), this, &LapsMenuScreen::lapClicked);
        btn->setProperty("lapName", l);
    }

    if (state()->previousLaps.size() > 0)
    {
        auto btn = addButton("ALL LAPS", this, &LapsMenuScreen::lapClicked);
        btn->setProperty("lapName", "ALL LAPS");
    }

    layout()->insertStretch(layout()->count());
}

void LapsMenuScreen::lapClicked()
{
    auto lapName = sender()->property("lapName");
    DBG_MSG << lapName;

    MenuScreen * men = new LapMenuScreen (dynamic_cast<MainWidget*> (parent()), dash(), state(), lapName.toString());
    stackMenu(men);
}