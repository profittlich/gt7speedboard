#include "sb/widgets/ButtonLabel.h"

#include <QFileDialog>

const unsigned g_margin = 10;
const unsigned g_spacing = 17;

ButtonLabel::ButtonLabel(QWidget * parent) : QLabel(parent)
{
    setMinimumSize(10, 0);
}

void ButtonLabel::mousePressEvent(QMouseEvent * ev)
{
    qInfo("Label clicked");
    emit labelClicked();
}

