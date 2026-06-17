#include "LapMenuScreen.h"

#include <QFileDialog>

LapMenuScreen::LapMenuScreen (MainWidget * parent, PDash dash, PState pstate, QString lap) : MenuScreen(parent, dash, pstate), m_lap(lap)
{
    setTitle(lap.toUpper());

    QPushButton * btn;

    if (lap == "ALL LAPS")
    {
        btn = addButton("EXPORT", this, &LapMenuScreen::exportAllClicked);
    }
    else if (state()->comparisonLaps.contains(lap))
    {
        addButton("CLEAR", this, &LapMenuScreen::clearClicked);

        if (lap != "ref-a")
        {
            btn = addButton("SAVE AS REF-A", this, &LapMenuScreen::saveAsRefClicked);
            btn->setProperty("target", "ref-a");
        }

        if (lap != "ref-b")
        {
            btn = addButton("SAVE AS REF-B", this, &LapMenuScreen::saveAsRefClicked);
            btn->setProperty("target", "ref-b");
        }

        if (lap != "ref-c")
        {
            btn = addButton("SAVE AS REF-C", this, &LapMenuScreen::saveAsRefClicked);
            btn->setProperty("target", "ref-c");
        }

        addButton("IMPORT", this, &LapMenuScreen::importClicked);
        addButton("EXPORT", this, &LapMenuScreen::exportClicked);
    }
    else
    {
        addButton("IMPORT", this, &LapMenuScreen::importClicked);
    }

    layout()->insertStretch(layout()->count());
}

void LapMenuScreen::saveAsRefClicked()
{
    DBG_MSG << "save as";
    QString target = sender()->property("target").toString();
    state()->saveComparisonLap(m_lap, target);
    state()->loadComparisonLap(target, target);
    //QFileDialog::getOpenFileName();
    deleteLater();
}

void LapMenuScreen::clearClicked()
{
    DBG_MSG << "clear";
    state()->deleteComparisonLap(m_lap, m_lap);
    deleteLater();

}

void LapMenuScreen::importClicked()
{
    DBG_MSG << "import";
    auto filePath = QFileDialog::getOpenFileName(this, "Load lap", QString(), "Lap (*.gt7lap; *.gt7track)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Load" << filePath << "as" << m_lap;
        state()->loadComparisonLap(m_lap, filePath, true);
        state()->saveComparisonLap(m_lap, m_lap);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();

}

void LapMenuScreen::exportClicked()
{
    DBG_MSG << "export";
    auto filePath = QFileDialog::getSaveFileName(this, "Save lap", QDate::currentDate().toString("yyyy-MM-dd") + " Reference Lap.gt7lap", "Lap (*.gt7lap)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save" << filePath << "from" << m_lap;
        state()->saveComparisonLap(m_lap, filePath, true);
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}

void LapMenuScreen::exportAllClicked()
{
    DBG_MSG << "export all";
    auto filePath = QFileDialog::getSaveFileName(this, "Save all laps", QDate::currentDate().toString("yyyy-MM-dd") + " All Laps.gt7laps", "Laps (*.gt7laps)");
    if(!filePath.isNull())
    {
        DBG_MSG << "Save" << filePath << "from" << m_lap;
        QFile f(filePath);
        f.open(QFile::WriteOnly);
        if (f.isOpen())
        {
            if (!state()->previousLaps.front()->preceedingPoint().isNull())
            {
                DBG_MSG << "write preceeding";
                f.write(state()->previousLaps.front()->preceedingPoint()->getData());
            }

            bool consecutive = true;
            PLap prev;
            for (auto l : state()->previousLaps)
            {
                DBG_MSG << "LAP" << l->points()[0]->currentLap();
                DBG_MSG << "has preceeding:" << !l->preceedingPoint().isNull();
                DBG_MSG << "has succeeding:" << !l->succeedingPoint().isNull();
                DBG_MSG << "check consecutivity";
                if (!prev.isNull())
                {
                    consecutive = l->points()[0]->currentLap() == (prev->points()[0]->currentLap() + 1);
                    DBG_MSG << consecutive << l->points()[0]->currentLap() << prev->points()[0]->currentLap();
                }

                if (!consecutive && !prev.isNull() && !prev->succeedingPoint().isNull())
                {
                    DBG_MSG << "write succeeding";
                    f.write(prev->succeedingPoint()->getData());
                }

                if (!consecutive && !l->preceedingPoint().isNull())
                {
                    DBG_MSG << "write preceeding";
                    f.write(l->preceedingPoint()->getData());
                }

                DBG_MSG << "write points" << l->points()[0]->currentLap();
                for (auto i : l->points())
                {
                    f.write(i->getData());
                }

                prev = l;
            }
            if (!prev.isNull())
            {
                DBG_MSG << "write succeeding";
                f.write(prev->succeedingPoint()->getData());
            }
                            f.close();
        }
    }
    else
    {
        DBG_MSG << "No file selected";
    }
    deleteLater();
}