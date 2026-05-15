#include "LapsMenuScreen.h"
#include "LapMenuScreen.h"

LapsMenuScreen::LapsMenuScreen (MainWidget * parent, PDash dash, PState pstate) : MenuScreen(parent, dash, pstate)
{
    setTitle("LAPS");

    for (auto l : state()->comparisonLaps.keys())
    {
        if (state()->invisibleComparisonLaps.contains(l))
        {
            continue;
        }
        auto btn = addButton(l.toUpper(), this, &LapsMenuScreen::lapClicked);
        btn->setProperty("lapName", l);
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